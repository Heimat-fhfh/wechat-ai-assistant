
import requests
import json
import os

def upload_wechat_material(access_token, file_path, material_type='image'):
    """
    上传素材到微信公众号平台
    
    Args:
        access_token: 微信接口调用凭证
        file_path: 要上传的文件路径
        material_type: 素材类型，可选值：image, voice, video, thumb
    
    Returns:
        dict: 微信API返回的结果
    """
    
    # 微信素材上传API地址
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material"
    
    # 构造请求参数
    params = {
        'access_token': access_token,
        'type': material_type
    }
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        # 使用multipart/form-data格式上传文件
        with open(file_path, 'rb') as file:
            files = {'media': file}
            response = requests.post(url, params=params, files=files)
        
        # 解析返回结果
        result = response.json()
        
        # 检查请求是否成功
        if response.status_code == 200:
            return result
        else:
            raise Exception(f"上传失败: {result.get('errmsg', '未知错误')}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("解析微信API返回结果失败")

# 使用示例
if __name__ == "__main__":
    # 替换为你的实际参数
    ACCESS_TOKEN = "95_2yb2v9mnkrjoItfFOWr_7l9SbHNT3jwpPLQNylGc5uMFwrJ9xFxtbyOMlCvKV7nreGL8Y80kjGs4yRqGsj3DTfJvYMYB0rE_pUFMkGYG6WlOb8SbHEYLi2dWJF4VEZeADAHQL"
    FILE_PATH = "/home/fhfh/Work/project/we_chat/mp/image/校历图片.jpg"  # 例如: "/path/to/your/image.jpg"
    MATERIAL_TYPE = "image"  # 根据实际文件类型修改
    
    try:
        result = upload_wechat_material(ACCESS_TOKEN, FILE_PATH, MATERIAL_TYPE)
        print("上传成功！")
        print("返回结果:", json.dumps(result, indent=2, ensure_ascii=False))
        
        # 获取素材ID（如果上传成功）
        if 'media_id' in result:
            print(f"素材ID: {result['media_id']}")
            
    except Exception as e:
        print(f"上传失败: {str(e)}")

