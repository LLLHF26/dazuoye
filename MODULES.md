# 模块详细说明文档

## 模块架构概览

本项目采用分层架构设计，主要分为以下层次：
- **模型层（Models）**：数据模型定义
- **服务层（Services）**：业务逻辑处理
- **API层（API）**：接口路由处理
- **工具层（Utils）**：通用工具函数

---

## 1. 用户认证与权限管理模块

### 1.1 模块概述
实现多角色用户系统，支持管理员、教师、学生三种角色，提供完整的认证和权限控制功能。

### 1.2 功能清单

#### 用户注册
- 用户名、邮箱、密码注册
- 角色选择（学生/教师）
- 邮箱验证（可选）
- 密码强度验证

#### 用户登录
- 用户名/邮箱登录
- 密码验证
- JWT Token生成
- 记住我功能

#### 权限控制
- 基于角色的访问控制（RBAC）
- 权限中间件
- API权限验证
- 前端路由权限

### 1.3 数据模型设计

**User（用户表）**
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- role: 角色（admin/teacher/student）
- created_at: 创建时间
- last_login: 最后登录时间
- is_active: 是否激活

**Role（角色表）**
- id: 主键
- name: 角色名称
- permissions: 权限列表（JSON）

### 1.4 相关文件
- `app/models/user.py` - 用户数据模型
- `app/api/auth.py` - 认证API接口
- `app/services/auth_service.py` - 认证业务逻辑

### 1.5 技术要点
- Flask-Login：会话管理
- Flask-JWT-Extended：JWT认证
- bcrypt：密码加密
- 装饰器模式：权限验证

---

## 2. 资料中心模块

### 2.1 模块概述
提供完整的文件管理系统，支持上传、下载、预览、分类和搜索功能。

### 2.2 功能清单

#### 文件上传
- 多文件上传
- 文件类型验证
- 文件大小限制
- 上传进度显示

#### 文件下载
- 文件下载
- 下载权限控制
- 下载统计

#### 在线预览
- PDF预览
- Word文档预览
- 图片预览
- 视频播放（可选）

#### 分类管理
- 按课程分类
- 标签系统
- 多级分类
- 分类统计

#### 全文搜索
- 文件名搜索
- 文件内容搜索（PDF/Word）
- 标签搜索
- 高级搜索（组合条件）

### 2.3 数据模型设计

**Material（资料表）**
- id: 主键
- filename: 文件名
- original_filename: 原始文件名
- file_path: 文件存储路径
- file_size: 文件大小
- file_type: 文件类型
- course_id: 课程ID（外键）
- uploader_id: 上传者ID（外键）
- description: 描述
- tags: 标签（JSON数组）
- download_count: 下载次数
- created_at: 上传时间

**Course（课程表）**
- id: 主键
- name: 课程名称
- code: 课程代码
- teacher_id: 授课教师ID（外键）

**Tag（标签表）**
- id: 主键
- name: 标签名称
- material_count: 关联资料数量

### 2.4 相关文件
- `app/models/material.py` - 资料数据模型
- `app/api/material.py` - 资料中心API
- `app/services/material_service.py` - 资料业务逻辑
- `app/utils/file_handler.py` - 文件处理工具
- `app/utils/search_engine.py` - 搜索引擎工具

### 2.5 技术要点
- Flask-Uploads：文件上传
- Whoosh：全文搜索
- PyPDF2/python-docx：文档解析
- 文件存储策略

---

## 3. 课堂考勤模块

### 3.1 模块概述
实现课堂考勤管理，支持教师创建考勤任务，学生通过扫码或手动方式完成签到。

### 3.2 功能清单

#### 考勤任务管理
- 创建考勤任务
- 设置考勤时间
- 考勤地点设置
- 考勤任务列表

#### 二维码签到
- 生成考勤二维码
- 二维码有效期管理
- 扫码签到验证
- 防重复签到

#### 手动签到
- 手动确认签到
- 签到理由填写
- 迟到/早退标记

#### 考勤统计
- 出勤率统计
- 缺勤记录查询
- 考勤报表生成
- 导出考勤数据

### 3.3 数据模型设计

**AttendanceTask（考勤任务表）**
- id: 主键
- course_id: 课程ID（外键）
- teacher_id: 教师ID（外键）
- title: 考勤标题
- start_time: 开始时间
- end_time: 结束时间
- location: 考勤地点
- qr_code: 二维码内容
- qr_code_expire: 二维码过期时间
- status: 状态（进行中/已结束）

**AttendanceRecord（考勤记录表）**
- id: 主键
- task_id: 考勤任务ID（外键）
- student_id: 学生ID（外键）
- check_in_time: 签到时间
- check_in_type: 签到方式（扫码/手动）
- status: 状态（正常/迟到/早退/缺勤）
- remark: 备注

### 3.4 相关文件
- `app/models/attendance.py` - 考勤数据模型
- `app/api/attendance.py` - 考勤API
- `app/services/attendance_service.py` - 考勤业务逻辑
- `app/utils/qrcode_generator.py` - 二维码生成工具

### 3.5 技术要点
- qrcode：二维码生成
- 时间验证：签到时间判断
- 防重复机制：避免重复签到

---

