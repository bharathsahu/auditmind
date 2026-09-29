import math
import re
from typing import List, Dict, Any, Set, Optional
from sqlalchemy.orm import Session
from app.models.database import MemoryNode

class HybridSearchService:
    def __init__(self, k_rrf: int = 60):
        self.k_rrf = k_rrf

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into lower-case alphanumeric tokens."""
        if not text:
            return []
        return re.findall(r'\w+', text.lower())

    def bm25_score(self, query_tokens: Set[str], node: MemoryNode) -> float:
        """BM25 & exact key code matching score."""
        content = (node.content or "").lower()
        tags = (node.tags or "").lower()
        category = (node.category or "").lower()
        ref_code = (node.reference_code or "").lower()

        score = 0.0

        for token in query_tokens:
            if token in ref_code and len(token) > 2:
                score += 15.0
            if token in tags:
                score += 5.0
            if token in content:
                freq = content.count(token)
                score += 2.0 * math.log(1 + freq)
            if token in category:
                score += 3.0

        return score

    def vector_dense_score(self, query_tokens: Set[str], node: MemoryNode) -> float:
        """Dense similarity heuristic (TF-IDF term vector overlap)."""
        content_tokens = set(self.tokenize(node.content))
        tags_tokens = set(self.tokenize(node.tags))
        all_node_tokens = content_tokens.union(tags_tokens)

        if not all_node_tokens or not query_tokens:
            return 0.0

        intersection = query_tokens.intersection(all_node_tokens)
        jaccard_sim = len(intersection) / len(query_tokens.union(all_node_tokens))
        
        year_boost = 1.2 if node.year and str(node.year) in query_tokens else 1.0
        return jaccard_sim * 10.0 * year_boost

    def reciprocal_rank_fusion(
        self, 
        bm25_ranked: List[Dict[str, Any]], 
        dense_ranked: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Combine keyword (BM25) and dense vector ranks using RRF formula."""
        rrf_map: Dict[int, float] = {}
        memory_obj_map: Dict[int, Dict[str, Any]] = {}

        for rank, item in enumerate(bm25_ranked, 1):
            item_id = item["id"]
            memory_obj_map[item_id] = item
            rrf_map[item_id] = rrf_map.get(item_id, 0.0) + (1.0 / (self.k_rrf + rank))

        for rank, item in enumerate(dense_ranked, 1):
            item_id = item["id"]
            memory_obj_map[item_id] = item
            rrf_map[item_id] = rrf_map.get(item_id, 0.0) + (1.0 / (self.k_rrf + rank))

        sorted_ids = sorted(rrf_map.keys(), key=lambda mem_id: rrf_map[mem_id], reverse=True)

        fused_results = []
        for mem_id in sorted_ids[:top_k]:
            res = memory_obj_map[mem_id].copy()
            res["rrf_score"] = round(rrf_map[mem_id], 4)
            fused_results.append(res)

        return fused_results

    def hybrid_search(
        self, 
        db: Session, 
        query: str, 
        limit: int = 5, 
        bank_id: str = "auditmind_org",
        org_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search combining BM25 keyword matching and dense vector similarity."""
        query_builder = db.query(MemoryNode).filter(MemoryNode.bank_id == bank_id)
        if org_id:
            query_builder = query_builder.filter(MemoryNode.organization_id == org_id)

        nodes = query_builder.all()
        if not nodes:
            return []

        query_tokens = set(self.tokenize(query))

        # Compute BM25 scores
        bm25_list = []
        for node in nodes:
            score = self.bm25_score(query_tokens, node)
            if score > 0 or not query_tokens:
                bm25_list.append({
                    "id": node.id,
                    "content": node.content,
                    "category": node.category,
                    "reference_type": node.reference_type,
                    "reference_code": node.reference_code,
                    "year": node.year,
                    "tags": node.tags.split(",") if node.tags else [],
                    "bm25_score": score
                })
        bm25_sorted = sorted(bm25_list, key=lambda x: x["bm25_score"], reverse=True)

        # Compute Dense scores
        dense_list = []
        for node in nodes:
            score = self.vector_dense_score(query_tokens, node)
            if score > 0 or not query_tokens:
                dense_list.append({
                    "id": node.id,
                    "content": node.content,
                    "category": node.category,
                    "reference_type": node.reference_type,
                    "reference_code": node.reference_code,
                    "year": node.year,
                    "tags": node.tags.split(",") if node.tags else [],
                    "dense_score": score
                })
        dense_sorted = sorted(dense_list, key=lambda x: x["dense_score"], reverse=True)

        # Reciprocal Rank Fusion
        return self.reciprocal_rank_fusion(bm25_sorted, dense_sorted, top_k=limit)

hybrid_search_service = HybridSearchService()
