import re
from date_tern import parse_chinese_date
from mcp_client import get_ticket,get_ticket_dict
from ticket_html import generate_ticket_html
from define import GENERATED_HTML_DIR
import logging
from ticket_html import check_file_exists


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ticket_match_html(info):
    
    filename = f"{info.get('时间')}_{info.get('出发地')}_{info.get('目的地')}.html"
    if check_file_exists(GENERATED_HTML_DIR,filename) == True:
        logger.info("文件已经存在")
        return filename
    
    ticket_dict = get_ticket_dict(info.get('时间'),info.get('出发地'),info.get('目的地'),True)
    return generate_ticket_html(ticket_dict,filename)

    

def ticket_match(info):
    timeRes = parse_chinese_date(info.get('时间'))
    if timeRes == '':
        logger.info(info.get('时间'))
        return '时间语言检测错误'
    logger.info(timeRes)
    return get_ticket(timeRes,info.get('出发地'),info.get('目的地'),True)

def text_to_event_match(text):
    # 更灵活的模式匹配
    patterns = [
        r'查询(.*?)从(.*?)到(.*?)的车票',
        r'查询(.*?)自(.*?)前往(.*?)的车票',
        r'查询(.*?)从(.*?)去(.*?)的车票'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return {
                '时间': match.group(1).strip(),
                '出发地': match.group(2).strip(),
                '目的地': match.group(3).strip(),
                '事件': '查询车票'
            }
    
    # 如果没有匹配到任何模式，尝试分步提取
    return {}