import time
from jwtGenerate import getJWT
from typing import List, Dict, Any, Optional
import requests
import threading

class WeatherCache:
    def __init__(self, cache_duration: int = 3 * 3600):  # 默认3小时
        self.cache_duration = cache_duration
        self.last_timestamp: Optional[float] = None
        self.cached_data: List[Dict[str, Any]] = []
        self.lock = threading.Lock()  # 添加线程锁
    
    def get_weather_data(self, location: str) -> List[Dict[str, Any]]:
        """获取天气数据，带缓存功能"""
        current_time = time.time()

        # 检查缓存是否有效（不需要加锁的读操作）
        if (self.last_timestamp is not None and 
            current_time - self.last_timestamp <= self.cache_duration):
            return self.cached_data
        
        # 检查缓存是否有效
        with self.lock:
            # 再次检查，防止多个线程同时等待锁时重复更新
            if (self.last_timestamp is not None and 
                current_time - self.last_timestamp <= self.cache_duration):
                return self.cached_data
            
            print(f"线程 {threading.get_ident()} 开始更新天气数据...")
            try:
                data = self._fetch_weather_data(location)
                self.cached_data = data
                self.last_timestamp = current_time
                print(f"线程 {threading.get_ident()} 更新成功")
                return data
            except Exception as e:
                print(f"线程 {threading.get_ident()} 更新失败: {e}")
                # 返回旧的缓存数据（如果有）
                return self.cached_data if self.cached_data else []
    
    def _fetch_weather_data(self, location: str) -> List[Dict[str, Any]]:
        """实际获取天气数据的方法"""
        print("更新天气信息中")

        jwt_token = getJWT()
        
        response = requests.get(
            url='https://mr65nevk3n.re.qweatherapi.com/v7/grid-weather/3d',
            params={'location': location},
            headers={
                'Authorization': f'Bearer {jwt_token}',
                'Accept-Encoding': 'gzip'
            },
            timeout=10
        )
        
        response.raise_for_status()
        weather_data = response.json()
        
        if weather_data.get('code') != '200':
            raise Exception(f"API returned error code: {weather_data.get('code')}")
        
        return weather_data.get('daily', [])

def getweatherahnu(weather_cache:WeatherCache):
    weather = weather_cache.get_weather_data("118.375,31.33")
    if weather:
        weather_text = f'''🌤 安师大天气小报 𝙵𝚘𝚛 𝚈𝚘𝚞 🌈

☀️ 今日天气：
🌡 温度：{weather[0]['tempMin']}~{weather[0]['tempMax']}℃
🏙 白天：{weather[0]['textDay']}
🌙 夜间：{weather[0]['textNight']}

🌻 明日预告：
🌡 温度：{weather[1]['tempMin']}~{weather[1]['tempMax']}℃
🏙 白天：{weather[1]['textDay']}
🌌 夜间：{weather[1]['textNight']}

🦋 后天预告：
🌡 温度：{weather[2]['tempMin']}~{weather[2]['tempMax']}℃
🏞 白天：{weather[2]['textDay']}
🌠 夜间：{weather[2]['textNight']}

🌟 更多天气资讯，请持续关注！(๑•̀ㅂ•́)و✧

【天气来源：和风天气】'''
        return weather_text

    else:
        return "获取天气数据失败，小崔正在加速修正中，请稍后尝试"
    pass

# 使用示例
if __name__ == "__main__":
    weather_cache = WeatherCache()
    weather_data = weather_cache.get_weather_data("118.375,31.33")
    print(getweatherahnu(weather_cache))

    '''
    if weather:
        print(f"获取到 {len(weather)} 天的天气数据")
        
        # 访问第一天的最低温度（注意：你之前写的是tenpMin，但API返回的是tempMin）
        first_day_temp_min = weather[0]['tempMin']
        print(f"第一天最低温度: {first_day_temp_min}°C")
        
        # 打印所有天气信息
        for day in weather:
            print(f"\n日期: {day['fxDate']}")
            print(f"最高温度: {day['tempMax']}°C")
            print(f"最低温度: {day['tempMin']}°C")
            print(f"白天天气: {day['textDay']}")
            print(f"夜间天气: {day['textNight']}")
    else:
        print("未能获取天气数据")
'''





