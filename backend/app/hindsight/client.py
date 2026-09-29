import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import MemoryNode
from app.services.hybrid_search_service import hybrid_search_service

logger = logging.getLogger(__name__)

class HindsightMemoryService:
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = os.getenv("HINDSIGHT_URL", base_url)
        self.default_bank_id = os.getenv("HINDSIGHT_BANK_ID", "auditmind_org")

    def _resolve_bank_id(self, bank_id: Optional[str] = None, org_id: Optional[int] = None) -> str:
        """Resolve tenant-isolated Hindsight memory bank identifier."""
        if bank_id and bank_id != "auditmind_org":
            return bank_id
        if org_id:
            return f"auditmind_org_{org_id}"
        return self.default_bank_id

    async def retain(
        self, 
        db: Session, 
        content: str, 
        category: str = "Audit History", 
        reference_type: str = "General", 
        reference_code: str = None, 
        tags: List[str] = None, 
        year: int = 2026, 
        bank_id: str = None,
        org_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Store audit knowledge into tenant-isolated Hindsight memory."""
        target_bank = self._resolve_bank_id(bank_id, org_id)
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
            year=year,
            organization_id=org_id
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

    async def recall(
        self, 
        db: Session, 
        query: str, 
        limit: int = 5, 
        bank_id: str = None,
        org_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve historical memories from tenant-isolated Hindsight bank."""
        target_bank = self._resolve_bank_id(bank_id, org_id)
        
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

        # 2. Fallback to Local Hybrid RRF Search
        return hybrid_search_service.hybrid_search(db, query, limit=limit, bank_id=target_bank, org_id=org_id)

    async def reflect(
        self, 
        db: Session, 
        query: str, 
        bank_id: str = None,
        org_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Perform deeper reasoning over tenant-isolated memories."""
        target_bank = self._resolve_bank_id(bank_id, org_id)
        recalled = await self.recall(db, query, limit=7, bank_id=target_bank, org_id=org_id)
        
        if not recalled:
            return {
                "query": query,
                "synthesis": "No relevant historical audit memories found in tenant memory bank.",
                "memories_used": []
            }

        memory_contexts = [f"[{m.get('year', 'N/A')}] ({m.get('category')} - {m.get('reference_code')}): {m.get('content')}" for m in recalled]
        synthesis = f"Based on {len(recalled)} recalled historical memories:\n\n" + "\n".join([f"- {ctx}" for ctx in memory_contexts])
        
        return {
            "query": query,
            "synthesis": synthesis,
            "memories_used": recalled
        }

hindsight_service = HindsightMemoryService()
