from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle
from typing import List
from rank_bm25 import BM25Okapi
import numpy as np
import jieba

class HybridRetriever(BaseRetriever):
    """支持归一化和权重调节的混合检索器"""
    
    def __init__(
        self, 
        vector_retriever: BaseRetriever,
        nodes: List[NodeWithScore],
        alpha: float = 0.5,  # 权重参数：BM25权重占比
        normalize_method: str = "minmax"  # 归一化方法
    ):
        super().__init__()
        self.vector_retriever = vector_retriever
        self.nodes = nodes
        self.alpha = alpha
        self.normalize_method = normalize_method
        
        # 初始化BM25
        self.node_texts = [node.text for node in nodes]
        self.tokenized_node_texts = [list(jieba.cut(text.lower())) for text in self.node_texts]
        self.bm25 = BM25Okapi(self.tokenized_node_texts)
        
        # 预计算节点ID映射
        self.node_id_to_index = {node.node_id: i for i, node in enumerate(nodes)}
    
    def _normalize_scores(self, scores: List[float]) -> np.ndarray:
        """分数归一化处理"""
        scores = np.array(scores)
        if self.normalize_method == "minmax":
            if np.max(scores) == np.min(scores):
                return np.zeros_like(scores)
            return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
        elif self.normalize_method == "zscore":
            return (scores - np.mean(scores)) / np.std(scores)
        else:
            raise ValueError(f"不支持的归一化方法: {self.normalize_method}")

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # 分词处理查询
        query = query_bundle.query_str
        tokenized_query = list(jieba.cut(query.lower()))
        
        # === BM25检索 ===
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_scores_norm = self._normalize_scores(bm25_scores)
        
        # === 向量检索 ===
        vector_nodes = self.vector_retriever.retrieve(query_bundle)
        
        # 提取向量检索分数并归一化
        vector_scores = [node.score for node in vector_nodes]
        vector_scores_norm = self._normalize_scores(vector_scores)
        
        # === 构建综合得分映射 ===
        combined_scores = {}
        
        # 处理BM25节点
        for idx, score in enumerate(bm25_scores_norm):
            node_id = self.nodes[idx].node_id
            combined_scores[node_id] = {
                "bm25": score,
                "vector": 0.0,  # 默认值
                "node": self.nodes[idx]
            }
        
        # 处理向量节点
        for node, score in zip(vector_nodes, vector_scores_norm):
            node_id = node.node.node_id
            if node_id in combined_scores:
                combined_scores[node_id]["vector"] = score
            else:
                combined_scores[node_id] = {
                    "bm25": 0.0,  # 默认值
                    "vector": score,
                    "node": node.node
                }
        
        # === 计算加权得分 ===
        combined_nodes = []
        for node_id, scores in combined_scores.items():
            weighted_score = (
                self.alpha * scores["bm25"] + 
                (1 - self.alpha) * scores["vector"]
            )
            combined_nodes.append(NodeWithScore(
                node=scores["node"],
                score=weighted_score
            ))
        
        # === 排序和去重 ===
        seen_ids = set()
        deduped_nodes = []
        for node in sorted(combined_nodes, key=lambda x: x.score, reverse=True):
            if node.node.node_id not in seen_ids:
                deduped_nodes.append(node)
                seen_ids.add(node.node.node_id)
        
        return deduped_nodes[:50]  # 控制返回数量