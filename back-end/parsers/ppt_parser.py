"""PPT/PPTX 课件解析器

使用 python-pptx 逐页提取所有文本框中的文字，返回带 slide 编号的列表。
"""

from pptx import Presentation


class PPTParser:
    """PPT 解析：遍历每一页 slide，提取所有形状内的文本"""

    def extract(self, file_path: str) -> list[dict]:
        prs = Presentation(file_path)
        slides = []
        for i, slide in enumerate(prs.slides, start=1):
            texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        t = paragraph.text.strip()
                        if t:
                            texts.append(t)
            if texts:
                slides.append({
                    'page_number': i,
                    'text': '\n'.join(texts),
                })
        return slides
