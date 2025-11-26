# 项目结构说明

## 目录树

```
dazuoye/
├── app/                          # 应用主目录
│   ├── __init__.py              # Flask应用初始化
│   ├── config.py                # 配置文件
│   │
│   ├── models/                  # 数据模型层
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型（认证与权限）
│   │   ├── material.py          # 资料模型（资料中心）
│   │   ├── attendance.py        # 考勤模型（课堂考勤）
│   │   ├── grade.py             # 成绩模型（成绩管理）
│   │   └── interaction.py       # 互动模型（课堂互动）
│   │
│   ├── api/                     # API路由层
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证API（注册/登录/权限）
│   │   ├── material.py          # 资料中心API（上传/下载/搜索）
│   │   ├── attendance.py        # 考勤API（创建任务/签到）
│   │   ├── grade.py             # 成绩管理API（录入/统计/图表）
│   │   └── interaction.py       # 互动API（投票/提问/弹幕）
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证服务
│   │   ├── material_service.py  # 资料服务
│   │   ├── attendance_service.py # 考勤服务
│   │   ├── grade_service.py     # 成绩服务
│   │   └── interaction_service.py # 互动服务
│   │
│   ├── utils/                   # 工具函数层
│   │   ├── __init__.py
│   │   ├── file_handler.py      # 文件处理工具
│   │   ├── search_engine.py     # 全文搜索引擎
│   │   ├── qrcode_generator.py  # 二维码生成工具
│   │   ├── excel_handler.py     # Excel处理工具
│   │   └── chart_generator.py   # 图表生成工具
│   │
│   ├── static/                  # 静态文件目录
│   │   ├── css/                 # CSS样式文件
│   │   ├── js/                  # JavaScript文件
│   │   └── uploads/             # 上传文件存储目录
│   │
│   └── templates/               # 模板文件目录
│       └── base.html            # 基础模板
│
├── migrations/                  # 数据库迁移文件（待生成）
├── tests/                       # 测试文件目录
│   └── __init__.py
│
├── .env                         # 环境变量配置（需手动创建）
├── .gitignore                   # Git忽略文件
├── requirements.txt             # Python依赖包列表
├── README.md                    # 项目说明文档
├── MODULES.md                   # 模块详细说明文档
├── PROJECT_STRUCTURE.md         # 项目结构说明（本文件）
└── run.py                       # 应用启动文件
```

## 模块对应关系

### 1. 用户认证与权限管理
- **模型**: `app/models/user.py`
- **API**: `app/api/auth.py`
- **服务**: `app/services/auth_service.py`
- **工具**: 使用Flask-Login、Flask-JWT-Extended

### 2. 资料中心
- **模型**: `app/models/material.py`
- **API**: `app/api/material.py`
- **服务**: `app/services/material_service.py`
- **工具**: 
  - `app/utils/file_handler.py` - 文件处理
  - `app/utils/search_engine.py` - 全文搜索

### 3. 课堂考勤
- **模型**: `app/models/attendance.py`
- **API**: `app/api/attendance.py`
- **服务**: `app/services/attendance_service.py`
- **工具**: `app/utils/qrcode_generator.py` - 二维码生成

### 4. 成绩管理
- **模型**: `app/models/grade.py`
- **API**: `app/api/grade.py`
- **服务**: `app/services/grade_service.py`
- **工具**: 
  - `app/utils/excel_handler.py` - Excel处理
  - `app/utils/chart_generator.py` - 图表生成

### 5. 课堂互动
- **模型**: `app/models/interaction.py`
- **API**: `app/api/interaction.py`
- **服务**: `app/services/interaction_service.py`
- **工具**: 使用Flask-SocketIO进行实时通信

## 文件说明

### 核心配置文件
- `app/config.py`: 应用配置类（数据库、JWT、文件上传等配置）
- `app/__init__.py`: Flask应用工厂函数，初始化扩展
- `.env`: 环境变量（数据库连接、密钥等，需手动创建）

### 数据模型文件
所有模型文件位于 `app/models/` 目录，使用SQLAlchemy ORM定义数据表结构。

### API路由文件
所有API路由文件位于 `app/api/` 目录，处理HTTP请求和响应。

### 服务层文件
所有业务逻辑文件位于 `app/services/` 目录，实现具体的业务功能。

### 工具函数文件
所有工具函数文件位于 `app/utils/` 目录，提供可复用的功能函数。

## 下一步开发步骤

1. **配置环境**
   - 创建 `.env` 文件
   - 配置数据库连接
   - 配置JWT密钥

2. **初始化数据库**
   - 在 `app/models/__init__.py` 中导入所有模型
   - 配置Flask-Migrate
   - 执行数据库迁移

3. **实现核心功能**
   - 按模块顺序实现功能
   - 先实现模型层
   - 再实现服务层
   - 最后实现API层

4. **测试验证**
   - 编写单元测试
   - 进行功能测试
   - 性能测试

## 注意事项

- 所有Python文件目前只包含注释说明，需要实现具体代码
- 数据库迁移文件需要运行 `flask db init` 后生成
- `.env` 文件需要手动创建，不要提交到Git
- 上传文件目录需要设置适当的权限
- 建议使用虚拟环境管理依赖

