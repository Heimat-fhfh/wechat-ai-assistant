import requests
import json
from typing import Optional, Dict, Any

def get_wechat_access_token(appid: str, secret: str) -> Optional[Dict[str, Any]]:
    """
    获取微信access_token
    
    Args:
        appid: 微信公众号的AppID
        secret: 微信公众号的AppSecret
        force_refresh: 是否强制刷新token，默认为False
    
    Returns:
        dict: 包含access_token和expires_in的字典，如果请求失败返回None
    """
    # API端点
    url = "https://api.weixin.qq.com/cgi-bin/token"
    
    # 请求参数
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, params=params)
        response.raise_for_status()  # 检查HTTP错误
        
        # 解析JSON响应
        result = response.json()
        
        # 检查是否成功获取access_token
        if 'access_token' in result:
            return {
                'access_token': result['access_token'],
                'expires_in': result['expires_in']
            }
        else:
            # 如果返回错误信息，打印错误
            print(f"获取access_token失败: {result.get('errmsg', '未知错误')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    # 替换为你的实际AppID和AppSecret
    APPID = "wxf4a68ccdf4a8f00f"
    APPSECRET = "40a51a1a94e3cc28eaa2caf4abe70add"
    
    # 普通模式获取access_token
    token_info = get_wechat_access_token(APPID, APPSECRET)
    if token_info:
        print(f"Access Token: {token_info['access_token']}")
        print(f"有效期: {token_info['expires_in']}秒")
    
    # 强制刷新模式获取access_token
    # token_info = get_wechat_access_token(APPID, APPSECRET, force_refresh=True)
