"""文档处理服务 — 文件解析、文本提取、分块调度"""

import os
import re
import logging
from typing import List, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from extensions import db
from models import Courseware, DocumentChunk
from utils.errors import NotFoundError
from parsers.chunker import estimate_tokens, chunk_text
from parsers import CoursewareParser as StructuredParser
from services.rag_service import index_courseware

logger = logging.getLogger(__name__)


def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """改进分块：先模拟结构化解析（按 【xxx】 标题分节再分块）

    如果输入文本包含 【xxx】 标题标记，则按标题分节处理；
    否则按段落+句子边界切分，滑动窗口保持上下文连贯。
    """
    if not text or not text.strip():
        return []

    # 检测是否已有标题标记
    has_headings = bool(re.search(r'^【[^】]+】', text, re.MULTILINE))

    if has_headings:
        # 已有结构化标记 → 用 chunk_text 分块
        pages = [{'page_number': 1, 'text': text, 'heading': None}]
        structured_chunks = chunk_text(pages, chunk_size, overlap)
        return [c['content'] for c in structured_chunks]

    # 无标题标记 → 段落+句子级滑动窗口
    paragraphs = re.split(r'\n\s*\n', text.strip())
    chunks = []
    current = ''

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_tokens = estimate_tokens(para)
        current_tokens = estimate_tokens(current)

        if current_tokens + para_tokens <= chunk_size:
            current = (current + '\n' + para).strip()
        else:
            if current:
                chunks.append(current)
                # 滑动窗口：保留末尾部分作为上下文
                if len(current) > overlap * 2:
                    # 按字符保留最后 overlap*2 个字符的文本
                    overlap_chars = int(overlap * 1.5)
                    overlap_text = current[-overlap_chars:] if len(current) > overlap_chars else current
                    current = overlap_text + '\n' + para
                else:
                    current = para
            else:
                # 单段超限 → 句子级切分
                sentences = re.split(r'(?<=[。！？.!?])\s*', para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    sent_tokens = estimate_tokens(sent)
                    if estimate_tokens(current) + sent_tokens <= chunk_size:
                        current = (current + '\n' + sent).strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = sent

    if current:
        chunks.append(current)

    return chunks if chunks else [text.strip()]


ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt', 'md'}


class DocumentService:

    def save_upload(self, file: FileStorage, course_id: int, uploader_id: int, title: str = None) -> Courseware:
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f'不支持的文件格式: .{ext}')

        filename = self._safe_filename(file.filename)
        upload_dir = self._get_upload_dir(course_id)
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        courseware = Courseware(
            course_id=course_id,
            title=title or os.path.splitext(file.filename)[0],
            file_type=ext,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            uploader_id=uploader_id,
            status='uploading',
        )
        db.session.add(courseware)
        db.session.commit()
        return courseware

    def get_file_path(self, courseware_id: int) -> str:
        cw = db.session.get(Courseware, courseware_id)
        if not cw:
            raise NotFoundError('课件不存在')
        return cw.file_path

    def extract_text(self, file_path: str, file_type: str) -> Tuple[str, int]:
        if file_type in ('txt', 'md'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(), 1
        elif file_type == 'pdf':
            return self._extract_pdf(file_path)
        elif file_type in ('ppt', 'pptx'):
            return self._extract_pptx(file_path)
        elif file_type in ('doc', 'docx'):
            return self._extract_docx(file_path)
        else:
            raise ValueError(f'不支持的文件类型: {file_type}')

    def process_document(self, courseware_id: int,
                         chunk_size: int = 1000, chunk_overlap: int = 200):
        """处理课件：提取文本 → 分块 → 写入 MySQL document_chunks 表"""
        cw = db.session.get(Courseware, courseware_id)
        if not cw:
            raise NotFoundError('课件不存在')

        try:
            cw.status = 'processing'
            db.session.commit()

            full_text, page_count = self.extract_text(cw.file_path, cw.file_type)
            cw.page_count = page_count

            chunks = split_text(full_text, chunk_size, chunk_overlap)

            for idx, chunk_text_val in enumerate(chunks):
                chunk = DocumentChunk(
                    courseware_id=courseware_id,
                    chunk_index=idx,
                    content=chunk_text_val,
                    token_count=estimate_tokens(chunk_text_val),
                )
                db.session.add(chunk)

            cw.chunk_count = len(chunks)
            cw.status = 'completed'

            # 4. Generate embeddings
            try:
                idx_result = index_courseware(courseware_id)
                logger.info(f'courseware embeddings done: {idx_result}')
            except Exception as e:
                logger.warning(f'embedding failed (non-fatal): {e}')

            db.session.commit()


        except Exception as e:
            cw.status = 'failed'
            db.session.commit()
            logger.error(f'文档处理失败 courseware_id={courseware_id}: {e}')
            raise

    def _extract_pdf(self, file_path: str) -> Tuple[str, int]:
        """PDF 文本提取：使用 PyMuPDF 逐页提取，保留页码"""
        import fitz
        doc = fitz.open(file_path)
        pages = []
        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if text:
                pages.append(f'【第{i}页】\n{text}')
        doc.close()
        return '\n\n'.join(pages), len(pages)

    def _extract_pptx(self, file_path: str) -> Tuple[str, int]:
        """PPT 文本提取：使用 StructuredParser 获取标题+正文结构"""
        parser = StructuredParser(file_path)
        parsed = parser.extract()
        if not parsed:
            return '', 0
        texts = []
        for p in parsed:
            heading = p.get('heading', '')
            body = p['text']
            if heading and not body.startswith(f'【{heading}】'):
                texts.append(f'【{heading}】\n{p["text"]}')
            else:
                texts.append(p['text'])
        return '\n\n'.join(texts), len(parsed)

    def _safe_filename(self, filename: str) -> str:
        import re
        name = filename.strip().replace("..", "").replace("/", "_").replace(chr(92), "_")
        name = re.sub(r'[^一-鿿\w\-\. ]', '', name)
        return name or "unnamed"

    def _extract_docx(self, file_path: str) -> Tuple[str, int]:
        """DOCX 文本提取：优先 StructuredParser，失败则尝试 win32com fallback"""
        try:
            parser = StructuredParser(file_path)
            parsed = parser.extract()
            if parsed:
                texts = [p["text"] for p in parsed]
                return "\n\n".join(texts), len(parsed)
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"DOCX parser: {e}")

        # Fallback: old .doc via win32com
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(file_path)
            text = doc.Content.Text.strip()
            para_count = len(doc.Paragraphs)
            doc.Close()
            word.Quit()
            return text, para_count
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"win32com: {e}")

        try:
            with open(file_path, "rb") as f:
                raw = f.read()
            t = raw.decode("utf-8", errors="ignore")
            if t.strip(): return t.strip(), 1
            t = raw.decode("gbk", errors="ignore")
            if t.strip(): return t.strip(), 1
        except:
            pass
        return "", 0

    def _get_upload_dir(self, course_id: int) -> str:
        from flask import current_app
        base = current_app.config['UPLOAD_FOLDER']
        return os.path.join(base, f'course_{course_id}')


document_service = DocumentService()




