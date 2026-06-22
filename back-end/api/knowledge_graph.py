"""知识图谱 API — 从 DB 读取知识点和关系，返回图谱数据"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Course, KnowledgePoint, KnowledgePointRelation, KpCourseware, Courseware
from services.knowledge_graph_service import build_course_graph

kg_bp = Blueprint('knowledge_graph', __name__)

# ── 关系类型 → 中文标签 ──────────────────────────────────────

RELATION_LABELS = {
    'prerequisite': '先修',
    'contains': '包含',
    'related': '相关',
    'extends': '延伸',
    'applies': '应用',
}


def _build_graph_data(course_id: int) -> dict:
    """从 DB 构建图谱数据 {nodes, edges}"""
    course = db.session.get(Course, course_id)
    if not course:
        return {'nodes': [], 'edges': []}

    nodes = []
    edges = []

    # 1. 课程根节点
    nodes.append({
        'id': f'course_{course.id}',
        'label': course.course_name,
        'type': 'course',
        'size': 30,
        'level': 0,
    })

    # 2. 知识点节点
    kps = KnowledgePoint.query.filter_by(course_id=course_id).order_by(KnowledgePoint.level, KnowledgePoint.id).all()
    kp_ids = set()
    for kp in kps:
        kp_ids.add(kp.id)
        node_size = 15 + kp.importance * 6  # importance 1-5 → size 21-45
        nodes.append({
            'id': f'kp_{kp.id}',
            'label': kp.name,
            'type': f'knowledge_point_l{kp.level}',
            'size': node_size,
            'level': kp.level,
            'importance': kp.importance,
            'difficulty': kp.difficulty,
            'description': kp.description,
            'keywords': kp.keywords.split(',') if kp.keywords else [],
            'kp_id': kp.id,
        })

    # 3. 课件节点
    coursewares = Courseware.query.filter_by(course_id=course_id).all()
    for cw in coursewares:
        nodes.append({
            'id': f'cw_{cw.id}',
            'label': cw.title,
            'type': 'courseware',
            'size': 22,
            'level': 0,
        })
        # 课程 → 课件边
        edges.append({
            'source': f'course_{course.id}',
            'target': f'cw_{cw.id}',
            'label': '包含',
            'type': 'contains',
        })

    # 4. 知识点 → 课件关联边
    kp_cw_assocs = KpCourseware.query.filter(
        KpCourseware.knowledge_point_id.in_(kp_ids)
    ).all()
    for assoc in kp_cw_assocs:
        edges.append({
            'source': f'kp_{assoc.knowledge_point_id}',
            'target': f'cw_{assoc.courseware_id}',
            'label': '来源',
            'type': 'source',
        })

    # 5. 知识点关系边
    relations = KnowledgePointRelation.query.filter(
        KnowledgePointRelation.source_kp_id.in_(kp_ids)
    ).all()
    for rel in relations:
        edges.append({
            'source': f'kp_{rel.source_kp_id}',
            'target': f'kp_{rel.target_kp_id}',
            'label': RELATION_LABELS.get(rel.relation_type, rel.relation_type),
            'type': rel.relation_type,
            'weight': rel.weight,
            'description': rel.description,
        })

    return {'nodes': nodes, 'edges': edges}


# ── 路由 ─────────────────────────────────────────────────────

@kg_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_graph(course_id):
    """获取课程知识图谱数据"""
    data = _build_graph_data(course_id)
    return jsonify({'code': 200, 'message': 'success', 'data': data}), 200


@kg_bp.route('/build/<int:course_id>', methods=['POST'])
@jwt_required()
def build_graph(course_id):
    """手动触发知识图谱构建（重建）"""
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在', 'data': None}), 404

    try:
        result = build_course_graph(course_id)
        return jsonify({
            'code': 200,
            'message': '知识图谱构建完成',
            'data': result,
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'知识图谱构建失败: {str(e)}',
            'data': None,
        }), 500
