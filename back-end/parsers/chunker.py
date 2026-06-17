"""智能文本分块器

策略（两层）：
  1. 优先按双换行符切出自然段落，保留语义完整性
  2. 超过 chunk_size 的大段用滑动窗口切割，窗口间重叠 overlap
"""

import re


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数（中文 ~1.5 char/token，英文 ~4 char/token）"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4) + 1


def chunk_text(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    """对解析结果进行智能分块

    Args:
        pages:      [{'page_number': int, 'text': str}, ...]
        chunk_size: 目标 token 数上限
        overlap:    滑动窗口重叠 token 数

    Returns:
        [{'content': str, 'chunk_index': int, 'token_count': int, 'page_ref': str|None}, ...]
    """
    chunks = []
    chunk_index = 0

    # ── 第一阶段：按自然段落（空行分开的块）预切片 ──
    raw_segments = []
    for page in pages:
        paragraphs = re.split(r'\n\s*\n', page['text'].strip())
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            raw_segments.append({
                'text': para,
                'page_ref': str(page['page_number']),
            })

    if not raw_segments:
        return chunks

    # ── 第二阶段：聚合成 chunk，超限则滑动窗口 ──
    current_parts = []
    current_tokens = 0

    def flush():
        nonlocal chunk_index, current_parts, current_tokens
        if not current_parts:
            return
        content = '\n\n'.join(p['text'] for p in current_parts)
        page_ref = current_parts[0]['page_ref']
        if current_parts[-1]['page_ref'] != page_ref:
            page_ref = f"{page_ref}-{current_parts[-1]['page_ref']}"
        chunks.append({
            'content': content,
            'chunk_index': chunk_index,
            'token_count': current_tokens,
            'page_ref': page_ref,
        })
        chunk_index += 1
        current_parts = []
        current_tokens = 0

    for seg in raw_segments:
        seg_tokens = estimate_tokens(seg['text'])

        # 单个段落就超限 → 滑动窗口切割
        if seg_tokens > chunk_size:
            flush()
            step = max(chunk_size - overlap, chunk_size // 2)
            start = 0
            while start < len(seg['text']):
                end = min(start + chunk_size * 2, len(seg['text']))
                piece = seg['text'][start:end]
                chunks.append({
                    'content': piece,
                    'chunk_index': chunk_index,
                    'token_count': estimate_tokens(piece),
                    'page_ref': seg['page_ref'],
                })
                chunk_index += 1
                start += step * 2
            continue

        if current_tokens + seg_tokens <= chunk_size:
            current_parts.append(seg)
            current_tokens += seg_tokens
        else:
            flush()
            current_parts = [seg]
            current_tokens = seg_tokens

    flush()
    return chunks
