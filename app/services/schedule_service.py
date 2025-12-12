"""
课程安排服务层
"""
from datetime import time
from typing import List, Dict, Any, Optional
from app import db
from app.models.schedule import CourseSchedule
from app.models.user import Course


class ScheduleService:
    """课程安排服务类"""
    
    @staticmethod
    def create_schedule(course_id: int, week: int, day_of_week: int, start_time: str, end_time: str, location: Optional[str] = None) -> CourseSchedule:
        """
        创建课程安排
        
        Args:
            course_id: 课程ID
            week: 周次 (1-18)
            day_of_week: 星期几 (0-6, 0=周一)
            start_time: 开始时间 (格式: HH:MM)
            end_time: 结束时间 (格式: HH:MM)
            location: 教室/地点
        
        Returns:
            CourseSchedule: 课程安排对象
        """
        # 验证课程是否存在
        course = Course.query.get(course_id)
        if not course:
            raise ValueError('课程不存在')
        
        # 验证周次
        if not (1 <= week <= 18):
            raise ValueError('周次必须在1-18之间')
        
        # 验证星期几
        if not (0 <= day_of_week <= 6):
            raise ValueError('星期几必须在0-6之间（0=周一，6=周日）')
        
        # 解析时间
        try:
            start = time.fromisoformat(start_time)
            end = time.fromisoformat(end_time)
        except ValueError:
            raise ValueError('时间格式不正确，请使用 HH:MM 格式')
        
        # 验证时间逻辑
        if start >= end:
            raise ValueError('开始时间必须早于结束时间')
        
        # 检查是否有时间冲突（同一课程在同一周次、同一时间段）
        conflict = CourseSchedule.query.filter_by(
            course_id=course_id,
            week=week,
            day_of_week=day_of_week
        ).filter(
            db.or_(
                db.and_(CourseSchedule.start_time <= start, CourseSchedule.end_time > start),
                db.and_(CourseSchedule.start_time < end, CourseSchedule.end_time >= end),
                db.and_(CourseSchedule.start_time >= start, CourseSchedule.end_time <= end)
            )
        ).first()
        
        if conflict:
            raise ValueError(f'该时间段已有课程安排：{conflict.course.name} {conflict.start_time}-{conflict.end_time}')
        
        schedule = CourseSchedule(
            course_id=course_id,
            week=week,
            day_of_week=day_of_week,
            start_time=start,
            end_time=end,
            location=location
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return schedule
    
    @staticmethod
    def get_schedules_by_course(course_id: int, week: Optional[int] = None) -> List[CourseSchedule]:
        """
        获取指定课程的所有安排
        
        Args:
            course_id: 课程ID
            week: 可选，如果提供则只返回该周的安排
        """
        query = CourseSchedule.query.filter_by(course_id=course_id)
        if week is not None:
            query = query.filter_by(week=week)
        return query.order_by(
            CourseSchedule.week, CourseSchedule.day_of_week, CourseSchedule.start_time
        ).all()
    
    @staticmethod
    def get_all_schedules(teacher_id: Optional[int] = None, week: Optional[int] = None) -> List[CourseSchedule]:
        """
        获取所有课程安排
        
        Args:
            teacher_id: 可选，如果提供则只返回该教师的课程安排
            week: 可选，如果提供则只返回该周的安排
        """
        query = CourseSchedule.query.join(Course)
        if teacher_id:
            query = query.filter(Course.teacher_id == teacher_id)
        if week is not None:
            query = query.filter(CourseSchedule.week == week)
        return query.order_by(
            CourseSchedule.week, CourseSchedule.day_of_week, CourseSchedule.start_time
        ).all()
    
    @staticmethod
    def get_schedule_by_id(schedule_id: int) -> Optional[CourseSchedule]:
        """根据ID获取课程安排"""
        return CourseSchedule.query.get(schedule_id)
    
    @staticmethod
    def update_schedule(schedule_id: int, day_of_week: Optional[int] = None, 
                       start_time: Optional[str] = None, end_time: Optional[str] = None,
                       location: Optional[str] = None, week: Optional[int] = None) -> CourseSchedule:
        """
        更新课程安排
        
        Args:
            schedule_id: 安排ID
            day_of_week: 星期几
            start_time: 开始时间
            end_time: 结束时间
            location: 教室/地点
        
        Returns:
            CourseSchedule: 更新后的课程安排对象
        """
        schedule = CourseSchedule.query.get(schedule_id)
        if not schedule:
            raise ValueError('课程安排不存在')
        
        if week is not None:
            if not (1 <= week <= 18):
                raise ValueError('周次必须在1-18之间')
            schedule.week = week
        
        if day_of_week is not None:
            if not (0 <= day_of_week <= 6):
                raise ValueError('星期几必须在0-6之间')
            schedule.day_of_week = day_of_week
        
        if start_time is not None:
            try:
                schedule.start_time = time.fromisoformat(start_time)
            except ValueError:
                raise ValueError('开始时间格式不正确')
        
        if end_time is not None:
            try:
                schedule.end_time = time.fromisoformat(end_time)
            except ValueError:
                raise ValueError('结束时间格式不正确')
        
        if location is not None:
            schedule.location = location
        
        # 验证时间逻辑
        if schedule.start_time >= schedule.end_time:
            raise ValueError('开始时间必须早于结束时间')
        
        # 检查时间冲突（排除自己）
        conflict = CourseSchedule.query.filter(
            CourseSchedule.id != schedule_id,
            CourseSchedule.course_id == schedule.course_id,
            CourseSchedule.week == schedule.week,
            CourseSchedule.day_of_week == schedule.day_of_week
        ).filter(
            db.or_(
                db.and_(CourseSchedule.start_time <= schedule.start_time, CourseSchedule.end_time > schedule.start_time),
                db.and_(CourseSchedule.start_time < schedule.end_time, CourseSchedule.end_time >= schedule.end_time),
                db.and_(CourseSchedule.start_time >= schedule.start_time, CourseSchedule.end_time <= schedule.end_time)
            )
        ).first()
        
        if conflict:
            raise ValueError(f'该时间段已有课程安排：{conflict.course.name} {conflict.start_time}-{conflict.end_time}')
        
        db.session.commit()
        return schedule
    
    @staticmethod
    def delete_schedule(schedule_id: int) -> None:
        """删除课程安排"""
        schedule = CourseSchedule.query.get(schedule_id)
        if not schedule:
            raise ValueError('课程安排不存在')
        
        db.session.delete(schedule)
        db.session.commit()
    
    @staticmethod
    def get_weekly_schedule(teacher_id: Optional[int] = None, week: Optional[int] = None) -> Dict[int, List[Dict[str, Any]]]:
        """
        获取周课表（按星期分组）
        
        Args:
            teacher_id: 可选，如果提供则只返回该教师的课程安排
            week: 可选，如果提供则只返回该周的安排
        
        Returns:
            Dict: {0: [...], 1: [...], ...} 格式的周课表
        """
        schedules = ScheduleService.get_all_schedules(teacher_id, week)
        weekly = {i: [] for i in range(7)}
        
        for schedule in schedules:
            weekly[schedule.day_of_week].append(schedule.to_dict())
        
        # 按时间排序
        for day in weekly:
            weekly[day].sort(key=lambda x: x['start_time'])
        
        return weekly
    
    @staticmethod
    def get_schedules_for_student(student_id: int, week: Optional[int] = None) -> List[CourseSchedule]:
        """
        获取学生选课的所有课程安排
        
        Args:
            student_id: 学生ID
            week: 可选，如果提供则只返回该周的安排
        
        Returns:
            List[CourseSchedule]: 学生选课的课程安排列表
        """
        from app.models.user import User
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return []
        
        # 获取学生选课的所有课程ID
        enrolled_courses = student.enrolled_courses.all()
        course_ids = [course.id for course in enrolled_courses]
        
        if not course_ids:
            return []
        
        # 查询这些课程的所有安排
        query = CourseSchedule.query.filter(
            CourseSchedule.course_id.in_(course_ids)
        )
        if week is not None:
            query = query.filter(CourseSchedule.week == week)
        return query.order_by(
            CourseSchedule.week, CourseSchedule.day_of_week, CourseSchedule.start_time
        ).all()
    
    @staticmethod
    def get_weekly_schedule_for_student(student_id: int, week: int) -> Dict[int, List[Dict[str, Any]]]:
        """
        获取学生的周课表（按星期分组）
        
        Args:
            student_id: 学生ID
            week: 周次 (1-18)
        
        Returns:
            Dict: {0: [...], 1: [...], ...} 格式的周课表
        """
        schedules = ScheduleService.get_schedules_for_student(student_id, week)
        weekly = {i: [] for i in range(7)}
        
        for schedule in schedules:
            weekly[schedule.day_of_week].append(schedule.to_dict())
        
        # 按时间排序
        for day in weekly:
            weekly[day].sort(key=lambda x: x['start_time'])
        
        return weekly

