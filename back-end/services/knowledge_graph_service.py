"""知识图谱服务 — LLM 驱动的知识点提取与关系分析"""
import json
import logging
from typing import List

from extensions import db
from models import Course, Courseware, DocumentChunk, KnowledgePoint, KnowledgePointRelation, KpCourseware
from utils.llm_client import llm_client

logger = logging.getLogger(__name__)

# ── LLM Prompts ──────────────────────────────────────────────

_EXTRACT_SYSTEM = (
    '你是一个教育领域的知识图谱构建专家。你的任务是从课件文本中提取结构化的知识点。\n\n'
    '要求：\n'
    '1. 提取有意义的核心概念、术语、理论、算法、方法等作为知识点\n'
    '2. 每个知识点给出：名称(name)、简要描述(description)、层级(level: 1=章级大概念, 2=节级, 3=小节级)、'
    '重要程度(importance: 1-5)、难度(difficulty: 1-5)、关键词(keywords: 逗号分隔的3-5个词)\n'
    '3. 只提取有实际教学意义的知识点，不要提取日常用语\n'
    '4. 知识点数量控制在 5-15 个，确保质量而非数量\n\n'
    '严格返回 JSON 数组，格式：\n'
    '[{"name": "知识点名", "description": "简要说明", "level": 1, "importance": 4, "difficulty": 3, "keywords": "关键词1,关键词2,关键词3"}, ...]\n'
    '不要包含任何其他内容。'
)

_EXTRACT_USER = (
    '请从以下课件内容中提取核心知识点。课件标题：{title}\n\n'
    '{chunks_text}\n\n'
    '请提取 {max_points} 个以内的核心知识点。'
)

_RELATIONS_SYSTEM = (
    '你是一个知识图谱关系分析专家。你的任务是分析给定知识点列表之间的语义关系。\n\n'
    '关系类型定义：\n'
    '- prerequisite: A 是学习 B 的预备知识（先修关系）\n'
    '- contains: A 包含 B（整体-部分关系）\n'
    '- related: A 与 B 强相关（同领域内紧密关联）\n'
    '- extends: A 是 B 的延伸/深入（扩展关系）\n'
    '- applies: A 可以应用于 B（应用关系）\n\n'
    '要求：\n'
    '1. 只输出有意义的关系，不要为每对知识点都生成关系\n'
    '2. 每个关系给出权重(weight: 0.0-1.0)和简要说明(description)\n'
    '3. 使用知识点名称(name)来指代源和目标\n\n'
    '严格返回 JSON 数组，格式：\n'
    '[{"source_name": "知识点A", "target_name": "知识点B", "relation_type": "prerequisite", "weight": 0.9, "description": "需要先理解A才能学B"}, ...]\n'
    '不要包含任何其他内容。'
)

_RELATIONS_USER = (
    '以下是课程中的知识点列表：\n\n'
    '{kp_list}\n\n'
    '请分析这些知识点之间的关系，提取 {max_relations} 个以内的最重要关系。'
)

# ── Config ───────────────────────────────────────────────────

MAX_KP_PER_COURSEWARE = 12
MAX_RELATIONS_PER_COURSE = 30
MAX_CHUNK_CHARS_FOR_EXTRACTION = 6000


# ── Public API ───────────────────────────────────────────────

def extract_from_courseware(courseware_id: int) -> List[KnowledgePoint]:
    """从单个课件中提取知识点并写入 DB

    Args:
        courseware_id: 课件 ID

    Returns:
        List[KnowledgePoint] — 新创建的知识点列表
    """
    cw = db.session.get(Courseware, courseware_id)
    if not cw:
        logger.warning(f'Courseware {courseware_id} not found')
        return []

    # 检查是否已提取过
    existing = KpCourseware.query.filter_by(courseware_id=courseware_id).count()
    if existing > 0:
        logger.info(f'Courseware {courseware_id} already has {existing} KP associations, skipping')
        return []

    if not llm_client.api_key:
        logger.warning('LLM_API_KEY not configured, cannot extract knowledge points')
        return []

    # 收集所有 chunk 内容
    chunks = DocumentChunk.query.filter_by(courseware_id=courseware_id)\
        .order_by(DocumentChunk.chunk_index).all()
    if not chunks:
        logger.warning(f'No chunks found for courseware {courseware_id}')
        return []

    # 构建上下文（限制总长度）
    chunk_texts = []
    total_chars = 0
    for ch in chunks:
        text = ch.content
        if total_chars + len(text) > MAX_CHUNK_CHARS_FOR_EXTRACTION:
            remaining = MAX_CHUNK_CHARS_FOR_EXTRACTION - total_chars
            if remaining > 200:
                chunk_texts.append(text[:remaining] + '\n...(内容已截断)')
            break
        chunk_texts.append(text)
        total_chars += len(text)

    chunks_text = '\n\n---\n\n'.join(chunk_texts)

    # 调用 LLM 提取知识点
    messages = [
        {'role': 'system', 'content': _EXTRACT_SYSTEM},
        {'role': 'user', 'content': _EXTRACT_USER.format(
            title=cw.title,
            chunks_text=chunks_text,
            max_points=MAX_KP_PER_COURSEWARE
        )},
    ]

    try:
        response = llm_client.chat(messages, temperature=0.2, max_tokens=2048, timeout=60)
        response = _clean_json_response(response)
        items = json.loads(response)
        if not isinstance(items, list):
            raise ValueError(f'LLM returned non-array: {type(items)}')
    except Exception as e:
        logger.error(f'Knowledge point extraction failed for courseware {courseware_id}: {e}')
        return []

    # 写入 DB
    created = []
    for item in items:
        if not isinstance(item, dict) or 'name' not in item:
            continue
        name = str(item.get('name', '')).strip()
        if len(name) < 2:
            continue

        # 检查是否已存在同名知识点（同一课程内）
        existing_kp = KnowledgePoint.query.filter_by(
            course_id=cw.course_id, name=name
        ).first()

        if existing_kp:
            kp = existing_kp
            # 更新描述（如果新提取的更详细）
            new_desc = str(item.get('description', '')).strip()
            if new_desc and len(new_desc) > len(kp.description or ''):
                kp.description = new_desc
        else:
            kp = KnowledgePoint(
                course_id=cw.course_id,
                name=name,
                description=str(item.get('description', '')).strip() or None,
                level=int(item.get('level', 1)),
                importance=int(item.get('importance', 3)),
                difficulty=int(item.get('difficulty', 3)),
                keywords=str(item.get('keywords', '')).strip() or None,
            )
            db.session.add(kp)
            db.session.flush()  # 获取 kp.id

        # 创建知识点-课件关联
        existing_assoc = KpCourseware.query.filter_by(
            knowledge_point_id=kp.id, courseware_id=courseware_id
        ).first()
        if not existing_assoc:
            assoc = KpCourseware(
                knowledge_point_id=kp.id,
                courseware_id=courseware_id,
                relevance_score=1.0,
            )
            db.session.add(assoc)

        created.append(kp)

    db.session.commit()
    logger.info(f'Extracted {len(created)} knowledge points from courseware {courseware_id}')
    return created


