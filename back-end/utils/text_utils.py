"""文本工具 — 知识点提取（LLM 批量优先，jieba 分词 fallback）"""
import re
import json
import os
import logging

# 确保 .env 已加载（Flask 在 python app.py 模式下可能未自动加载）
from dotenv import load_dotenv
load_dotenv()

import jieba
import jieba.posseg as pseg

logger = logging.getLogger(__name__)

# ── 是否启用 LLM 知识点提取（可通过环境变量关闭，强制走 jieba） ──
_LLM_ENABLED = os.environ.get('KNOWLEDGE_EXTRACT_LLM', 'true').lower() not in ('false', '0', 'no')

# ── 加载自定义词典（jieba fallback 时使用，防止专业术语被切碎） ──
_dict_path = os.path.join(os.path.dirname(__file__), 'knowledge_dict.txt')
if os.path.exists(_dict_path):
    jieba.load_userdict(_dict_path)

# ── 停用词表 ──────────────────────────────────────────────
_STOP_WORDS = {
    # 虚词 / 代词
    '的', '了', '是', '在', '和', '与', '也', '都', '被', '把',
    '这', '那', '它', '他', '她', '们', '我', '你', '一个', '没有',
    '不', '为', '就', '有', '对', '上', '中', '下', '到', '去',
    '会', '可', '以', '能', '但', '而', '从', '或', '其', '将',
    '什么', '怎么', '如何', '为什么', '怎样', '哪个', '哪些',
    '这个', '那个', '这些', '那些', '一下', '一些', '什么用',
    # 高频无意义词
    '老师', '问题', '区别', '好像', '应该', '还是', '不太', '总是',
    '是不是', '能不能', '试试', '下子', '有点', '不会', '不知道',
    '想问', '问一下', '请问', '讲讲', '详细', '分别', '每个',
    '如果', '可以', '比如', '这样', '也是', '用',
    # 过于通用的词（作为知识点无意义）
    '场景', '本质', '代码', '条件', '方法', '分析方法', '概念',
    '关系', '过程', '思路', '原理', '角色', '关联', '功能',
    '实现', '应用', '使用', '背后', '理解',
    '设置', '做题', '搞不清楚', '区别', '什么区别',
    '时候', '时候用',
}

# ── jieba 词性过滤：只保留实义词性 ───────────────────────
_ALLOWED_POS = {'n', 'nz', 'vn', 'eng', 'l', 'j'}

# ── LLM Prompts ──────────────────────────────────────────

_BATCH_EXTRACT_SYSTEM_PROMPT = (
    '你是一个教育领域的知识点提取专家。你的任务是分析一组学生提问，'
    '从中识别核心知识点（专业术语、算法名称、数据结构、理论概念、技术方法等），'
    '并统计每个知识点在多少条提问中出现过（同一条提问中多次提及只计 1 次）。'
    '只提取有实际意义的专业知识点，不要提取日常用语、问候语、语气词、普通动词。'
    '返回 JSON 数组，按出现次数降序排列。'
)

_BATCH_EXTRACT_USER_PROMPT = (
    '以下是 {count} 条学生提问。请从所有提问中提取核心知识点，'
    '统计每个知识点出现在多少条不同的提问中，按出现次数降序返回前 {top_n} 个。\n\n'
    '{questions}\n\n'
    '严格返回 JSON 数组，格式：[{{"name": "知识点名", "count": 次数}}, ...]\n'
    '不要包含任何其他内容。'
)


