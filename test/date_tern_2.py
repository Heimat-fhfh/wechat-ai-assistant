from cn2date import cn2date
from datetime import datetime

def parse_chinese_date(date_str):
    try:
        # 使用 cn2date 解析
        results = cn2date.parse(date_str)
        if results:
            # 调用 datetime() 方法获取实际的 datetime 对象
            return results[0].datetime().date().isoformat()
        else:
            return None
    except Exception as e:
        print(f"cn2date 解析错误: {e}")
        return None

# 测试
test_cases = ["后天", "5月1日", "昨天", "十二月31日"]
for case in test_cases:
    result = parse_chinese_date(case)
    print(f"'{case}' -> {result}")