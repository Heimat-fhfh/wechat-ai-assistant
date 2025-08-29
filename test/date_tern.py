# 首先安装库
# pip install dateparser

import dateparser

def natural_to_iso(date_string):
    parsed_date = dateparser.parse(date_string, languages=['zh'])
    if parsed_date:
        return parsed_date.date().isoformat()
    return None

# 示例
examples = [
    "后天",
    "明天",
    "3天前",
    "2023年10月15日",
    "October 15, 2023",
    "5月1日",
    "in 2 days"
    # "下周三",
    # "两周后",
]

# for example in examples:
#     iso_date = natural_to_iso(example)
#     print(f"'{example}' -> {iso_date}")

import dateparser
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 尝试解析并查看详细过程
date_string = "5月1日"
try:
    parsed_date = dateparser.parse(date_string)
    print(f"结果: {parsed_date}")
except Exception as e:
    print(f"错误: {e}")