def _extract_knowledge_points_batch_llm(question_texts, top_n=20):
    """一次 LLM 调用批量提取所有提问的知识点并聚合计数"""
    from utils.llm_client import llm_client

    if not llm_client.api_key:
        raise RuntimeError('LLM_API_KEY 未配置')

    # 构建带编号的提问列表
    numbered = '\n'.join(
        f'{i+1}. {text}' for i, text in enumerate(question_texts)
    )

    user_prompt = _BATCH_EXTRACT_USER_PROMPT.format(
        count=len(question_texts),
        top_n=top_n,
        questions=numbered,
    )

    messages = [
        {'role': 'system', 'content': _BATCH_EXTRACT_SYSTEM_PROMPT},
        {'role': 'user', 'content': user_prompt},
    ]

    response = llm_client.chat(messages, temperature=0.1, max_tokens=1024, timeout=30)
    response = response.strip()

    # 去掉可能的 markdown 代码块包裹
    if response.startswith('```'):
        lines = response.split('\n')
        json_lines = [l for l in lines if not l.startswith('```')]
        response = '\n'.join(json_lines).strip()

    try:
        items = json.loads(response)
        if isinstance(items, list):
            result = []
            for item in items:
                if isinstance(item, dict) and 'name' in item and 'count' in item:
                    name = str(item['name']).strip()
                    count = int(item['count'])
                    if len(name) >= 2 and count > 0:
                        result.append({'name': name, 'count': count})
            return result[:top_n]
        else:
            raise ValueError(f'LLM 返回非数组: {type(items)}')
    except json.JSONDecodeError:
        logger.warning(f'LLM 返回非 JSON 格式: {response[:200]}')
        raise


def _extract_knowledge_points_jieba(question_texts, top_n=20):
    """jieba 逐条分词 + 聚合计数（LLM 不可用时的 fallback）"""
    counter = {}
    for text in question_texts:
        if not text:
            continue

        words = pseg.cut(text.strip())
        seen = set()  # 同一提问中重复知识点只计 1 次
        for w, flag in words:
            w = w.strip()
            if len(w) < 2 or len(w) > 20:
                continue
            if w in _STOP_WORDS:
                continue
            if w.isdigit():
                continue
            if re.fullmatch(r'[\s，。；：、？!！\-=+\[\]【】《》（）()\.,:;?!\'\"' '‘’“”…—]+', w):
                continue
            if flag not in _ALLOWED_POS:
                continue
            seen.add(w)

        for kw in seen:
            counter[kw] = counter.get(kw, 0) + 1

    sorted_items = sorted(counter.items(), key=lambda x: (-x[1], -len(x[0])))
    return [{'name': k, 'count': v} for k, v in sorted_items[:top_n]]


# ── 公共接口 ──────────────────────────────────────────────

def extract_keywords(text, max_count=8):
    """提取关键词（jieba 分词，用于单条文本的快速提取）

    Args:
        text: 待提取文本
        max_count: 最多返回关键词数量

    Returns:
        list[str] 关键词列表
    """
    if not text:
        return []

    words = pseg.cut(text.strip())
    freq = {}
    for w, flag in words:
        w = w.strip()
        if len(w) < 2 or len(w) > 20:
            continue
        if w in _STOP_WORDS:
            continue
        if w.isdigit():
            continue
        if re.fullmatch(r'[\s，。；：、？!！\-=+\[\]【】《》（）()\.,:;?!\'\"' '‘’“”…—]+', w):
            continue
        if flag not in _ALLOWED_POS:
            continue
        freq[w] = freq.get(w, 0) + 1

    sorted_kws = sorted(freq.items(), key=lambda x: (-x[1], -len(x[0])))
    return [kw for kw, _ in sorted_kws[:max_count]]


def extract_knowledge_points(question_texts, top_n=20):
    """从多个问题文本中提取知识点并聚合计数

    LLM 可用时：一次批量调用，秒级返回
    LLM 不可用时：jieba 分词 + 词频聚合

    Args:
        question_texts: list[str] — 每个问题拼接标题+内容后的文本
        top_n: 返回前 N 条知识点

    Returns:
        list[dict] — [{'name': str, 'count': int}, ...] 按 count 降序
    """
    global _LLM_ENABLED

    if not question_texts:
        return []

    # 每次请求重新读取环境变量，允许运行时热切换
    _LLM_ENABLED = os.environ.get('KNOWLEDGE_EXTRACT_LLM', 'true').lower() not in ('false', '0', 'no')

    if _LLM_ENABLED:
        try:
            return _extract_knowledge_points_batch_llm(question_texts, top_n)
        except Exception as e:
            logger.warning(f'LLM 批量知识点提取失败，fallback 到 jieba: {e}')

    return _extract_knowledge_points_jieba(question_texts, top_n)
