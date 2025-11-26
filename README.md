# 教学管理系统

## 项目简介

本项目是一个功能完整的教学管理系统，支持多角色用户管理、资料中心、课堂考勤、成绩管理和课堂互动等功能。

## 功能模块

### 1. 用户认证与权限管理模块

**功能描述：**
- 多角色登录（管理员、教师、学生）
- 用户注册功能
- 基于角色的权限控制（RBAC）
- JWT Token认证机制
- 密码加密存储

**技术要点：**
- Flask-Login：用户会话管理
- Flask-JWT-Extended：JWT Token生成与验证
- bcrypt：密码加密
- SQLAlchemy：用户数据模型

### 2. 资料中心模块

**功能描述：**
- 文件上传/下载功能
- 在线预览（支持PDF、Word、图片等格式）
- 按课程分类管理
- 标签分类系统
- 全文搜索功能

**技术要点：**
- Flask-Uploads：文件上传处理
- Whoosh：全文搜索引擎
- PyPDF2/python-docx：文档解析
- 文件存储管理

### 3. 课堂考勤模块

**功能描述：**
- 教师创建考勤任务
- 学生扫码签到
- 手动确认签到
- 考勤记录查询与统计

**技术要点：**
- qrcode：二维码生成
- 考勤任务管理
- 签到状态跟踪
- 考勤数据统计

### 4. 成绩管理模块

**功能描述：**

#### 4.1 成绩录入
- 单条成绩录入
- Excel模板批量导入
- 成绩数据验证

#### 4.2 统计分析
- 自动计算平均分、最高分、最低分、标准差
- 生成可视化图表：
  - 分数段分布图（柱状图）
  - 成绩趋势图（折线图）
  - 班级对比图

**技术要点：**
- pandas：Excel数据处理
- openpyxl：Excel文件读写
- matplotlib/seaborn：数据可视化
- 统计分析算法

### 5. 课堂互动模块

**功能描述：**
- 实时投票功能
- 在线提问系统
- 弹幕互动功能
- 实时消息推送

**技术要点：**
- Flask-SocketIO：WebSocket实时通信
- 事件驱动架构
- 消息队列管理

## 项目结构

```
dazuoye/
├── app/                          # 应用主目录
│   ├── __init__.py              # Flask应用初始化
│   ├── config.py                # 配置文件
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── material.py          # 资料模型
│   │   ├── attendance.py        # 考勤模型
│   │   ├── grade.py             # 成绩模型
│   │   └── interaction.py       # 互动模型
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证相关API
│   │   ├── material.py          # 资料中心API
│   │   ├── attendance.py        # 考勤API
│   │   ├── grade.py             # 成绩管理API
│   │   └── interaction.py       # 互动API
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证服务
│   │   ├── material_service.py  # 资料服务
│   │   ├── attendance_service.py # 考勤服务
│   │   ├── grade_service.py     # 成绩服务
│   │   └── interaction_service.py # 互动服务
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── file_handler.py      # 文件处理工具
│   │   ├── search_engine.py     # 搜索引擎工具
│   │   ├── qrcode_generator.py  # 二维码生成工具
│   │   ├── excel_handler.py     # Excel处理工具
│   │   └── chart_generator.py   # 图表生成工具
│   ├── static/                  # 静态文件
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/            # 上传文件存储
│   └── templates/               # 模板文件
│       ├── base.html
│       └── ...
├── migrations/                  # 数据库迁移文件
├── tests/                       # 测试文件
│   ├── __init__.py
│   └── test_*.py
├── .env                         # 环境变量配置
├── .gitignore                   # Git忽略文件
├── requirements.txt             # Python依赖包
├── README.md                    # 项目说明文档
└── run.py                       # 应用启动文件
```

## 技术栈

- **后端框架：** Flask 3.0.0
- **数据库ORM：** SQLAlchemy 2.0.23
- **数据库：** MySQL
- **认证：** Flask-Login + JWT
- **文件处理：** Flask-Uploads
- **搜索：** Whoosh
- **数据处理：** pandas, openpyxl
- **可视化：** matplotlib, seaborn
- **实时通信：** Flask-SocketIO
- **二维码：** qrcode

## 安装与运行

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件，配置以下内容：

```
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dbname

# JWT密钥
JWT_SECRET_KEY=your-secret-key-here

# Flask密钥
SECRET_KEY=your-flask-secret-key

# 文件上传配置
UPLOAD_FOLDER=app/static/uploads
MAX_UPLOAD_SIZE=16777216  # 16MB
```

### 4. 初始化数据库

```bash
# 创建数据库迁移
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. 运行应用

```bash
python run.py
```

## 开发计划

### 第一阶段：基础框架搭建
- [x] 项目结构创建
- [x] 依赖包配置
- [ ] 数据库模型设计
- [ ] 基础配置完成

### 第二阶段：用户认证模块
- [ ] 用户模型设计
- [ ] 注册/登录功能
- [ ] 权限控制实现
- [ ] JWT认证集成

### 第三阶段：资料中心模块
- [ ] 文件上传/下载
- [ ] 在线预览功能
- [ ] 分类管理
- [ ] 全文搜索

### 第四阶段：考勤模块
- [ ] 考勤任务创建
- [ ] 二维码生成
- [ ] 签到功能
- [ ] 考勤统计

### 第五阶段：成绩管理模块
- [ ] 成绩录入功能
- [ ] Excel导入
- [ ] 统计分析
- [ ] 图表生成

### 第六阶段：课堂互动模块
- [ ] WebSocket配置
- [ ] 投票功能
- [ ] 提问系统
- [ ] 弹幕功能

## 注意事项

1. **安全性：**
   - 所有密码使用bcrypt加密存储
   - JWT Token设置合理的过期时间
   - 文件上传需要类型和大小验证
   - SQL注入防护（使用ORM）

2. **性能优化：**
   - 文件存储使用对象存储（可选）
   - 数据库索引优化
   - 缓存机制（可选Redis）

3. **扩展性：**
   - 模块化设计，便于扩展
   - API接口标准化
   - 前后端分离架构

## 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。

