from MysqlManager import MySQLManager
from RedisResponseManager import RedisResponseManager
from define import *
from getweather import WeatherCache

# 初始化MySQL管理器
mysql_manager = MySQLManager(MYSQL_CONFIG)

# 全局响应管理器
response_manager = RedisResponseManager(
    mysql_manager=mysql_manager,
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)

weather_cache = WeatherCache()
