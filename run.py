"""
应用启动入口
============
提供命令行直接运行 Flask 开发服务器的能力。
"""

from __future__ import annotations

import os

from app import create_app


def _detect_config_name() -> str:
    """
    根据 FLASK_ENV / APP_ENV 环境变量自动选择配置名称。
    """

    return os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development"


app = create_app(_detect_config_name())


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )