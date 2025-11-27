"""
Flask 应用工厂
==============
负责创建 Flask 实例、加载配置并初始化常用扩展（SQLAlchemy、Migrate等）。
"""

from __future__ import annotations

from typing import Optional, Type

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import BaseConfig, CONFIG_MAP

# 全局扩展实例，供模型层通过 `from app import db` 直接引用。
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    根据传入的配置名称生成应用实例。若未提供配置名称，则使用 BaseConfig。
    """

    config_class: Type[BaseConfig] = CONFIG_MAP.get(config_name or "", BaseConfig)

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/health")
    def health_check():
        """
        健康检查接口，方便在部署到服务器时通过探针确认应用与数据库是否存活。
        """

        return {"status": "ok"}, 200

    return app