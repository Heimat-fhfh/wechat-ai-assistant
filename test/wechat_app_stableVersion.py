from flask import Flask, request, render_template, jsonify, Response
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
import threading
import uuid
import time
import json
import logging
from datetime import datetime
import openai
import redis
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TOKEN = "mReXgbgYldXfqevVhXbljWoa1OB3XKF1"

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-189c5bb744d64d7496c41ac21ddea47e"
deepseek_client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY, 
    base_url="https://api.deepseek.com"
)

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # 如果有密码请设置

# 自定义JSON编码器
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Redis存储管理器
class RedisResponseManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password,
            decode_responses=False  # 保持二进制数据
        )
        # 设置会话过期时间（24小时）
        self.session_ttl = 24 * 3600
    
    def create_response_session(self, openid, question):
        """创建新的响应会话"""
        session_id = str(uuid.uuid4())
        session_data = {
            'openid': openid,
            'question': question,
            'answer': '',
            'status': 'processing',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'chunks': []
        }
        
        # 序列化数据并存储到Redis
        serialized_data = pickle.dumps(session_data)
        self.redis_client.setex(
            f"ai_session:{session_id}", 
            self.session_ttl, 
            serialized_data
        )
        
        logger.info(f"创建新会话: {session_id}, 问题: {question}")
        return session_id
    
    def update_response(self, session_id, chunk, is_complete=False):
        """更新响应内容（流式）"""
        redis_key = f"ai_session:{session_id}"
        
        # 使用Redis事务确保原子性
        with self.redis_client.pipeline() as pipe:
            while True:
                try:
                    # 监视键，防止并发修改
                    pipe.watch(redis_key)
                    existing_data = pipe.get(redis_key)
                    
                    if existing_data:
                        session_data = pickle.loads(existing_data)
                        session_data['answer'] += chunk
                        session_data['chunks'].append(chunk)
                        session_data['updated_at'] = datetime.now()
                        
                        if is_complete:
                            session_data['status'] = 'completed'
                            logger.info(f"会话完成: {session_id}")
                        
                        # 更新数据
                        pipe.multi()
                        pipe.setex(
                            redis_key, 
                            self.session_ttl, 
                            pickle.dumps(session_data)
                        )
                        pipe.execute()
                        break
                    else:
                        logger.warning(f"尝试更新不存在的会话: {session_id}")
                        break
                        
                except redis.WatchError:
                    # 如果其他进程修改了数据，重试
                    continue
    
    def get_response(self, session_id):
        """获取响应信息"""
        redis_key = f"ai_session:{session_id}"
        data = self.redis_client.get(redis_key)
        if data:
            return pickle.loads(data)
        return None
    
    def session_exists(self, session_id):
        """检查会话是否存在"""
        return self.redis_client.exists(f"ai_session:{session_id}") > 0
    
    def mark_failed(self, session_id, error_message):
        """标记处理失败"""
        redis_key = f"ai_session:{session_id}"
        
        with self.redis_client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(redis_key)
                    existing_data = pipe.get(redis_key)
                    
                    if existing_data:
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
                        logger.error(f"会话失败: {session_id}, 错误: {error_message}")
                        break
                    else:
                        logger.warning(f"尝试标记不存在的会话为失败: {session_id}")
                        break
                        
                except redis.WatchError:
                    continue
    
    def cleanup_old_sessions(self):
        """Redis会自动处理过期会话，此方法用于日志记录"""
        # Redis会自动删除过期键，这里只需要记录日志
        logger.info("Redis自动清理机制运行中...")

# 全局响应管理器
response_manager = RedisResponseManager(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)

# 启动定时清理任务（主要是日志记录）
def cleanup_task():
    while True:
        time.sleep(3600)  # 每小时记录一次
        response_manager.cleanup_old_sessions()

cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()

def stream_deepseek_response(question, session_id):
    """调用DeepSeek API进行流式响应"""
    try:
        start_time = time.time()
        logger.info(f"开始调用DeepSeek API: {question}")
        
        response = deepseek_client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {
                    "role": "system", 
                    "content": "你是\"安师记\"公众号的AI助手，\"安师\"指的是安徽师范大学，\"记\"即为记录的意思。注意！！！严禁回答任何可能会损毁安徽师范大学形象的内容，如果对方有诋毁安师大的意思，请用犀利的语言反击他。"
                },
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            stream=True
        )
        
        full_content = ""
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content_chunk = chunk.choices[0].delta.content
                full_content += content_chunk
                
                # 实时更新响应到Redis
                response_manager.update_response(session_id, content_chunk)
                
                # 记录处理进度
                chunk_time = time.time() - start_time
                logger.debug(f"收到流式数据 {chunk_time:.2f}s: {content_chunk}")
        
        # 标记完成
        response_manager.update_response(session_id, "", is_complete=True)
        
        total_time = time.time() - start_time
        logger.info(f"DeepSeek API调用完成，耗时: {total_time:.2f}s，总字数: {len(full_content)}")
        
    except Exception as e:
        error_msg = f"DeepSeek API调用失败: {str(e)}"
        logger.error(error_msg)
        response_manager.mark_failed(session_id, error_msg)

