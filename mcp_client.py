from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import TextContent
from io import StringIO
import pandas as pd
import re
import asyncio
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_time_to_natural(time_str):
    """
    将时间格式转换为自然语言
    例如：00:39 → "39分钟", 01:30 → "1小时30分钟"
    """
    try:
        hours, minutes = map(int, time_str.split(':'))
        
        if hours == 0:
            return f"{minutes}分钟"
        elif minutes == 0:
            return f"{hours}小时"
        else:
            return f"{hours}小时{minutes}分钟"
    except:
        return time_str  # 如果解析失败，返回原字符串
    
# 将CSV数据转换为字典数组
def parse_csv_to_dict(csv_string):
    temp_data = re.sub(r',(?=[^\[\]]*\])', ';', csv_string)
    df = pd.read_csv(StringIO(temp_data))
    df['票价'] = df['票价'].str.replace(';', ',')
    ticket_dicts = df.to_dict('records')
    # 处理票价信息
    for train in ticket_dicts:
        train['票价信息'] = parse_ticket_prices(train['票价'])

    return ticket_dicts

# 解析票价信息
def parse_ticket_prices(price_str):
    prices = {}
    # 去除方括号并按逗号分割
    items = price_str.strip('[]').split(',')
    for item in items:
        if ':' in item:
            key, value = item.split(':', 1)
            prices[key.strip()] = value.strip()
    return prices

def str_train_info_natural(train_data):
    res = ''
    for train in train_data:
        res += f"车次 {train['车次']} 信息"
        if train['特色标签'] != '/':
            res += f"({train['特色标签']})：\n"
        else:
            res += '：\n'
        # res += f"  从 {train['出发站']} 出发，到达 {train['到达站']}\n"
        res += f"  发车时间：{train['出发时间']}\n  到达时间：{train['到达时间']}\n  历时{convert_time_to_natural(train['历时'])}\n"
        res += "  票价情况：\n"
        for seat_type, price_info in train['票价信息'].items():
            res += f"    {seat_type}: {price_info}\n"
        res += "\n"
    return res

# 用自然语言输出
def print_train_info_natural(train):
    print(f"车次 {train['车次']} 信息",end="")
    if train['特色标签'] != '/':
        print(f"({train['特色标签']})：")
    else:
        print('：')
    # print(f"  从 {train['出发站']} 出发，到达 {train['到达站']}")
    print(f"  发车时间：{train['出发时间']}，到达时间：{train['到达时间']}，历时{convert_time_to_natural(train['历时'])}")
    print("  票价情况：")
    for seat_type, price_info in train['票价信息'].items():
        print(f"    {seat_type}: {price_info}")

def get_ticket_dict(date:str,fromStation:str,toStation:str,csvFormat:bool):
    async def _call():
        logger.info(f"{date},{fromStation},{toStation},{csvFormat}")
        sse_url = "http://127.0.0.1:5002/sse"
        async with sse_client(url=sse_url) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                args = {
                    'date': date,
                    'fromStation': '',
                    'toStation': '',
                    'csvFormat': csvFormat,
                    # 'earliestStartTime': 20
                }
                try:
                    city_result = await session.call_tool("get-station-code-of-citys", arguments={"citys": f"{fromStation}|{toStation}"})
                    content_item = city_result.content[0]
                    if isinstance(content_item, TextContent):
                        city_json_data = json.loads(content_item.text)
                        args['fromStation'] = city_json_data[f'{fromStation}']['station_code']
                        args['toStation'] = city_json_data[f'{toStation}']['station_code']
                        logger.info(f'{fromStation}车站代码:',city_json_data[f'{fromStation}']['station_code'])
                        logger.info(f'{toStation}车站代码:',city_json_data[f'{toStation}']['station_code'])
                except Exception as e:
                    logger.error("城市代码获取失败，请检查")
                    return "station_code_Error"
                
                tickets_result = await session.call_tool("get-tickets", arguments=args)
                content_item = tickets_result.content[0]
                if isinstance(content_item, TextContent):
                    logger.info(content_item.text)
                    if content_item.text == "没有查询到相关车次信息":
                        logger.error("没有查询到相关车次信息")
                        return "no_ticket"
                    csv_data = content_item.text

                    # 转换数据
                    train_data = parse_csv_to_dict(csv_data)
                    return train_data

    return asyncio.run(_call())


def get_ticket(date:str,fromStation:str,toStation:str,csvFormat:bool):
    
    train_data = get_ticket_dict(date,fromStation,toStation,csvFormat)

    # 输出所有车次信息
    res_str = str_train_info_natural(train_data)
    # print(train_data)
    #print("从芜湖到合肥的列车信息：\n")
    # print(res_str)
    logger.info(f'输出字数:{len(res_str)}')
    return res_str
                    


'''
查询 in str
提取XX时间
提取XX地点
date: XX时间
fromStation: 芜湖 -> 车站编码
toStation: XX地点 -> 车站编码
csvFormat: false|true

查询XX时间到XX地点的车票
'''




if __name__ == "__main__":
    print(get_ticket('2025-08-28','芜湖','合肥',True))