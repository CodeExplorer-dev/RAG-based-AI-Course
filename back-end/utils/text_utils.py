"""文本工具 — 知识点提取（LLM 批量提取）"""
import json
import logging

from utils.llm_client import llm_client

logger = logging.getLogger(__name__)

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


# ── 公共接口 ──────────────────────────────────────────────

def extract_knowledge_points(question_texts, top_n=20):
    """从多个问题文本中提取知识点并聚合计数

    所有问题一次批量发给 LLM，由 LLM 直接返回聚合后的知识点排行。

    Args:
        question_texts: list[str] — 每个问题拼接标题+内容后的文本
        top_n: 返回前 N 条知识点

    Returns:
        list[dict] — [{'name': str, 'count': int}, ...] 按 count 降序
    """
    if not question_texts:
        return []

    if not llm_client.api_key:
        logger.warning('LLM_API_KEY 未配置，无法提取知识点')
        return []

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
        if not isinstance(items, list):
            raise ValueError(f'LLM 返回非数组: {type(items)}')

        result = []
        for item in items:
            if isinstance(item, dict) and 'name' in item and 'count' in item:
                name = str(item['name']).strip()
                count = int(item['count'])
                if len(name) >= 2 and count > 0:
                    result.append({'name': name, 'count': count})
        return result[:top_n]

    except json.JSONDecodeError:
        logger.warning(f'LLM 返回非 JSON 格式: {response[:200]}')
        return []