def analyze_relationships(course_id: int) -> List[KnowledgePointRelation]:
    """分析课程内所有知识点之间的关系并写入 DB

    Args:
        course_id: 课程 ID

    Returns:
        List[KnowledgePointRelation] — 新创建的关系列表
    """
    if not llm_client.api_key:
        logger.warning('LLM_API_KEY not configured, cannot analyze relationships')
        return []

    kps = KnowledgePoint.query.filter_by(course_id=course_id).all()
    if len(kps) < 2:
        logger.info(f'Course {course_id} has fewer than 2 KPs, skipping relationship analysis')
        return []

    # 构建知识点列表文本
    kp_lines = []
    for kp in kps:
        desc = kp.description or ''
        kp_lines.append(f'{kp.id}. {kp.name} — {desc[:80]}')
    kp_list_text = '\n'.join(kp_lines)

    # 构建 name→id 映射
    name_to_id = {kp.name: kp.id for kp in kps}

    # 调用 LLM 分析关系
    messages = [
        {'role': 'system', 'content': _RELATIONS_SYSTEM},
        {'role': 'user', 'content': _RELATIONS_USER.format(
            kp_list=kp_list_text,
            max_relations=MAX_RELATIONS_PER_COURSE
        )},
    ]

    try:
        response = llm_client.chat(messages, temperature=0.1, max_tokens=2048, timeout=60)
        response = _clean_json_response(response)
        items = json.loads(response)
        if not isinstance(items, list):
            raise ValueError(f'LLM returned non-array: {type(items)}')
    except Exception as e:
        logger.error(f'Relationship analysis failed for course {course_id}: {e}')
        return []

    # 清除旧关系（全量重建）
    KnowledgePointRelation.query.filter(
        KnowledgePointRelation.source_kp_id.in_([kp.id for kp in kps])
    ).delete(synchronize_session='fetch')

    # 写入新关系
    created = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        source_name = str(item.get('source_name', '')).strip()
        target_name = str(item.get('target_name', '')).strip()
        relation_type = str(item.get('relation_type', 'related')).strip()

        if relation_type not in ('prerequisite', 'contains', 'related', 'extends', 'applies'):
            relation_type = 'related'

        source_id = name_to_id.get(source_name)
        target_id = name_to_id.get(target_name)
        if not source_id or not target_id or source_id == target_id:
            continue

        # 去重
        pair_key = (source_id, target_id)
        if pair_key in seen:
            continue
        seen.add(pair_key)

        relation = KnowledgePointRelation(
            source_kp_id=source_id,
            target_kp_id=target_id,
            relation_type=relation_type,
            weight=float(item.get('weight', 0.8)),
            description=str(item.get('description', '')).strip() or None,
        )
        db.session.add(relation)
        created.append(relation)

    db.session.commit()
    logger.info(f'Analyzed {len(created)} relationships for course {course_id}')
    return created


def build_course_graph(course_id: int) -> dict:
    """编排完整的图谱构建流程

    Args:
        course_id: 课程 ID

    Returns:
        dict — {knowledge_points: int, relations: int}
    """
    # 为该课程所有未处理的课件提取知识点
    coursewares = Courseware.query.filter_by(course_id=course_id, status='completed').all()
    total_kps = 0
    for cw in coursewares:
        kps = extract_from_courseware(cw.id)
        total_kps += len(kps)

    # 分析关系
    relations = analyze_relationships(course_id)

    return {
        'knowledge_points': total_kps,
        'relations': len(relations),
    }


# ── Helpers ──────────────────────────────────────────────────

def _clean_json_response(response: str) -> str:
    """清理 LLM 返回的 JSON 字符串"""
    response = response.strip()
    # 去掉 markdown 代码块包裹
    if response.startswith('```'):
        lines = response.split('\n')
        json_lines = [l for l in lines if not l.startswith('```')]
        response = '\n'.join(json_lines).strip()
    return response
