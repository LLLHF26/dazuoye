"""
课程安排API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.schedule_service import ScheduleService

bp = Blueprint('schedule', __name__)


@bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    """获取课程安排列表"""
    try:
        user_id = int(get_jwt_identity())
        from app.models.user import User
        user = User.query.get(user_id)
        
        course_id = request.args.get('course_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        student_id = request.args.get('student_id', type=int)
        week = request.args.get('week', type=int)  # 周次 (1-18)
        weekly = request.args.get('weekly', 'false').lower() == 'true'
        
        # 如果是学生，且没有指定student_id，则使用当前用户ID
        if user and user.role == 'student' and not student_id:
            student_id = user_id
        
        if weekly:
            # 返回周课表格式
            if not week:
                # 如果没有指定周次，默认使用第1周
                week = 1
            if student_id:
                # 学生查看自己的课表
                data = ScheduleService.get_weekly_schedule_for_student(student_id, week)
            else:
                # 教师查看自己的课表
                data = ScheduleService.get_weekly_schedule(teacher_id, week)
            return jsonify({'weekly_schedule': data, 'week': week}), 200
        elif course_id:
            # 返回指定课程的安排
            schedules = ScheduleService.get_schedules_by_course(course_id, week)
            return jsonify({
                'schedules': [s.to_dict() for s in schedules]
            }), 200
        elif student_id:
            # 返回学生选课的所有课程安排
            schedules = ScheduleService.get_schedules_for_student(student_id, week)
            return jsonify({
                'schedules': [s.to_dict() for s in schedules]
            }), 200
        else:
            # 返回所有安排（教师或管理员）
            schedules = ScheduleService.get_all_schedules(teacher_id, week)
            return jsonify({
                'schedules': [s.to_dict() for s in schedules]
            }), 200
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"获取课程安排失败: {error_detail}")  # 打印详细错误信息到控制台
        return jsonify({'error': f'获取失败: {str(e)}', 'detail': error_detail}), 500


@bp.route('/schedules', methods=['POST'])
@jwt_required()
def create_schedule():
    """创建课程安排（仅教师）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        # 验证必填字段
        required_fields = ['course_id', 'day_of_week', 'start_time', 'end_time']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
        
        # 验证权限：只有教师可以创建课程安排
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': '只有教师可以创建课程安排'}), 403
        
        # 验证课程是否属于该教师
        from app.models.user import Course
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({'error': '课程不存在'}), 404
        
        if course.teacher_id != user_id and user.role != 'admin':
            return jsonify({'error': '只能为自己的课程创建安排'}), 403
        
        schedule = ScheduleService.create_schedule(
            course_id=data['course_id'],
            week=data['week'],
            day_of_week=data['day_of_week'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            location=data.get('location')
        )
        
        return jsonify({
            'schedule': schedule.to_dict(),
            'message': '创建成功'
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id: int):
    """更新课程安排（仅教师）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        # 验证权限
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': '只有教师可以更新课程安排'}), 403
        
        # 验证课程安排是否存在且属于该教师
        schedule = ScheduleService.get_schedule_by_id(schedule_id)
        if not schedule:
            return jsonify({'error': '课程安排不存在'}), 404
        
        if schedule.course.teacher_id != user_id and user.role != 'admin':
            return jsonify({'error': '只能修改自己课程的安排'}), 403
        
        schedule = ScheduleService.update_schedule(
            schedule_id=schedule_id,
            day_of_week=data.get('day_of_week'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            location=data.get('location'),
            week=data.get('week')
        )
        
        return jsonify({
            'schedule': schedule.to_dict(),
            'message': '更新成功'
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id: int):
    """删除课程安排（仅教师）"""
    try:
        user_id = int(get_jwt_identity())
        
        # 验证权限
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': '只有教师可以删除课程安排'}), 403
        
        # 验证课程安排是否存在且属于该教师
        schedule = ScheduleService.get_schedule_by_id(schedule_id)
        if not schedule:
            return jsonify({'error': '课程安排不存在'}), 404
        
        if schedule.course.teacher_id != user_id and user.role != 'admin':
            return jsonify({'error': '只能删除自己课程的安排'}), 403
        
        ScheduleService.delete_schedule(schedule_id)
        
        return jsonify({'message': '删除成功'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

