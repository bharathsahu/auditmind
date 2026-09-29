import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import MemoryNode

logger = logging.getLogger(__name__)

class HindsightMemoryService:
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = os.getenv("HINDSIGHT_URL", base_url)
        self.default_bank_id = os.getenv("HINDSIGHT_BANK_ID", "auditmind_org")

    async def retain(self, db: Session, content: str, category: str = "Audit History", 
                     reference_type: str = "General", reference_code: str = None, 
                     tags: List[str] = None, year: int = 2026, bank_id: str = None) -> Dict[str, Any]:
        """Store useful audit knowledge into persistent Hindsight memory."""
        target_bank = bank_id or self.default_bank_id
        tag_str = ",".join(tags) if tags else ""

        # 1. Try sending to external Hindsight Server API if available
        remote_success = False
        try:
            async with httpx.AsyncClient(timeout=0.5) as client:
                res = await client.post(
                    f"{self.base_url}/v1/banks/{target_bank}/retain",
                    json={"content": content, "metadata": {"category": category, "ref": reference_code, "tags": tag_str}}
                )
                if res.status_code in (200, 201):
                    remote_success = True
                    logger.info(f"Retained memory in remote Hindsight server: {target_bank}")
        except Exception:
            pass

        # 2. Store in local MemoryNode persistent database
        node = MemoryNode(
            bank_id=target_bank,
            content=content,
            category=category,
            reference_type=reference_type,
            reference_code=reference_code,
            tags=tag_str,
            year=year
        )
        db.add(node)
        db.commit()
        db.refresh(node)

        return {
            "status": "success",
            "memory_id": node.id,
            "bank_id": target_bank,
            "remote_synced": remote_success,
            "content": content
        }

    async def recall(self, db: Session, query: str, limit: int = 5, bank_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve relevant historical audit memories for a query."""
        target_bank = bank_id or self.default_bank_id
        
        # 1. Check remote Hindsight server
        try:
            async with httpx.AsyncClient(timeout=0.5) as client:
                res = await client.post(
                    f"{self.base_url}/v1/banks/{target_bank}/recall",
                    json={"query": query, "top_k": limit}
                )
                if res.status_code == 200:
                    data = res.json()
                    if "results" in data and len(data["results"]) > 0:
                        return data["results"]
        except Exception:
            pass

        # 2. Embedded Hybrid Recall fallback over MemoryNode table
        nodes = db.query(MemoryNode).filter(MemoryNode.bank_id == target_bank).all()
        query_words = set(query.lower().split())
        
        scored_memories = []
        for node in nodes:
            content_lower = node.content.lower()
            tags_lower = node.tags.lower() if node.tags else ""
            category_lower = node.category.lower()
            
            # Simple keyword frequency + semantic relevance heuristic
            score = 0
            for word in query_words:
                if len(word) > 2:
                    if word in content_lower:
                        score += 3
                    if word in tags_lower:
                        score += 4
                    if word in category_lower:
                        score += 2

            if score > 0 or len(query_words) == 0:
                scored_memories.append({
                    "id": node.id,
                    "content": node.content,
                    "category": node.category,
                    "reference_type": node.reference_type,
                    "reference_code": node.reference_code,
                    "year": node.year,
                    "tags": node.tags.split(",") if node.tags else [],
                    "relevance_score": score
                })

        # Sort by relevance score desc
        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_memories[:limit]

    async def reflect(self, db: Session, query: str, bank_id: str = None) -> Dict[str, Any]:
        """Perform deeper reasoning over historical memories to detect patterns or summarize findings."""
        recalled = await self.recall(db, query, limit=7, bank_id=bank_id)
        
        if not recalled:
            return {
                "query": query,
                "synthesis": "No relevant historical audit memories found in Hindsight memory bank.",
                "memories_used": []
            }

        # Build reflective summary from memories
        memory_contexts = [f"[{m.get('year', 'N/A')}] ({m.get('category')} - {m.get('reference_code')}): {m.get('content')}" for m in recalled]
        
        # Synthetic reasoning breakdown
        synthesis = f"Based on {len(recalled)} recalled historical memories:\n\n"
        synthesis += "\n".join([f"- {ctx}" for ctx in memory_contexts])
        
        return {
            "query": query,
            "synthesis": synthesis,
            "memories_used": recalled
        }

hindsight_service = HindsightMemoryService()