## 4. 成绩管理模块

### 4.1 模块概述
提供完整的成绩管理功能，包括成绩录入、批量导入、统计分析和可视化展示。

### 4.2 功能清单

#### 成绩录入
- 单条成绩录入
- 成绩修改
- 成绩删除
- 成绩审核

#### Excel批量导入
- Excel模板下载
- 批量导入验证
- 导入错误提示
- 导入结果反馈

#### 统计分析
- 平均分计算
- 最高/最低分
- 标准差计算
- 及格率统计
- 优秀率统计

#### 可视化图表
- 分数段分布图（柱状图）
- 成绩趋势图（折线图）
- 班级对比图
- 个人成绩分析图

### 4.3 数据模型设计

**Grade（成绩表）**
- id: 主键
- student_id: 学生ID（外键）
- course_id: 课程ID（外键）
- exam_type: 考试类型（平时/期中/期末）
- score: 分数
- full_score: 满分
- percentage: 百分比
- remark: 备注
- created_at: 录入时间
- updated_at: 更新时间

**Course（课程表）**
- id: 主键
- name: 课程名称
- code: 课程代码
- credit: 学分
- teacher_id: 授课教师ID（外键）

### 4.4 相关文件
- `app/models/grade.py` - 成绩数据模型
- `app/api/grade.py` - 成绩管理API
- `app/services/grade_service.py` - 成绩业务逻辑
- `app/utils/excel_handler.py` - Excel处理工具
- `app/utils/chart_generator.py` - 图表生成工具

### 4.5 技术要点
- pandas：数据处理
- openpyxl：Excel操作
- matplotlib/seaborn：数据可视化
- 统计分析算法

---

## 5. 课堂互动模块

### 5.1 模块概述
实现实时课堂互动功能，包括投票、提问和弹幕等互动方式。

### 5.2 功能清单

#### 实时投票
- 创建投票
- 投票选项设置
- 实时投票统计
- 投票结果展示
- 匿名/实名投票

#### 在线提问
- 学生提问
- 问题分类
- 教师回答
- 问题点赞
- 问题搜索

#### 弹幕功能
- 实时弹幕发送
- 弹幕过滤
- 弹幕统计
- 弹幕历史记录

#### 实时消息
- WebSocket连接
- 消息推送
- 在线用户列表
- 消息历史

### 5.3 数据模型设计

**Vote（投票表）**
- id: 主键
- course_id: 课程ID（外键）
- creator_id: 创建者ID（外键）
- title: 投票标题
- description: 投票描述
- options: 选项（JSON）
- is_anonymous: 是否匿名
- start_time: 开始时间
- end_time: 结束时间
- status: 状态

**VoteRecord（投票记录表）**
- id: 主键
- vote_id: 投票ID（外键）
- user_id: 投票者ID（外键）
- option_id: 选项ID
- created_at: 投票时间

**Question（提问表）**
- id: 主键
- course_id: 课程ID（外键）
- student_id: 提问者ID（外键）
- content: 问题内容
- category: 问题分类
- answer: 回答内容
- answerer_id: 回答者ID（外键）
- like_count: 点赞数
- status: 状态（待回答/已回答）

**Danmaku（弹幕表）**
- id: 主键
- course_id: 课程ID（外键）
- user_id: 发送者ID（外键）
- content: 弹幕内容
- color: 弹幕颜色
- position: 弹幕位置
- created_at: 发送时间

### 5.4 相关文件
- `app/models/interaction.py` - 互动数据模型
- `app/api/interaction.py` - 互动API
- `app/services/interaction_service.py` - 互动业务逻辑

### 5.5 技术要点
- Flask-SocketIO：WebSocket实时通信
- 事件驱动架构
- 消息队列管理
- 实时数据同步

---

## 模块间关系

### 数据关联
- 用户模块是基础，其他模块都依赖用户信息
- 资料中心、考勤、成绩、互动都与课程关联
- 所有模块都需要权限验证

### 业务流程
1. 用户登录 → 获取Token
2. 教师创建课程 → 学生加入课程
3. 教师上传资料 → 学生下载/预览
4. 教师创建考勤 → 学生签到
5. 教师录入成绩 → 统计分析
6. 课堂互动 → 实时通信

---

## 开发优先级建议

### 第一阶段：基础功能
1. 用户认证与权限管理
2. 基础数据模型

### 第二阶段：核心功能
1. 资料中心（上传/下载）
2. 课堂考勤（基础功能）

### 第三阶段：扩展功能
1. 成绩管理（录入/统计）
2. 资料搜索功能

### 第四阶段：高级功能
1. 课堂互动（实时通信）
2. 数据可视化
3. 性能优化

---

## 注意事项

1. **安全性**
   - 所有API需要权限验证
   - 文件上传需要类型和大小限制
   - SQL注入防护
   - XSS攻击防护

2. **性能**
   - 大文件上传使用分片上传
   - 搜索功能使用索引优化
   - 数据库查询优化
   - 缓存机制

3. **用户体验**
   - 友好的错误提示
   - 加载状态提示
   - 响应式设计
   - 操作反馈

4. **可扩展性**
   - 模块化设计
   - 接口标准化
   - 配置外部化
   - 日志记录

