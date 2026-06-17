"""课件解析器统一入口

根据文件后缀自动选择对应的解析器，返回统一的 [{page, text}, ...] 格式。
"""

import os
from .pdf_parser import PDFParser
from .ppt_parser import PPTParser
from .docx_parser import DOCXParser


class CoursewareParser:
    """统一解析器，根据文件后缀分发到具体的解析器"""

    PARSER_MAP = {
        '.pdf': PDFParser,
        '.ppt': PPTParser,
        '.pptx': PPTParser,
        '.doc': DOCXParser,
        '.docx': DOCXParser,
    }

    def __init__(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        parser_cls = self.PARSER_MAP.get(ext)
        if not parser_cls:
            raise ValueError(f"不支持的文件格式: {ext}")
        self.parser = parser_cls()
        self.file_path = file_path

    def extract(self) -> list[dict]:
        """提取文本，返回 [{page_number: int, text: str}, ...]"""
        return self.parser.extract(self.file_path)


__all__ = ['CoursewareParser']
