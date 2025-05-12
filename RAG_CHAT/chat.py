import os
from llama_index.core import StorageContext,load_index_from_storage,Settings
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.embeddings.langchain import LangchainEmbedding
from RAG_CHAT.HybridRetriever import HybridRetriever
from RAG_CHAT.online_model import online_model_chat
from build_knowledge_repository.create_db import *
from dotenv import load_dotenv
from RAG_CHAT.local_model import local_model_chat
import re
from RAG_CHAT.query_reform import query_reform

load_dotenv()

DB_PATH = "VectorStore"
TMP_NAME = "tmp_abcd"

rerank_model = os.getenv("rerank_model")
embedding_model = os.getenv("embedding_model")
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model
)
EMBED_MODEL = LangchainEmbedding(embeddings)

# 设置嵌入模型
Settings.embed_model = EMBED_MODEL

def get_model_response(multi_modal_input,history,temperature,max_tokens,history_round,db_name,similarity_threshold,chunk_cnt,hybrid_retrieve, re_rank, thinking, model, llm_clean_tmp, chunk_size_tmp, chunk_overlap_tmp, file_load_tmp, query_change, weight):
    # prompt = multi_modal_input['text']
    prompt = history[-1][0]
    tmp_files = multi_modal_input['files']
    if os.path.exists(os.path.join("File",TMP_NAME)):
        db_name = TMP_NAME
    else:
        if tmp_files:
            create_tmp_kb(tmp_files, llm_clean_tmp, chunk_size_tmp, chunk_overlap_tmp, file_load_tmp)
            db_name = TMP_NAME

    if query_change == True:
        prompt = query_reform(prompt)
        
    print(f"prompt:{prompt},tmp_files:{tmp_files},db_name:{db_name}")
    try:
        storage_context = StorageContext.from_defaults(
            persist_dir=os.path.join(DB_PATH,db_name)
        )
        index = load_index_from_storage(storage_context)
        print("index获取完成")

        retriever_engine = index.as_retriever(
            similarity_top_k=10,
        )
        retrieve_chunk = retriever_engine.retrieve(prompt)
        #print(f"原始chunk为：{retrieve_chunk}")
        

        if hybrid_retrieve == True:

            nodes = index.docstore.docs.values()
            # 转换为List[BaseNode]后直接传入
            nodes_list = list(nodes)  # 明确转换为列表
            #创建混合检索器
            hybrid_retriever = HybridRetriever(retriever_engine, nodes_list, weight)
           
            # 混合检索结果
            hybrid_results = hybrid_retriever.retrieve(prompt)
            for node in hybrid_results:
                print('混合检索完成')
                print(f"Score: {node.score:.2f} - {node.text[:100]}...\n-----")

            if len(hybrid_results) > 0 :
                retrieve_chunk = hybrid_results
        
        if re_rank == True:
            # 实例化 reranker（已定义）
            reranker = SentenceTransformerRerank(top_n=chunk_cnt, model=rerank_model)
            # 使用 reranker 对检索结果进行重排序
            retrieve_chunk = reranker.postprocess_nodes(retrieve_chunk, query_str=prompt)

        try:
            results = retrieve_chunk[:chunk_cnt]
           
            print(f"rerank成功，重排后的chunk为：{results}")
        except:
            results = retrieve_chunk[:chunk_cnt]
            print(f"rerank失败，chunk为：{results}")
        chunk_text = ""
        chunk_show = ""
        for i in range(len(results)):
            if results[i].score >= similarity_threshold:
                chunk_text = chunk_text + f"## {i+1}:\n {results[i].text}\n"
                chunk_show = chunk_show + f"## {i+1}:\n {results[i].text}\nscore: {round(results[i].score,2)}\n"
        print(f"已获取chunk：{chunk_text}")
        prompt_template = f"请参考以下内容：{chunk_text}，以合适的语气回答用户的问题：{prompt}。如果参考内容中有图片链接也请直接返回。请遵循以下回答原则：1. 仅基于提供的参考内容回答问题，不要使用你自己的知识；2. 如果参考内容中没有足够信息，请坦诚告知你无法回答；3. 回答应该全面、准确、有条理，并使用适当的段落和结构；4. 请用中文回答；5. 在回答末尾标注信息来源。请现在开始回答："
    except Exception as e:
        print(f"异常信息：{e}")
        prompt_template = prompt
        chunk_show = ""

    history[-1][-1] = ""

    if model == "local_model":
        res = local_model_chat(history, history_round, prompt_template, temperature, max_tokens, thinking)
        # 解析返回的文本内容，将图片链接替换为图片展示
        res_with_images = re.sub(r'(http[s]?://[^\s]+)', lambda match: f'<img src="{match.group(1)}" alt="图片" style="max-width: 100%; height: auto;">', res)
        history[-1][-1] = res_with_images
        yield history,chunk_show

    else:
        res = online_model_chat(history, history_round, prompt_template, temperature, max_tokens)
        assistant_response = ""
        for chunk in res:
            content = chunk.choices[0].delta.content
            if content is not None:
                assistant_response += content
            history[-1][-1] = assistant_response
            yield history,chunk_show


