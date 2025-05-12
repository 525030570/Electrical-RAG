import re
from pathlib import Path
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from typing import List, Dict, Optional
from build_knowledge_repository.clean_document import process_documents

UNSTRUCTURED_FILE_PATH = "File/Unstructured"

def extract_title(text: str) -> Optional[Dict]:
    """提取Markdown标题层级和内容"""
    match = re.search(r'^(#{1,6})\s*(.+)$', text, re.MULTILINE)
    return {"level": len(match.group(1)), "title": match.group(2)} if match else None

def parse_markdown_with_metadata(file_path: Path, llm_clean) -> List[Document]:
    """解析Markdown文件并保留结构化元数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 提取所有图片路径（保留原始文本中的图片引用）
    # images = re.findall(r'!\[.*?\]\((.*?)\)', text)
    
    # 去除标题符号
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # 将图片标记删除
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 去除段落之间的空行
    text = re.sub(r'\n\s*\n', '\n', text)
    
    if llm_clean == True:
        # 调用大模型进行文档清洗处理
        text = Document(text=text, metadata={})
    
        print("正在调用大模型进行文档清洗处理...")
        documents = process_documents([text])
        text = documents[0].text
        print("文档清洗处理完成！")


    return Document(
        text=text,
        metadata={
            "title": file_path.stem,
            "path": str(file_path),
            #"images": images,
            "source_label": file_path.parent.name  # 保留原始label_name分类
        }

    )

# 主处理逻辑
def process_markdown_files(file_path: List[str], llm_clean) -> List[Document]:
    documents = []
    # 递归遍历所有.md文件
    for file in file_path:  # 明确只处理.md文件
        file = Path(file)
        if file.is_file():
            try:
                documents.append(parse_markdown_with_metadata(file, llm_clean))
            except Exception as e:
                print(f"解析失败 {file}: {str(e)}")
                continue
    print(documents)
    
    parser = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=100,
        include_metadata=True,  # 确保元数据传递到节点
    )
    nodes = parser.get_nodes_from_documents(documents)
    print(nodes)
    
    # 为每个节点添加图片引用
    for node, original_doc in zip(nodes, documents):
        node.metadata.update({
            #"images": original_doc.metadata["images"],
            "title_hierarchy": get_title_hierarchy(node.text)  # 新增标题层级分析
        })
    
    return nodes

def get_title_hierarchy(text: str) -> List[Dict]:
    """分析文本中的标题层级关系"""
    titles = []
    for line in text.split('\n'):
        if title_info := extract_title(line):
            titles.append(title_info)
    return titles