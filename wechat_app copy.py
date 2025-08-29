from flask import Flask, request, render_template, jsonify, Response,send_from_directory
from wechatpy import parse_message
from wechatpy.utils import check_signature
from wechatpy.replies import TextReply,ImageReply
from wechatpy.exceptions import InvalidSignatureException
from getweather import getweatherahnu
from datetime import datetime
from deepseek_response import stream_deepseek_response
from variable import mysql_manager,response_manager,weather_cache
from function_match import text_to_event_match,ticket_match,ticket_match_html
import urllib.parse
from date_tern import parse_chinese_date
import os
from define import *
import threading
import re
import time
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 将时间编码为ISO格式
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 清理任务（主要是日志记录）
def cleanup_task():
    while True:
        time.sleep(3600)
        logger.info("系统运行正常，Redis自动清理机制运行中...")

# 微信公众号接口
@app.route('/we_chat/mp', methods=['GET', 'POST'])
def WeChatController():
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
        
        # 更新用户信息
        mysql_manager.update_user(msg.source)
        
        if msg.type == 'text':
            event = text_to_event_match(msg.content)

            if "帮助" in msg.content:
                return TextReply(content = """💬【贴心小提示】✨

无论您发送什么📩~
只要不包含特殊关键词✖️
都会由🤖安师记助手暖心回复哦！

💡 其他功能：
✨ 发送"帮助"查看所有指令
✨ 输入"天气"获取花津校区预报                      
✨ 发送"获取校历"获取25-26学年校历图片
✨ 发送"历史记录"获取你和AI的所有对话

(๑˃̵ᴗ˂̵)و 您的每个问题，我们都会认真解答~

🌟 24小时智能陪伴，学习生活全搞定！""", message=msg).render()
            
            elif "天气" in msg.content:
                return TextReply(content = getweatherahnu(weather_cache), message=msg).render()
            elif msg.content == "获取校历":
                return ImageReply(media_id = 'jqvHn1qQ4TluzlBLoyKz-wVfdK-9fJePwmQKFe_I83fUqTStuL5uesbt_K1N88Lg', message=msg).render()
            elif msg.content == "历史记录":
                return TextReply(content = "https://ahnucjx.cn/we_chat/history/"+msg.source, message=msg).render()
            
            elif re.search(r"你好(呀)?",msg.content):
                return TextReply(content = "你好呀！😊 这里是「安师记」的AI助手，很高兴为您服务！\n \
有什么关于安徽师范大学的问题需要帮忙解答吗？\n \
无论是课程安排、校历信息还是校园生活，我都可以帮你哦！✨", message=msg).render()
            
            elif event.get('事件') == '查询车票':

                timeRes = parse_chinese_date(event.get('时间'))
                if timeRes == '':
                    logger.info(event.get('时间'))
                    return TextReply(content = "'时间检测错误'" ,message=msg).render()
                
                event['时间'] = timeRes
                url_link = BASE_GENERATED_HTML + f"{timeRes}_{urllib.parse.quote(event.get('出发地', ''))}_{urllib.parse.quote(event.get('目的地', ''))}.html"
                
                res = ticket_match_html(event)
                if res == '':
                    return TextReply(content = "当前获取车票人数过多,请稍后重试" ,message=msg).render()
                elif res == "station_code_Error":
                    return TextReply(content = "城市信息读取错误，请重试" ,message=msg).render()
                elif res == "no_ticket":
                    return TextReply(content = "没有查询到相关车次信息" ,message=msg).render()
                
                return TextReply(content = f"{timeRes}的车票列表生成成功,请点击以下链接:\n"+url_link, message=msg).render()
                


            # 创建响应会话
            session_id = response_manager.create_response_session(
                msg.source, msg.content
            )
            
            # 生成结果页面URL
            result_url = f"https://ahnucjx.cn/ai-result/{session_id}"
            
            # 启动异步AI处理
            thread = threading.Thread(
                target=stream_deepseek_response, 
                args=(msg.content, session_id, msg.source)
            )
            thread.daemon = True
            thread.start()
            
            # 立即返回结果页面链接
            reply_content = f"🤖 AI正在回答您的问题，点击查看实时结果：\n{result_url}"
            reply = TextReply(content = reply_content, message=msg)
            
            return reply.render()
        
        elif msg.type == 'event':
            if msg.event == 'subscribe':
                reply = TextReply(content = """感谢关注《安师记》公众号，本公众号免费使用AI问答，更多定制内容等你发现🎊 真挚感谢您的关注——《安师记》官方公众号！✨
                                    
（✧∀✧） 这里为您准备了超有趣的AI智能问答服务！完全【免！费！】使用哦~

💎 隐藏惊喜：
• 🤖 AI智能互动超有趣
• ✨ 独家优质内容持续更新
• 📚 个性化内容一键定制

(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ 期待和您一起探索更多精彩！
快来体验吧~ 我们会用满满的爱心❤️为您服务！

✨ 发送关键字"帮助"查看所有指令
                                  
P.S. 您的每次点击都是对我的鼓励哟~ (●'◡'●)""", message=msg)
                return reply.render()
            return "success"
        
        return "success"
    return "Invalid request"

# AI回答结果网站
@app.route('/ai-result/<session_id>')
def ai_result_page(session_id):
    """AI结果展示页面"""
    if not response_manager.session_exists(session_id):
        logger.warning(f"会话不存在: {session_id}")
        return render_template('error.html', 
                             message="会话不存在或已过期",
                             session_id=session_id), 404
    
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

# AI对话历史记录界面
@app.route('/we_chat/history/<openid>')
def user_history(openid):
    """用户历史记录页面"""
    sessions = response_manager.get_user_history(openid)
    
    # 格式化时间
    for session in sessions:
        for key in ['created_at', 'updated_at']:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('history.html',
                         openid=openid,
                         sessions=sessions)

# AI对话历史记录API
@app.route('/api/history/<openid>')
def api_user_history(openid):
    """API接口：获取用户历史记录"""
    sessions = response_manager.get_user_history(openid)
    
    # 转换datetime对象
    for session in sessions:
        for key in ['created_at', 'updated_at']:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].isoformat()
    
    return jsonify({'success': True, 'sessions': sessions})

# AI对话流式传输接口
@app.route('/api/ai-stream/<session_id>')
def ai_stream_api(session_id):
    def generate():
        try:
            # 检查会话是否存在
            if not response_manager.session_exists(session_id):
                yield f"data: {json.dumps({'type': 'error', 'message': '会话不存在'})}\n\n" # 流式数据发送
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
                    
                    time.sleep(0.5)
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

# 车票结果表格展示
@app.route('/we_chat/ticket/<filename>')
def ticket_page(filename):
    
    return send_from_directory(
        GENERATED_HTML_DIR, 
        filename, 
        as_attachment=False  # 设为True会强制下载，False则在浏览器中显示
    )

# 错误界面
@app.route('/we_chat/error')
def error_page():
    return render_template('error.html', message="页面不存在")


if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    app.run(host='127.0.0.1', port=5001, threaded=True)

