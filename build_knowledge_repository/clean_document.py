from openai import OpenAI
from typing import List
import time
import os
from dotenv import load_dotenv
from llama_index.core.schema import Document


load_dotenv()
client = OpenAI(
        api_key=os.getenv("online_model_API_KEY"),
        base_url=os.getenv("online_model_API_URL"),
    )   


def clean_document_content(content: str) -> str:
    
    system_prompt = """
    你是一位专业的数据清洗工程师，擅长处理多领域文本，确保数据干净准确。
    任务目标：对文档进行智能化清洗，确保内容完整性同时去除噪声，为RAG系统提供高质量输入。
    
    请严格按以下规则清洗文档：

    1. 合并碎片化段落（保留序列词连贯性）。
        段落优化规则：
        - **碎片合并**：
        - 合并条件：相邻段落若满足以下任意一条则合并：
            1. 后一段落首句缺少主语且前一段落末句语义不完整
            2. 段落长度<15字符且非独立标题/列表项
            3. 包含序列词断句（如"首先，"在段末而"其次"在下一段首）
        - 禁止操作：不得改变原文字符顺序或删除有效内容

        - **逻辑保护**：
        - 强制保留所有序列标记（"第一、...第二、...最后"等）的段落连续性
        - 保持学术文献中的"Figure 1:"、"Table 2："等标注与描述文本的原始位置

    2. 移除：页眉页脚、广告、乱码、空白行、重复内容。
        噪声过滤规则：
        - **必清除项**：
        ✓ 页眉页脚（含页码/文档路径）
        ✓ 广告语（含"点击注册"、"限时优惠"等模式文本）
        ✓ 乱码（如"^%$#@"等连续非语言字符）
        ✓ 空白行（连续空行保留1行）
        ✓ 重复内容（相似度>90%的相邻段落）
        
        - **条件清除项**：
        ✓ 版权声明（仅当出现在文档首尾1/5区域时移除）
        ✓ HTML标签（保留<table><ul>等语义化标签内容）
        ✓ 无效行（如仅含"- - - -"的分隔符）

        - **特殊保护**：
        ✓ 保留法律文档中的"§1.2"等条款编号
        ✓ 保持代码块中的缩进和换行
    
    3. 保留：正文原内容、逻辑标记、列表/表格结构。
        格式保留规则：
        - **结构标记**：
        • 章节标题：除文档第一个标题外，仅保留带有数字含义的标题，如"## 1.1 引言"，"# 一、研究背景"等含有数字含义的层级标记，其余标题降为正文
        • 列表项：保留"-"、"•"、"1)"等列表前缀
        • 表格：转换为Markdown格式（保留行列关系）

        - **引用保护**：
        • 学术引用如"[1-3]"保持原位
        • 直接引语（"..."）不得拆分

    4. 增强要求：
        - **语义校验**：
        1. 对合并后的段落进行语法连贯性检查
        2. 中英文混排时确保空格规范（如"GPT模型[10]"）

    输出只返回清洗后的纯文本，不要额外说明
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
        print("LLM清洗完成")
        print(response.choices[0].message.content)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI处理失败: {str(e)}")
        return content  # 失败时返回原文

def process_documents(documents: List[Document]) -> List[Document]:
    """处理文档列表并保持原结构"""
    processed_docs = []
    
    for doc in documents:
        if hasattr(doc, 'text') and doc.text:  # 检查是否有文本内容
            original_text = doc.text
            
            # 分块处理（避免超过token限制）
            chunk_size = 5000 
            text_chunks = [original_text[i:i+chunk_size] 
                          for i in range(0, len(original_text), chunk_size)]
            
            cleaned_chunks = []
            for chunk in text_chunks:
                cleaned = clean_document_content(chunk)
                cleaned_chunks.append(cleaned)
                time.sleep(1)  # 避免速率限制
            
            # 合并处理后的块
            doc.text = ''.join(cleaned_chunks)
            # 添加处理标记到 metadata 中
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata['cleaned'] = True
            
        processed_docs.append(doc)
        
    
    return processed_docs