# 请复制此文件为 define.py 并填写实际的配置信息
# 注意：此文件仅作为模板，实际配置请勿提交到版本控制

TOKEN = "your_wechat_token_here"

# MySQL 配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'wechat_ai',
    'user': 'wechat_user',
    'password': 'your_mysql_password_here',  # 请修改为你的MySQL密码
    'charset': 'utf8mb4'
}

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # 如果有密码请填写

GENERATED_HTML_DIR = 'generated_html/'
BASE_GENERATED_HTML = 'https://your-domain.com/we_chat/ticket/'

DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

WEATHER_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
your_private_key_here
-----END PRIVATE KEY-----"""
WEATHER_API_HOST = "your_weather_api_host_here"
WEATHER_SUB_ID = 'your_weather_sub_id_here'
WEATHER_KEY_ID = 'your_weather_key_id_here'
