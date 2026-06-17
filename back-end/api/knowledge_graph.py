from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Course, Courseware, DocumentChunk
import re

kg_bp = Blueprint('knowledge_graph', __name__)

_STOP_WORDS = {'的', '了', '是', '在', '和', '与', '也', '都', '被', '把',
               '这', '那', '它', '他', '她', '们', '我', '你', '一个', '没有',
               '不', '为', '就', '有', '对', '上', '中', '下', '到', '去',
               '会', '可', '以', '能', '但', '而', '从', '或', '其', '将'}


def _extract_keywords(text, max_count=6):
    """简单提取关键词（词频统计 + 长度过滤）"""
    segments = re.split(r'[，。；：、？!！\n\r\s]+', text)
    freq = {}
    for seg in segments:
        seg = seg.strip()
        if len(seg) < 2 or len(seg) > 20 or seg in _STOP_WORDS:
            continue
        freq[seg] = freq.get(seg, 0) + 1
    sorted_kws = sorted(freq.items(), key=lambda x: -x[1])
    return [kw for kw, _ in sorted_kws[:max_count]]


@kg_bp.route('/detail/<int:course_id>', methods=['GET'])
@jwt_required()
def get_graph_detail(course_id):
    """增强版知识图谱：提取知识点及其关系"""
    c = db.session.get(Course, course_id)
    if not c:
        return jsonify({'code': 200, 'message': 'success', 'data': {'nodes': [], 'edges': []}}), 200

    cws = Courseware.query.filter_by(course_id=course_id).all()
    nodes = []
    edges = []

    # 课程根节点
    nodes.append({'id': f'course_{c.id}', 'label': c.course_name, 'type': 'course', 'size': 28})
    seen_labels = set()

    for cw in cws:
        cw_id = f'cw_{cw.id}'
        nodes.append({'id': cw_id, 'label': cw.title, 'type': 'courseware', 'size': 22})
        edges.append({'source': f'course_{c.id}', 'target': cw_id, 'label': '包含', 'type': 'contains'})

        # 提取该课件中的知识点片段
        chunks = DocumentChunk.query.filter_by(courseware_id=cw.id)\
            .order_by(DocumentChunk.chunk_index).all()
        all_text = ' '.join([ch.content for ch in chunks])
        keywords = _extract_keywords(all_text, max_count=6)

        kw_nodes = []
        for kw in keywords:
            if kw in seen_labels:
                continue
            seen_labels.add(kw)
            kw_id = f'kw_{cw.id}_{kw[:10]}'
            kw_nodes.append({'id': kw_id, 'label': kw, 'type': 'knowledge', 'size': 14})

        nodes.extend(kw_nodes)
        for kn in kw_nodes:
            edges.append({
                'source': cw_id,
                'target': kn['id'],
                'label': '知识点',
                'type': 'knowledge'
            })

        # 课件间顺序关系
        idx = cws.index(cw)
        if idx > 0:
            prev_id = f'cw_{cws[idx - 1].id}'
            edges.append({
                'source': prev_id,
                'target': cw_id,
                'label': '下一篇',
                'type': 'sequence'
            })

    return jsonify({'code': 200, 'message': 'success', 'data': {'nodes': nodes, 'edges': edges}}), 200


@kg_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_graph(course_id):
    """基础版知识图谱"""
    c = db.session.get(Course, course_id)
    if not c:
        return jsonify({'code': 200, 'message': 'success', 'data': {'nodes': [], 'edges': []}}), 200
    cws = Courseware.query.filter_by(course_id=course_id).all()
    nodes = [{'id': 'course', 'label': c.course_name, 'type': 'course', 'size': 28}]
    edges = []
    for cw in cws:
        nid = 'cw_' + str(cw.id)
        nodes.append({'id': nid, 'label': cw.title, 'type': 'courseware', 'size': 22})
        edges.append({'source': 'course', 'target': nid, 'label': '包含'})
    return jsonify({'code': 200, 'message': 'success', 'data': {'nodes': nodes, 'edges': edges}}), 200
