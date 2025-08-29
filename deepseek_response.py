import time
import logging
import openai
from variable import response_manager
from define import DEEPSEEK_API_KEY


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

deepseek_client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY, 
    base_url="https://api.deepseek.com"
)

def stream_deepseek_response(question, session_id, openid):
    """调用DeepSeek API进行流式响应"""
    try:
        start_time = time.time()
        logger.info(f"开始调用DeepSeek API: {question}")

        with open("提示词.md", 'r', encoding="utf-8") as file:
            system_content = file.read()

        response = deepseek_client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            stream=True
        )
        
        full_content = ""
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content_chunk = chunk.choices[0].delta.content
                full_content += content_chunk
                
                # 实时更新响应
                response_manager.update_response(session_id, content_chunk)
                
                chunk_time = time.time() - start_time
                logger.debug(f"收到流式数据 {chunk_time:.2f}s: {content_chunk}")
        
        # 标记完成
        response_manager.update_response(session_id, "", is_complete=True)
        
        total_time = time.time() - start_time
        logger.info(f"DeepSeek API调用完成，耗时: {total_time:.2f}s，总字数: {len(full_content)}, \n 问题：{question}, \n AI回答：{full_content}")
        
    except Exception as e:
        error_msg = f"DeepSeek API调用失败: {str(e)}"
        logger.error(error_msg)
        response_manager.mark_failed(session_id, error_msg)
