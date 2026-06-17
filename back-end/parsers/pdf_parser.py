"""PDF 课件解析器

使用 PyMuPDF (fitz) 逐页提取文本，返回带页码的列表。
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
                pages.append({
                    'page_number': page.number + 1,
                    'text': text,
                })
        doc.close()
        return pages
