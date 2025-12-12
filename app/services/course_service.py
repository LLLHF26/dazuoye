"""
课程管理服务层
- 课程的增删改查
- 学生管理（添加/移除学生）
"""
from app import db
from app.models.user import Course, User, course_students
from sqlalchemy import and_


class CourseService:
    """课程服务类"""
    
    @staticmethod
    def create_course(name, code, teacher_id, credit=0.0):
        """
        创建课程
        
        Args:
            name: 课程名称
            code: 课程代码
            teacher_id: 教师ID
            credit: 学分
        
        Returns:
            Course: 课程对象
        """
        # 检查课程代码是否已存在
        existing = Course.query.filter_by(code=code).first()
        if existing:
            raise ValueError(f'课程代码 {code} 已存在')
        
        # 验证教师是否存在
        teacher = User.query.get(teacher_id)
        if not teacher:
            raise ValueError('教师不存在')
        if teacher.role != 'teacher':
            raise ValueError('指定的用户不是教师')
        
        course = Course(
            name=name,
            code=code,
            teacher_id=teacher_id,
            credit=credit
        )
        
        db.session.add(course)
        db.session.commit()
        
        return course
    
    @staticmethod
    def get_all_courses():
        """获取所有课程"""
        return Course.query.all()
    
    @staticmethod
    def get_course_by_id(course_id):
        """根据ID获取课程"""
        return Course.query.get_or_404(course_id)
    
    @staticmethod
    def get_courses_by_teacher(teacher_id):
        """获取指定教师的课程"""
        return Course.query.filter_by(teacher_id=teacher_id).all()
    
    @staticmethod
    def update_course(course_id, teacher_id, name=None, code=None, credit=None):
        """
        更新课程信息
        
        Args:
            course_id: 课程ID
            teacher_id: 教师ID（用于权限验证）
            name: 课程名称
            code: 课程代码
            credit: 学分
        
        Returns:
            Course: 更新后的课程对象
        """
        course = Course.query.get_or_404(course_id)
        
        # 验证权限
        if course.teacher_id != teacher_id:
            raise PermissionError('无权修改此课程')
        
        if name is not None:
            course.name = name
        if code is not None:
            # 检查课程代码是否已被其他课程使用
            existing = Course.query.filter(Course.code == code, Course.id != course_id).first()
            if existing:
                raise ValueError(f'课程代码 {code} 已被使用')
            course.code = code
        if credit is not None:
            course.credit = credit
        
        db.session.commit()
        
        return course
    
    @staticmethod
    def delete_course(course_id, teacher_id):
        """
        删除课程
        
        Args:
            course_id: 课程ID
            teacher_id: 教师ID（用于权限验证）
        
        Returns:
            bool: 是否删除成功
        """
        course = Course.query.get_or_404(course_id)
        
        # 验证权限
        if course.teacher_id != teacher_id:
            raise PermissionError('无权删除此课程')
        
        db.session.delete(course)
        db.session.commit()
        
        return True
    
    @staticmethod
    def add_student_to_course(course_id, student_id, teacher_id):
        """
        添加学生到课程
        
        Args:
            course_id: 课程ID
            student_id: 学生ID
            teacher_id: 教师ID（用于权限验证）
        
        Returns:
            Course: 课程对象
        """
        course = Course.query.get_or_404(course_id)
        
        # 验证权限
        if course.teacher_id != teacher_id:
            raise PermissionError('无权管理此课程的学生')
        
        # 验证学生是否存在
        student = User.query.get(student_id)
        if not student:
            raise ValueError('学生不存在')
        if student.role != 'student':
            raise ValueError('指定的用户不是学生')
        
        # 检查学生是否已在课程中
        if student in course.students.all():
            raise ValueError('学生已在此课程中')
        
        course.students.append(student)
        db.session.commit()
        
        return course
    
    @staticmethod
    def remove_student_from_course(course_id, student_id, teacher_id):
        """
        从课程中移除学生
        
        Args:
            course_id: 课程ID
            student_id: 学生ID
            teacher_id: 教师ID（用于权限验证）
        
        Returns:
            Course: 课程对象
        """
        course = Course.query.get_or_404(course_id)
        
        # 验证权限
        if course.teacher_id != teacher_id:
            raise PermissionError('无权管理此课程的学生')
        
        # 验证学生是否存在
        student = User.query.get(student_id)
        if not student:
            raise ValueError('学生不存在')
        
        # 检查学生是否在课程中
        if student not in course.students.all():
            raise ValueError('学生不在此课程中')
        
        course.students.remove(student)
        db.session.commit()
        
        return course
    
    @staticmethod
    def get_course_students(course_id, teacher_id):
        """
        获取课程的学生列表
        
        Args:
            course_id: 课程ID
            teacher_id: 教师ID（用于权限验证）
        
        Returns:
            list: 学生列表
        """
        course = Course.query.get_or_404(course_id)
        
        # 验证权限
        if course.teacher_id != teacher_id:
            raise PermissionError('无权查看此课程的学生')
        
        return course.students.all()
    
    @staticmethod
    def get_all_students():
        """获取所有学生（用于添加到课程）"""
        return User.query.filter_by(role='student').all()

