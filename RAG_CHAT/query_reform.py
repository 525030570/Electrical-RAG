from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
        api_key=os.getenv("online_model_API_KEY"),
        base_url=os.getenv("online_model_API_URL"),
    )   


def query_reform(content: str) -> str:
    
    system_prompt = """
    你是一位专业的提示词工程师，擅长为大模型撰写提示词。
    任务：将用户输入的原始查询（Query）重写为更规范、具体的表达形式，使其更符合知识库文档的专业术语和语义结构，从而提升RAG系统的检索效果。

    要求：
    1. **保留原意**：改写后的查询需与原始查询语义一致。
    2. **增强专业性**：添加领域术语或技术细节（如品牌全称、产品型号、功能参数等）。
    3. **明确问题结构**：使用疑问句式或条件限定（如“哪款...”、“如何...”、“基于...”）。
    4. **避免歧义**：消除口语化表达或模糊表述（如“最好”需具体化为“性能最强”或“评分最高”）。
    5. **只输出重构后的查询**：避免输出与查询无关的其他信息。

    输入格式：
    - 原始查询："用户输入的原始问题"

    输出格式：
    - 改写后的查询："{规范化、具体化的查询}"**

    示例：
    原始查询："苹果手机拍照最好的型号"
    改写后的查询："苹果公司发布的iPhone型号中，哪款相机性能最强？"**

    请根据以上规则，对以下查询进行改写：
    原始查询："用户输入的原始问题"
    改写后的查询：
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("online_chat_model_name"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.3 
        )
        print("LLM重写完成")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM处理失败: {str(e)}")
        return content  # 失败时返回原文

