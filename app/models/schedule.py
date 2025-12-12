"""
课程安排数据模型
"""
from datetime import datetime
from app import db


class CourseSchedule(db.Model):
    """课程安排表"""
    __tablename__ = 'course_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    week = db.Column(db.Integer, nullable=False, index=True)  # 周次 (1-18)
    day_of_week = db.Column(db.Integer, nullable=False, index=True)  # 0-6, 0=周一, 6=周日
    start_time = db.Column(db.Time, nullable=False)  # 开始时间，如 08:00
    end_time = db.Column(db.Time, nullable=False)  # 结束时间，如 09:40
    location = db.Column(db.String(100), nullable=True)  # 教室/地点
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    course = db.relationship('Course', backref='schedules', lazy='joined')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'course_code': self.course.code if self.course else None,
            'week': self.week,
            'day_of_week': self.day_of_week,
            'day_name': self.get_day_name(),
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_day_name(self):
        """获取星期名称"""
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return days[self.day_of_week] if 0 <= self.day_of_week < 7 else '未知'
    
    def __repr__(self):
        return f'<CourseSchedule {self.course.name if self.course else "Unknown"} {self.get_day_name()} {self.start_time}-{self.end_time}>'

