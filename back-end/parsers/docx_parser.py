"""DOCX 课件解析器

使用 python-docx 提取所有段落文本，返回带段落编号的列表。
"""

from docx import Document


class DOCXParser:
    """DOCX 解析：遍历每一段落提取文本"""

    def extract(self, file_path: str) -> list[dict]:
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if paragraphs:
            return [{
                'page_number': 1,
                'text': '\n'.join(paragraphs),
            }]
        return []
