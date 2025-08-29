# 安师记微信公众号AI助手

一个基于Flask和微信公众号开发的智能AI助手系统，为安徽师范大学学生提供校园服务。

## 🚀 功能特性

### 🤖 AI智能问答
- 基于DeepSeek模型的智能对话系统
- 流式响应，实时显示回答过程
- 对话历史记录查看功能
- 支持多轮对话上下文

### 🎫 车票查询服务
- 智能识别中文日期和时间
- 支持出发地和目的地识别
- 自动生成车票信息HTML页面
- 实时车票信息展示

### 🌤️ 天气查询
- 安徽师范大学花津校区天气预报
- 实时天气信息获取
- 天气数据缓存机制

### 📚 校园服务
- 校历信息查询
- 课程时间安排
- 校园卡办理指南
- 转专业相关信息
- 新生攻略

## 📁 项目结构

```
mp/
├── wechat_app.py          # 主应用文件，微信公众号接口
├── requirements.txt       # Python依赖包
├── define.py             # 配置文件（数据库、Token等）
├── gunicorn_config.py    # Gunicorn服务器配置
├── run.sh                # 启动脚本
├── 提示词.md             # AI系统提示词和校园信息
├── 
├── function_match.py     # 功能匹配模块
├── date_tern.py          # 中文日期解析
├── getweather.py         # 天气获取模块
├── deepseek_response.py  # DeepSeek AI响应处理
├── 
├── MysqlManager.py       # MySQL数据库管理
├── RedisResponseManager.py # Redis响应管理
├── jwtGenerate.py        # JWT生成工具
├── 
├── templates/            # HTML模板目录
│   ├── ai_result.html   # AI结果展示页面
│   ├── history.html     # 历史记录页面
│   └── error.html       # 错误页面
├── static/              # 静态资源目录
│   ├── css/             # CSS样式文件
│   └── js/              # JavaScript文件
├── generated_html/      # 生成的HTML文件目录
├── image/               # 图片资源目录
```

## 🛠️ 技术栈

- **后端框架**: Flask 3.1.1
- **Web服务器**: Gunicorn
- **数据库**: MySQL + Redis
- **AI模型**: DeepSeek
- **微信SDK**: wechatpy
- **部署**: 生产环境部署

## 📦 安装部署

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

### 1. 克隆项目
```bash
git clone <项目地址>
cd mp
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置敏感信息

#### 方法一：使用define.py（推荐用于开发）
复制 `define.example.py` 为 `define.py` 并填写实际配置：
```bash
cp define.example.py define.py
```

然后编辑 `define.py` 文件，填写实际的配置信息。

#### 方法二：使用环境变量（推荐用于生产）
复制 `.env.example` 为 `.env` 并填写实际配置：
```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填写实际的环境变量。

**重要安全提示**: 
- 请勿将 `define.py` 或 `.env` 文件提交到版本控制系统
- 这些文件包含敏感信息，已在 `.gitignore` 中配置忽略
- 生产环境建议使用环境变量或安全的配置管理服务

### 4. 配置数据库
根据您选择的配置方法，在相应的配置文件中设置数据库连接信息：

```python
# define.py 中的配置示例
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'wechat_ai',
    'user': 'your_username',
    'password': 'your_password',
    'charset': 'utf8mb4'
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
```

或者使用环境变量：
```bash
# .env 文件中的配置示例
MYSQL_HOST=localhost
MYSQL_DATABASE=wechat_ai
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_CHARSET=utf8mb4

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 4. 初始化数据库
创建相应的数据库和表结构（需要根据项目需求创建）。

### 5. 配置微信公众号
在微信公众号后台配置：
- 服务器地址: `https://your-domain.com/we_chat/mp`
- Token: 与 `define.py` 中的 `TOKEN` 一致

### 6. 启动服务
```bash
# 开发环境
python wechat_app.py

# 生产环境
./run.sh
```

## 🔧 配置文件说明

### define.py
- `TOKEN`: 微信公众号验证Token
- `MYSQL_CONFIG`: MySQL数据库配置
- `REDIS_*`: Redis缓存配置
- `GENERATED_HTML_DIR`: 生成HTML文件目录
- `BASE_GENERATED_HTML`: 生成HTML文件的基础URL

### gunicorn_config.py
Gunicorn服务器配置：
- workers: 工作进程数
- bind: 绑定地址和端口
- timeout: 超时时间
- worker_class: 工作进程类型

## 🌐 API接口

### 微信公众号接口
- `GET/POST /we_chat/mp` - 微信公众号消息接收和处理

### AI相关接口
- `GET /ai-result/<session_id>` - AI结果展示页面
- `GET /api/ai-stream/<session_id>` - AI流式响应接口
- `GET /we_chat/history/<openid>` - 用户历史记录页面
- `GET /api/history/<openid>` - 用户历史记录API

### 车票查询接口
- `GET /we_chat/ticket/<filename>` - 车票信息展示页面

## 🎯 使用说明

### 微信公众号交互
用户可以通过微信公众号发送以下指令：

1. **帮助** - 查看所有可用指令
2. **天气** - 获取花津校区天气预报
3. **获取校历** - 获取25-26学年校历图片
4. **历史记录** - 查看与AI的对话历史
5. **车票查询** - 查询指定日期的车票信息（如：查询8月30日芜湖到南京的车票）

### 日志查看
```bash
# 查看Gunicorn日志
tail -f gunicorn_access.log
tail -f gunicorn_error.log
```

## 📝 更新日志

### v1.0.0 (2025-08-29)
- 初始版本发布
- 基础AI问答功能
- 车票查询服务
- 天气查询功能
- 历史记录管理

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目维护者：小崔同学
- 邮箱：3466597694@qq.com
- 微信公众号：安师记

