"""
应用配置文件
==================
该模块集中管理所有环境共享的配置项，并且默认输出一个基于 MySQL 的
SQLAlchemy 连接字符串。通过环境变量可以自定义数据库账号、密码等敏感
信息，从而在不同的部署环境中保持一致的配置体验。
"""

from __future__ import annotations

import os
from datetime import timedelta
from typing import Dict, Type
from urllib.parse import quote_plus

from dotenv import load_dotenv

# 立即加载 .env，方便在本地开发阶段直接覆盖默认配置。
load_dotenv()


def _build_mysql_uri() -> str:
    """
    返回一个 MySQL 连接字符串。优先读取 DATABASE_URL，其次拼接单独的
    数据库相关环境变量，保证无论用户提供哪种方式都能成功连接。
    """
    direct_url = os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url

    username = os.getenv("DB_USERNAME", "root")
    password = quote_plus(os.getenv("DB_PASSWORD", "root"))
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "dazuoye")
    params = os.getenv("DB_PARAMS", "charset=utf8mb4")

    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?{params}"


class BaseConfig:
    """
    通用配置：提供安全密钥、数据库和文件上传等基础配置，适用于所有环境。
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _build_mysql_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "280")),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
    }
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "0") == "1"

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "local-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "60"))
    )

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE", 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")


class DevelopmentConfig(BaseConfig):
    """开发环境配置，默认开启调试和回显 SQL。"""

    DEBUG = True
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "1") == "1"


class TestingConfig(BaseConfig):
    """测试环境配置，使用独立的测试数据库并关闭 JWT 过期检查。"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "mysql+pymysql://root:root@127.0.0.1:3306/dazuoye_test"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    """生产环境配置，保持最少的默认输出，所有敏感信息靠环境变量注入。"""

    DEBUG = False


CONFIG_MAP: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}