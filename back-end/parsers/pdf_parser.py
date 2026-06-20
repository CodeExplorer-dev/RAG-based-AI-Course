"""PDF 课件解析器

使用 PyMuPDF (fitz) 逐页提取文本，返回带页码的列表。
页码优先使用 PDF 页面标签（与阅读器中显示的页码一致），
无标签时回退到物理页码。
"""

import fitz


class PDFParser:
    """PDF 解析：逐页提取文本"""

    def extract(self, file_path: str) -> list[dict]:
        doc = fitz.open(file_path)
        pages = []
        for page in doc:
            text = page.get_text().strip()
            if text:
                # 优先使用 PDF 页面标签（与课件上显示的页码一致）
                label = page.get_label()
                if label is not None:
                    try:
                        page_num = int(label)
                    except (ValueError, TypeError):
                        page_num = page.number + 1  # 标签非数字时回退
                else:
                    page_num = page.number + 1  # 无标签时用物理页码
                pages.append({
                    'page_number': page_num,
                    'text': text,
                })
        doc.close()
        return pages
