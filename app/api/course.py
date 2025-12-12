"""
课程管理API
- 课程的增删改查
- 学生管理（添加/移除学生）
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.course_service import CourseService
from app.models.user import User

bp = Blueprint('course', __name__)


@bp.route('/courses', methods=['GET'])
@jwt_required(optional=True)
def get_courses():
    """获取课程列表"""
    try:
        user_id = get_jwt_identity()
        
        # 如果用户已登录，根据角色返回不同的课程列表
        if user_id:
            user = User.query.get(int(user_id))
            if user and user.role == 'student':
                # 学生：只返回已加入的课程
                enrolled_courses = user.enrolled_courses.all()
                courses = [c.to_dict() for c in enrolled_courses]
            else:
                # 教师和管理员：返回所有课程
                courses = [c.to_dict() for c in CourseService.get_all_courses()]
        else:
            # 未登录用户：返回所有课程
            courses = [c.to_dict() for c in CourseService.get_all_courses()]
        
        return jsonify({
            'courses': courses
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500


@bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    """创建课程（教师/管理员）"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        if user.role not in ['teacher', 'admin']:
            return jsonify({'error': '无权创建课程'}), 403
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'code']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        # 创建课程
        course = CourseService.create_course(
            name=data['name'],
            code=data['code'],
            teacher_id=user_id if user.role == 'teacher' else data.get('teacher_id', user_id),
            credit=float(data.get('credit', 0.0))
        )
        
        return jsonify({
            'message': '课程创建成功',
            'course': course.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required(optional=True)
def get_course_detail(course_id):
    """获取课程详情"""
    try:
        include_students = request.args.get('include_students', 'false').lower() == 'true'
        course = CourseService.get_course_by_id(course_id)
        return jsonify(course.to_dict(include_students=include_students)), 200
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500


@bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    """更新课程信息（教师）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        course = CourseService.update_course(
            course_id=course_id,
            teacher_id=user_id,
            name=data.get('name'),
            code=data.get('code'),
            credit=float(data['credit']) if 'credit' in data else None
        )
        
        return jsonify({
            'message': '课程更新成功',
            'course': course.to_dict()
        }), 200
    
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    """删除课程（教师）"""
    try:
        user_id = int(get_jwt_identity())
        
        CourseService.delete_course(course_id, user_id)
        
        return jsonify({'message': '课程删除成功'}), 200
    
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/courses/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    """获取课程的学生列表（教师）"""
    try:
        user_id = int(get_jwt_identity())
        
        students = CourseService.get_course_students(course_id, user_id)
        
        return jsonify({
            'students': [s.to_dict() for s in students]
        }), 200
    
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500


@bp.route('/courses/<int:course_id>/students', methods=['POST'])
@jwt_required()
def add_student_to_course(course_id):
    """添加学生到课程（教师）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'student_id' not in data:
            return jsonify({'error': '缺少student_id字段'}), 400
        
        course = CourseService.add_student_to_course(
            course_id=course_id,
            student_id=int(data['student_id']),
            teacher_id=user_id
        )
        
        return jsonify({
            'message': '学生添加成功',
            'course': course.to_dict(include_students=True)
        }), 200
    
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'添加失败: {str(e)}'}), 500


@bp.route('/courses/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def remove_student_from_course(course_id, student_id):
    """从课程中移除学生（教师）"""
    try:
        user_id = int(get_jwt_identity())
        
        course = CourseService.remove_student_from_course(
            course_id=course_id,
            student_id=student_id,
            teacher_id=user_id
        )
        
        return jsonify({
            'message': '学生移除成功',
            'course': course.to_dict(include_students=True)
        }), 200
    
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'移除失败: {str(e)}'}), 500


@bp.route('/students', methods=['GET'])
@jwt_required()
def get_all_students():
    """获取所有学生列表（用于添加到课程）"""
    try:
        students = CourseService.get_all_students()
        return jsonify({
            'students': [s.to_dict() for s in students]
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