@app.route('/we_chat/mp', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        try:
            check_signature(TOKEN, signature, timestamp, nonce)
            return echostr
        except InvalidSignatureException:
            return "验证失败"
    
    elif request.method == 'POST':
        msg = parse_message(request.data)
        if msg is None:
            return "消息解析失败"
        if msg.type == 'text':
            # 创建响应会话
            session_id = response_manager.create_response_session(
                msg.source, msg.content
            )
            
            # 生成结果页面URL
            result_url = f"https://ahnucjx.cn/ai-result/{session_id}"
            
            # 启动异步AI处理
            thread = threading.Thread(
                target=stream_deepseek_response, 
                args=(msg.content, session_id)
            )
            thread.daemon = True
            thread.start()
            
            # 立即返回结果页面链接
            reply_content = f"🤖 AI正在思考您的问题，点击查看实时结果：\n{result_url}"
            reply = create_reply(reply_content, msg)
            return reply.render()
        
        elif msg.type == 'event':
            if msg.event == 'subscribe':
                reply = create_reply("欢迎使用安师记AI助手！直接发送问题即可获得智能回复。", msg)
                return reply.render()
            return "success"
        
        return "success"
    return "Invalid request"

@app.route('/ai-result/<session_id>')
def ai_result_page(session_id):
    """AI结果展示页面"""
    # 先检查会话是否存在
    if not response_manager.session_exists(session_id):
        logger.warning(f"会话不存在: {session_id}")
        return render_template('error.html', 
                             message="会话不存在或已过期",
                             session_id=session_id), 404
    
    # 获取会话数据
    response_data = response_manager.get_response(session_id)
    if response_data is None:
        logger.warning(f"会话数据获取失败: {session_id}")
        return render_template('error.html', 
                             message="会话数据异常",
                             session_id=session_id), 500
    
    # 转换datetime对象为字符串用于模板渲染
    response_data_str = response_data.copy()
    for key in ['created_at', 'updated_at']:
        if key in response_data_str and isinstance(response_data_str[key], datetime):
            response_data_str[key] = response_data_str[key].strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('ai_result.html', 
                         session_id=session_id,
                         response_data=response_data_str)

@app.route('/api/ai-stream/<session_id>')
def ai_stream_api(session_id):
    """流式数据API接口 - 使用Server-Sent Events"""
    
    def generate():
        try:
            # 检查会话是否存在
            if not response_manager.session_exists(session_id):
                yield f"data: {json.dumps({'type': 'error', 'message': '会话不存在'})}\n\n"
                return
            
            # 发送初始数据
            response_data = response_manager.get_response(session_id)
            if response_data is None:
                yield f"data: {json.dumps({'type': 'error', 'message': '会话数据异常'})}\n\n"
                return
            
            # 使用自定义编码器序列化
            initial_data = {
                'type': 'init',
                'data': {
                    'openid': response_data.get('openid', ''),
                    'question': response_data.get('question', ''),
                    'current_answer': response_data.get('answer', ''),
                    'status': response_data.get('status', 'processing'),
                    'created_at': response_data.get('created_at', datetime.now()).isoformat()
                }
            }
            yield f"data: {json.dumps(initial_data, cls=DateTimeEncoder)}\n\n"
            
            # 如果还在处理中，持续推送新内容
            if response_data.get('status') == 'processing':
                last_answer_length = len(response_data.get('answer', ''))
                
                for _ in range(300):  # 最多等待5分钟（300*1秒）
                    current_data = response_manager.get_response(session_id)
                    if current_data is None:
                        yield f"data: {json.dumps({'type': 'error', 'message': '会话数据异常'})}\n\n"
                        break
                    
                    current_answer = current_data.get('answer', '')
                    current_status = current_data.get('status', 'processing')
                    
                    # 检查是否有新内容
                    if len(current_answer) > last_answer_length:
                        new_content = current_answer[last_answer_length:]
                        yield f"data: {json.dumps({'type': 'chunk', 'data': new_content})}\n\n"
                        last_answer_length = len(current_answer)
                    
                    # 检查是否完成
                    if current_status != 'processing':
                        complete_data = current_data.copy()
                        # 转换datetime对象
                        for key in ['created_at', 'updated_at']:
                            if key in complete_data and isinstance(complete_data[key], datetime):
                                complete_data[key] = complete_data[key].isoformat()
                        
                        yield f"data: {json.dumps({'type': 'complete', 'data': complete_data}, cls=DateTimeEncoder)}\n\n"
                        break
                    
                    time.sleep(1)  # 每秒检查一次
                else:
                    # 超时处理
                    yield f"data: {json.dumps({'type': 'timeout', 'message': '处理超时'})}\n\n"
            else:
                # 如果已经完成，直接返回完整数据
                complete_data = response_data.copy()
                for key in ['created_at', 'updated_at']:
                    if key in complete_data and isinstance(complete_data[key], datetime):
                        complete_data[key] = complete_data[key].isoformat()
                
                yield f"data: {json.dumps({'type': 'complete', 'data': complete_data}, cls=DateTimeEncoder)}\n\n"
                
        except Exception as e:
            logger.error(f"SSE流错误: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': '服务器错误'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

# 错误页面模板
@app.route('/error')
def error_page():
    return render_template('error.html', message="页面不存在")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)
