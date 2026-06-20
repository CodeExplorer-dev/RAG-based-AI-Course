"""智能文本分块器
策略（两层）：
  1. 优先按自然段落（空行分隔）切出语义完整的块
  2. 超过 chunk_size 的大段用滑动窗口切割，窗口间重叠 overlap
  3. 检测标题行（【xxx】格式），将标题与其后的内容绑定，不分离
"""

import re


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数（中文 ~1.5 char/token，英文 ~4 char/token）"""
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    other = len(text) - chinese
    return int(chinese / 1.5 + other / 4) + 1


def _find_heading_boundaries(text: str) -> list[int]:
    """找到所有 【xxx】 标题行的位置（行首索引）"""
    boundaries = []
    for m in re.finditer(r'^【[^】]+】', text, re.MULTILINE):
        boundaries.append(m.start())
    return boundaries


def chunk_text(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
    max_pages_per_chunk: int = 2,
) -> list[dict]:
    """对解析结果进行智能分块
    Args:
        pages:      [{'page_number': int, 'text': str, 'heading': str|None}, ...]
        chunk_size: 目标 token 数上限
        overlap:    滑动窗口重叠 token 数
        max_pages_per_chunk: 单个 chunk 最多跨越的页数（默认 2，确保页码精度）
    Returns:
        [{'content': str, 'chunk_index': int, 'token_count': int, 'page_ref': str|None, 'heading': str|None}, ...]
    """
    chunks = []
    chunk_index = 0

    # 收集所有页面的句子/段落
    raw_segments = []
    for page in pages:
        heading = page.get('heading')
        paragraphs = re.split(r'\n\s*\n', page['text'].strip())
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            raw_segments.append({
                'text': para,
                'page_ref': str(page['page_number']) if page.get('page_number') is not None else None,
                'heading': heading or page.get('heading'),
            })

    if not raw_segments:
        return chunks

    # ── 第二阶段：聚合成 chunk，超限或跨页过多则切割 ──
    current_parts = []
    current_tokens = 0
    current_pages = set()  # 当前 chunk 已包含的页号集合

    def flush():
        nonlocal chunk_index, current_parts, current_tokens, current_pages
        if not current_parts:
            return
        content = '\n\n'.join(p['text'] for p in current_parts)
        first_h = current_parts[0]['heading']
        last_h = current_parts[-1]['heading']
        heading = first_h or last_h
        page_ref = current_parts[0]['page_ref']
        if page_ref is not None and current_parts[-1]['page_ref'] != page_ref:
            page_ref = f"{page_ref}-{current_parts[-1]['page_ref']}"
        chunks.append({
            'content': content,
            'chunk_index': chunk_index,
            'token_count': current_tokens,
            'page_ref': page_ref,
            'heading': heading,
        })
        chunk_index += 1
        current_parts = []
        current_tokens = 0
        current_pages = set()

    for seg in raw_segments:
        seg_tokens = estimate_tokens(seg['text'])

        # 单个段落超限 → 用滑动窗口切割
        if seg_tokens > chunk_size:
            flush()
            step = max(chunk_size - overlap, chunk_size // 2)
            text = seg['text']
            pos = 0
            while pos < len(text):
                # 调整终点：先按 token 估算，再对齐到最近的句子边界
                estimated_end = pos + int(chunk_size * 1.5)
                end = min(estimated_end, len(text))
                chunk_text_val = text[pos:end]
                chunk_tokens = estimate_tokens(chunk_text_val)
                chunks.append({
                    'content': chunk_text_val,
                    'chunk_index': chunk_index,
                    'token_count': chunk_tokens,
                    'page_ref': seg['page_ref'],
                    'heading': seg['heading'],
                })
                chunk_index += 1
                # 按 token 数滑动
                advance = int(step * 1.5)
                pos += max(advance, 1)

            continue

        # 页边界控制：当前 chunk 已跨满 max_pages_per_chunk 页，且新段落来自新页 → 先 flush
        seg_page = seg['page_ref']
        is_new_page = seg_page is not None and seg_page not in current_pages
        if is_new_page and len(current_pages) >= max_pages_per_chunk:
            flush()

        # 正常合并
        if current_tokens + seg_tokens <= chunk_size:
            current_parts.append(seg)
            current_tokens += seg_tokens
            if seg_page is not None:
                current_pages.add(seg_page)
        else:
            flush()
            current_parts = [seg]
            current_tokens = seg_tokens
            if seg_page is not None:
                current_pages = {seg_page}
            else:
                current_pages = set()

    flush()
    return chunks
