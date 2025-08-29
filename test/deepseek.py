from openai import OpenAI

# 全局常量 - DeepSeek API 密钥
DEEPSEEK_API_KEY = "sk-189c5bb744d64d7496c41ac21ddea47e"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def get_deepseek_response(user_message):
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是\"安师记\"公众号的AI助手，\"安师\"指的是安徽师范大学，\"记\"即为记录的意思，在回复消息时语言尽量简短，若需回答复杂内容也可详细说明。注意，严禁回答任何可能会损毁安徽师范大学形象的内容。"},
        {"role": "user", "content": user_message},
    ],
    stream=False
    )
    ai_response = response.choices[0].message.content
    return ai_response.strip()



# 示例使用
if __name__ == "__main__":
    user_input = "你好，介绍一下你自己"
    print("用户输入:", user_input)
    print("AI 回复:", get_deepseek_response(user_input))