import uuid
import redis
import pickle
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis存储管理器
class RedisResponseManager:
    def __init__(self, mysql_manager, host='localhost', port=6379, db=0, password=None):
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password,
            decode_responses=False
        )
        self.mysql_manager = mysql_manager
        self.session_ttl = 24 * 3600
    
    def create_response_session(self, openid, question):
        """创建新的响应会话"""
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'openid': openid,
            'question': question,
            'answer': '',
            'status': 'processing',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'chunks': []
        }
        
        # 存储到Redis
        serialized_data = pickle.dumps(session_data)
        self.redis_client.setex(
            f"ai_session:{session_id}", 
            self.session_ttl, 
            serialized_data
        )
        
        # 同步到MySQL
        mysql_session_data = session_data.copy()
        mysql_session_data.pop('chunks', None)  # 移除不需要存储的字段
        self.mysql_manager.save_session(mysql_session_data)
        
        logger.info(f"创建新会话: {session_id}, 问题: {question}")
        return session_id
    
    def update_response(self, session_id, chunk, is_complete=False):
        """更新响应内容（流式）"""
        redis_key = f"ai_session:{session_id}"
        
        with self.redis_client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(redis_key)
                    existing_data = pipe.get(redis_key)

                    if existing_data and isinstance(existing_data, bytes):
                        session_data = pickle.loads(existing_data)
                        session_data['answer'] += chunk
                        session_data['chunks'].append(chunk)
                        session_data['updated_at'] = datetime.now()
                        
                        if is_complete:
                            session_data['status'] = 'completed'
                            logger.info(f"会话完成: {session_id}")
                        
                        # 更新Redis
                        pipe.multi()
                        pipe.setex(
                            redis_key, 
                            self.session_ttl, 
                            pickle.dumps(session_data)
                        )
                        pipe.execute()
                        
                        # 同步到MySQL
                        mysql_session_data = session_data.copy()
                        mysql_session_data.pop('chunks', None)
                        self.mysql_manager.save_session(mysql_session_data)
                        
                        break
                    else:
                        logger.warning(f"尝试更新不存在的会话: {session_id}")
                        break
                        
                except redis.WatchError:
                    continue
    
    def get_response(self, session_id):
        """获取响应信息"""
        # 首先尝试从Redis获取
        redis_key = f"ai_session:{session_id}"
        data = self.redis_client.get(redis_key)
        if isinstance(data, bytes):
            return pickle.loads(data)
        
        # 如果Redis中没有，从MySQL获取
        mysql_data = self.mysql_manager.get_session(session_id)
        if mysql_data:
            # 转换为与Redis相同的格式
            mysql_data['chunks'] = []
            return mysql_data
        
        return None
    
    def session_exists(self, session_id):
        """检查会话是否存在"""
        # 检查Redis
        if self.redis_client.exists(f"ai_session:{session_id}"):
            return True
        
        # 检查MySQL
        return self.mysql_manager.get_session(session_id) is not None
    
    def mark_failed(self, session_id, error_message):
        """标记处理失败"""
        redis_key = f"ai_session:{session_id}"
        
        with self.redis_client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(redis_key)
                    existing_data = pipe.get(redis_key)
                    
                    if isinstance(existing_data, bytes):
                        session_data = pickle.loads(existing_data)
                        session_data['status'] = 'failed'
                        session_data['answer'] = f"处理失败: {error_message}"
                        session_data['updated_at'] = datetime.now()
                        
                        pipe.multi()
                        pipe.setex(
                            redis_key, 
                            self.session_ttl, 
                            pickle.dumps(session_data)
                        )
                        pipe.execute()
                        
                        # 同步到MySQL
                        mysql_session_data = session_data.copy()
                        mysql_session_data.pop('chunks', None)
                        self.mysql_manager.save_session(mysql_session_data)
                        
                        logger.error(f"会话失败: {session_id}, 错误: {error_message}")
                        break
                    else:
                        logger.warning(f"尝试标记不存在的会话为失败: {session_id}")
                        break
                        
                except redis.WatchError:
                    continue
    
    def get_user_history(self, openid, limit=20, offset=0):
        """获取用户历史记录"""
        return self.mysql_manager.get_user_sessions(openid, limit, offset)
