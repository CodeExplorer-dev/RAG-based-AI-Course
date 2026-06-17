from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import StudentQuestion, Course
stats_bp = Blueprint('statistics', __name__)
@stats_bp.route('', methods=['GET'])
@jwt_required()
def get_stats():
    return jsonify({'code':200,'message':'success','data':{'total_questions':StudentQuestion.query.count(),'total_courses':Course.query.count(),'total_knowledge_points':0,'top_questions':[]}}),200
