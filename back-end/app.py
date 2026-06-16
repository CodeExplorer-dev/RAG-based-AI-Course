# -*- coding: utf-8 -*-
import os, tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
CORS(app)
dbd = os.path.join('D:/RAG/RAG-based-AI-Course/', 'rag_course.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbd.replace(chr(92), '/')
app.config['JWT_SECRET_KEY'] = 'course-rag-secret-2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class StudentQuestion(db.Model):
    __tablename__ = 'student_questions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_name = db.Column(db.String(80), nullable=False)
    course_id = db.Column(db.Integer)
    course_name = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        for u in [
            ('admin','admin123','admin'),
            ('teacher1','teacher123','teacher'),
            ('student1','student123','student'),
        ]:
            db.session.add(User(username=u[0], password=generate_password_hash(u[1]), role=u[2]))
        db.session.commit()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data: return jsonify({'m':'err'}),400
    if not data.get('username') or not data.get('password'): return jsonify({'m':'missing'}),400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'m':'exists'}),409
    u = User(username=data['username'], password=generate_password_hash(data['password']), role=data.get('role','student'))
    db.session.add(u); db.session.commit()
    return jsonify({'m':'ok'}),201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'m':'missing'}),400
    u = User.query.filter_by(username=data['username']).first()
    if not u or not check_password_hash(u.password, data['password']):
        return jsonify({'m':'bad'}),401
    token = create_access_token(identity=str(u.id))
    return jsonify({'token':token,'user':{'id':u.id,'username':u.username,'role':u.role}})

@app.route('/api/ask-teacher', methods=['POST'])
@jwt_required()
def ask_teacher():
    uid = int(get_jwt_identity())
    u = User.query.get(uid)
    if not u or u.role != 'student': return jsonify({'m':'forbidden'}),403
    d = request.get_json()
    q = StudentQuestion(student_id=uid, student_name=u.username, title=d.get('title',''), content=d.get('content',''))
    db.session.add(q); db.session.commit()
    return jsonify({'m':'ok','id':q.id}),201

@app.route('/api/ask-teacher', methods=['GET'])
@jwt_required()
def teacher_see_questions():
    qs = StudentQuestion.query.order_by(StudentQuestion.created_at.desc()).all()
    return jsonify({'questions':[{'id':q.id,'student_name':q.student_name,'title':q.title,'content':q.content,'status':q.status,'answer':q.answer,'created_at':str(q.created_at)} for q in qs]})

@app.route('/api/ask-teacher/mine', methods=['GET'])
@jwt_required()
def my_questions():
    uid = int(get_jwt_identity())
    qs = StudentQuestion.query.filter_by(student_id=uid).order_by(StudentQuestion.created_at.desc()).all()
    return jsonify({'questions':[{'id':q.id,'title':q.title,'content':q.content,'status':q.status,'answer':q.answer,'created_at':str(q.created_at)} for q in qs]})

@app.route('/api/ask-teacher/<int:qid>/reply', methods=['POST'])
@jwt_required()
def reply_question(qid):
    q = StudentQuestion.query.get(qid)
    if not q: return jsonify({'m':'nf'}),404
    d = request.get_json()
    q.answer = d.get('answer',''); q.status = 'answered'
    db.session.commit()
    return jsonify({'m':'ok'})

@app.route('/api/teacher/stats', methods=['GET'])
@jwt_required()
def teacher_stats():
    return jsonify({'courses':0,'courseware':0,'questions': StudentQuestion.query.count(),'knowledge_points':0})

@app.route('/api/teacher/statistics', methods=['GET'])
@jwt_required()
def teacher_statistics():
    return jsonify({'questions':[]})

@app.route('/api/teacher/courses', methods=['GET'])
@jwt_required()
def teacher_courses():
    return jsonify({'courses':[]})

@app.route('/api/teacher/courses', methods=['POST'])
@jwt_required()
def create_course():
    return jsonify({'m':'ok'})

@app.route('/api/teacher/courses/<int:cid>', methods=['DELETE'])
@jwt_required()
def del_teacher_course(cid):
    return jsonify({'m':'ok'})

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    return jsonify({'users':User.query.count(),'courses':0,'questions':0,'knowledge_points':0})

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_users():
    users = User.query.all()
    return jsonify({'users':[{'id':u.id,'username':u.username,'role':u.role,'created_at':str(u.created_at)} for u in users]})

@app.route('/api/admin/users/<int:uid>/role', methods=['PUT'])
@jwt_required()
def update_role(uid):
    u = User.query.get(uid)
    if not u: return jsonify({'m':'nf'}),404
    u.role = request.get_json().get('role'); db.session.commit()
    return jsonify({'m':'ok'})

@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
@jwt_required()
def del_user(uid):
    u = User.query.get(uid)
    if not u: return jsonify({'m':'nf'}),404
    db.session.delete(u); db.session.commit()
    return jsonify({'m':'ok'})

@app.route('/api/admin/courses', methods=['GET'])
@jwt_required()
def admin_courses():
    return jsonify({'courses':[]})

@app.route('/api/admin/courses/<int:cid>', methods=['DELETE'])
@jwt_required()
def admin_del_course(cid):
    return jsonify({'m':'ok'})

@app.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    return jsonify({'courses':[]})

@app.route('/api/courseware', methods=['GET'])
@jwt_required()
def get_courseware():
    return jsonify({'courseware':[]})

@app.route('/api/courses/join', methods=['POST'])
@jwt_required()
def join_course():
    return jsonify({'m':'ok'})

@app.route('/api/statistics', methods=['GET'])
@jwt_required()
def public_stats():
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

