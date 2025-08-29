
import mysql.connector
from mysql.connector import Error


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# MySQL数据库管理器
class MySQLManager:
    def __init__(self, config):
        self.config = config
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            logger.error(f"MySQL连接失败: {e}")
            return None
    
    def init_database(self):
        """初始化数据库和表"""
        try:
            # 先连接不指定数据库
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # 切换到目标数据库
            cursor.execute(f"USE {self.config['database']}")
            
            # 创建会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(36) NOT NULL UNIQUE,
                    openid VARCHAR(64) NOT NULL,
                    question TEXT NOT NULL,
                    answer LONGTEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'processing',
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    INDEX idx_openid (openid),
                    INDEX idx_created_at (created_at),
                    INDEX idx_session_id (session_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建用户表（用于存储用户信息）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    openid VARCHAR(64) NOT NULL UNIQUE,
                    nickname VARCHAR(100),
                    created_at DATETIME NOT NULL,
                    last_active DATETIME NOT NULL,
                    INDEX idx_openid (openid)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("MySQL数据库初始化完成")
            
        except Error as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def save_session(self, session_data):
        """保存会话到MySQL"""
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ai_sessions 
                    (session_id, openid, question, answer, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    answer = VALUES(answer), 
                    status = VALUES(status), 
                    updated_at = VALUES(updated_at)
                """, (
                    session_data['session_id'],
                    session_data['openid'],
                    session_data['question'],
                    session_data['answer'],
                    session_data['status'],
                    session_data['created_at'],
                    session_data['updated_at']
                ))
                connection.commit()
                cursor.close()
                connection.close()
        except Error as e:
            logger.error(f"保存会话到MySQL失败: {e}")
    
    def get_user_sessions(self, openid, limit=20, offset=0):
        """获取用户的历史会话"""
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT session_id, question, answer, status, created_at, updated_at
                    FROM ai_sessions 
                    WHERE openid = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s OFFSET %s
                """, (openid, limit, offset))
                
                sessions = cursor.fetchall()
                cursor.close()
                connection.close()
                return sessions
            return []
        except Error as e:
            logger.error(f"获取用户会话失败: {e}")
            return []
    
    def get_session(self, session_id):
        """根据session_id获取会话"""
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT session_id, openid, question, answer, status, created_at, updated_at
                    FROM ai_sessions 
                    WHERE session_id = %s
                """, (session_id,))
                
                session = cursor.fetchone()
                cursor.close()
                connection.close()
                return session
            return None
        except Error as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    def update_user(self, openid, nickname=None):
        """更新用户信息"""
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor()
                if nickname:
                    cursor.execute("""
                        INSERT INTO users (openid, nickname, created_at, last_active)
                        VALUES (%s, %s, NOW(), NOW())
                        ON DUPLICATE KEY UPDATE 
                        nickname = VALUES(nickname), 
                        last_active = NOW()
                    """, (openid, nickname))
                else:
                    cursor.execute("""
                        INSERT INTO users (openid, created_at, last_active)
                        VALUES (%s, NOW(), NOW())
                        ON DUPLICATE KEY UPDATE last_active = NOW()
                    """, (openid,))
                
                connection.commit()
                cursor.close()
                connection.close()
        except Error as e:
            logger.error(f"更新用户信息失败: {e}")


