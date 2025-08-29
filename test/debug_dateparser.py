import dateparser
import dateparser_data

def debug_dateparser():
    """调试dateparser的解析过程"""
    
    # 查看dateparser是否真的支持"后天"
    from dateparser_data.settings.default import default_loader
    zh_settings = default_loader.get_language_settings('zh')
    
    print("中文翻译映射:")
    for key, values in zh_settings.info.get('translations', {}).items():
        if '后天' in values or 'in 2 days' in key:
            print(f"{key}: {values}")
    
    # 测试解析
    test_cases = ["后天", "in 2 days", "明天", "today"]
    
    print("\n解析测试:")
    for case in test_cases:
        result = dateparser.parse(case, languages=['zh'])
        print(f"'{case}' -> {result}")

# 运行调试
debug_dateparser()