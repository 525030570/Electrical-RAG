import gradio as gr
import os
import shutil
from llama_index.core import VectorStoreIndex,Settings,SimpleDirectoryReader
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SentenceSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from dotenv import load_dotenv
from pathlib import Path
from build_knowledge_repository.upload_file import *
from build_knowledge_repository.md_process import  process_markdown_files
from build_knowledge_repository.minerU import minerU_process
from build_knowledge_repository.clean_document import process_documents
from build_knowledge_repository.file_read import read_file



load_dotenv()

DB_PATH = "VectorStore"
STRUCTURED_FILE_PATH = "File/Structured"
UNSTRUCTURED_FILE_PATH = "File/Unstructured"
TMP_NAME = "tmp_abcd"

embedding_model = os.getenv("embedding_model")
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model
)
EMBED_MODEL = LangchainEmbedding(embeddings)




# 设置嵌入模型
Settings.embed_model = EMBED_MODEL
# 刷新知识库
def refresh_knowledge_base():
    return os.listdir(DB_PATH)

# 创建非结构化向量数据库
def create_unstructured_db(db_name:str,label_name:list,md:bool,llm_clean:bool,chunk_size:int, chunk_overlap:int, file_load:str):
    print(f"知识库名称为：{db_name}，类目名称为：{label_name}")
    if label_name is None:
        gr.Info("没有选择类目")
    elif len(db_name) == 0:
        gr.Info("没有命名知识库")
    # 判断是否存在同名向量数据库
    elif db_name in os.listdir(DB_PATH):
        gr.Info("知识库已存在，请换个名字或删除原来知识库再创建")
    else:
        gr.Info("正在创建知识库，请等待知识库创建成功信息显示后前往RAG问答")

        if md:
            documents = []
            for label in label_name:
                label_path = os.path.join(UNSTRUCTURED_FILE_PATH,label)
                label_path_obj = Path(label_path)
                for file in label_path_obj.glob('**/*.pdf'):  # 明确只处理.pdf文件
                    if file.is_file():
                        try:
                            out_file_path = minerU_process(file)
                            documents.append(out_file_path)
                            print(documents)
                        except Exception as e:
                            print(f"解析失败 {file}: {str(e)}")
                            continue

            nodes =  process_markdown_files(documents, llm_clean)

        else:
            documents = []
            for label in label_name:
                label_path = os.path.join(UNSTRUCTURED_FILE_PATH,label)
                
                if file_load == "文本加载":
                    
                    path_obj = Path(label_path)
                    for file in path_obj.glob('**/*'):
                        if file.is_file():
                            documents.append(read_file(str(file))) 
                else:
                    documents.extend(SimpleDirectoryReader(label_path).load_data())
            
            if llm_clean == True:
                # 调用大模型进行文档清洗处理
                documents = process_documents(documents)

            splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            nodes = splitter.get_nodes_from_documents(documents)

        index = VectorStoreIndex(
            nodes
        )

        db_path = os.path.join(DB_PATH,db_name)
        if not os.path.exists(db_path):
            os.mkdir(db_path)
            index.storage_context.persist(db_path)     
        elif os.path.exists(db_path):
            pass
        gr.Info("知识库创建成功，可前往RAG问答进行提问")
    
# 创建结构化向量数据库
def create_structured_db(db_name:str,data_table:list):
    print(f"知识库名称为：{db_name}，数据表名称为：{data_table}")
    if data_table is None:
        gr.Info("没有选择数据表")
    elif len(db_name) == 0:
        gr.Info("没有命名知识库")
    # 判断是否存在同名向量数据库
    elif db_name in os.listdir(DB_PATH):
        gr.Info("知识库已存在，请换个名字或删除原来知识库再创建")
    else:
        gr.Info("正在创建知识库，请等待知识库创建成功信息显示后前往RAG问答")
        documents = []
        for label in data_table:
            label_path = os.path.join(STRUCTURED_FILE_PATH,label)
            documents.extend(SimpleDirectoryReader(label_path).load_data())
        # index = VectorStoreIndex.from_documents(
        #     documents
        # )
        nodes = []
        for doc in documents:
            doc_content = doc.get_content().split('\n')
            for chunk in doc_content:
                node = TextNode(text=chunk)
                node.metadata = {'source': doc.get_doc_id(),'file_name':doc.metadata['file_name']}
                nodes = nodes + [node]
        index = VectorStoreIndex(nodes)
        db_path = os.path.join(DB_PATH,db_name)
        if not os.path.exists(db_path):
            os.mkdir(db_path)
        index.storage_context.persist(db_path)
        gr.Info("知识库创建成功，可前往RAG问答进行提问")


# 删除指定名称知识库
def delete_db(db_name:str):
    if db_name is not None:
        folder_path = os.path.join(DB_PATH, db_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            gr.Info(f"已成功删除{db_name}知识库")
            print(f"已成功删除{db_name}知识库")
        else:
            gr.Info(f"{db_name}知识库不存在")
            print(f"{db_name}知识库不存在")

# 实时更新知识库列表
def update_knowledge_base():
    return gr.update(choices=os.listdir(DB_PATH))

# 临时文件创建知识库
def create_tmp_kb(files, llm_clean_tmp, chunk_size_tmp, chunk_overlap_tmp, file_load_tmp):
    if not os.path.exists(os.path.join("File",TMP_NAME)):
        os.mkdir(os.path.join("File",TMP_NAME))
    for file in files:
        file_name = os.path.basename(file)
        shutil.move(file,os.path.join("File",TMP_NAME,file_name))

    if file_load_tmp == "文本加载":
        
        documents = []

        for file in Path(os.path.join("File",TMP_NAME)).glob('**/*'):
            if file.is_file():
                documents.append(read_file(str(file))) 
    else:
        documents = SimpleDirectoryReader(os.path.join("File",TMP_NAME)).load_data()

    if llm_clean_tmp == True:
        print("正在调用大模型进行文档清洗处理")
        documents = process_documents(documents)
    
    splitter = SentenceSplitter(chunk_size=chunk_size_tmp, chunk_overlap=chunk_overlap_tmp)
    nodes = splitter.get_nodes_from_documents(documents)
    index = VectorStoreIndex(
            nodes
        )
    db_path = os.path.join(DB_PATH,TMP_NAME)
    if not os.path.exists(db_path):
        os.mkdir(db_path)
    index.storage_context.persist(db_path)

# 清除tmp文件夹下内容 
def clear_tmp():
    if os.path.exists(os.path.join("File",TMP_NAME)):
        shutil.rmtree(os.path.join("File",TMP_NAME))
    if os.path.exists(os.path.join(DB_PATH,TMP_NAME)):
        shutil.rmtree(os.path.join(DB_PATH,TMP_NAME))