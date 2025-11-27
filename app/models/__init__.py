"""
数据模型模块
============
统一暴露 SQLAlchemy 实例，后续单个模型文件在被实现时可直接导入 db。
"""

from app import db

__all__ = ["db"]