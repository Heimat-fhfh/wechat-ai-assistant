import openai  # for OpenAI API calls
import time  # for measuring time duration of API calls

start_time = time.time()

DEEPSEEK_API_KEY = "sk-189c5bb744d64d7496c41ac21ddea47e"
client = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# send a ChatCompletion request to count to 100
response = client.chat.completions.create(
    model='deepseek-chat',
    messages=[
        {"role": "system", "content": "你是\"安师记\"公众号的AI助手，\"安师\"指的是安徽师范大学，\"记\"即为记录的意思，在回复消息时语言尽量简短，若需回答复杂内容也可详细说明。注意，严禁回答任何可能会损毁安徽师范大学形象的内容。"},
        {"role": "user", "content": "介绍一下你自己"},
    ],
    temperature=0,
    stream=True  # again, we set stream=True
)

# create variables to collect the stream of chunks
collected_chunks = []
collected_messages = []
# iterate through the stream of events
for chunk in response:
    chunk_time = time.time() - start_time  # calculate the time delay of the chunk
    collected_chunks.append(chunk)  # save the event response
    chunk_message = chunk.choices[0].delta  # extract the message
    collected_messages.append(chunk_message)  # save the message
    print(chunk_message.content,end="\n")
    # print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}")  # print the delay and text

# print the time delay and text received
print(f"Full response received {chunk_time:.2f} seconds after request")
full_reply_content = ''.join([m.content for m in collected_messages])
print(f"Full conversation received: {full_reply_content}")