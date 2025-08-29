# wechat_app.py

from flask import Flask, request
from wechatpy import parse_message, create_reply
from wechatpy.replies import TextReply,EmptyReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.messages import TextMessage, ImageMessage  # 导入消息类型
from threading import Thread

app = Flask(__name__)

# 微信公众号配置的Token
TOKEN = "mReXgbgYldXfqevVhXbljWoa1OB3XKF1"

def process_Text_message(msg):
    msg_source = msg.source
    msg_target = msg.source



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
            Thread(target=process_Text_message,args=(msg))
            return TextReply(content = f"你发送了: {msg.content}", message=msg).render()
        elif msg.type == 'image':
            return TextReply(content = "这是一张图片", message=msg).render()
        elif msg.type == 'voice':
            return TextReply(content = f"这是一段音频", message=msg).render()
        elif msg.type == 'shortvideo':
            return TextReply(content = f"这是一段短视频", message=msg).render()
        elif msg.type == 'video':
            return TextReply(content = f"这是一段视频", message=msg).render()
        elif msg.type == 'location':
            locationmsg = f"经度: {msg.location_y}, 纬度: {msg.location_x}"
            return TextReply(content = f"收到地理位置消息: {locationmsg}", message=msg).render()
        elif msg.type == 'link':
            return TextReply(content = f"这是一个链接", message=msg).render()
        elif msg.type == 'miniprogrampage':
            return TextReply(content = f"收到小程序卡片消息", message=msg).render()
        
        elif msg.type == 'event':
            if msg.event == 'subscribe':
                return TextReply(content = "感谢关注安师记公众号！", message=msg).render()
            elif msg.event == 'unsubscribe':
                # 取消关注处理
                return "success"
            else:
                return EmptyReply().render()
        else:
            return TextReply(content = f"不支持的消息类型", message=msg).render()

    # 添加默认返回值，虽然理论上不会执行到这里
    return "Invalid request"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)