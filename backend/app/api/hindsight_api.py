from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, MemoryNode
from app.models.schemas import MemoryNodeResponse
from app.hindsight.client import hindsight_service

router = APIRouter(prefix="/api/hindsight", tags=["Hindsight Memory Explorer"])

@router.get("/memories", response_model=List[MemoryNodeResponse])
def get_memories(bank_id: str = "auditmind_org", db: Session = Depends(get_db)):
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == bank_id).order_by(MemoryNode.id.desc()).all()
    return memories

@router.get("/categories")
def get_memory_categories(bank_id: str = "auditmind_org", db: Session = Depends(get_db)):
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == bank_id).all()
    categories = {}
    for m in memories:
        cat = m.category or "General"
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "bank_id": bank_id,
        "total_memories": len(memories),
        "categories": categories
    }

@router.get("/graph")
def get_memory_graph(bank_id: str = "auditmind_org", db: Session = Depends(get_db)):
    """Generate visual relationship graph nodes & links for Memory Explorer UI."""
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == bank_id).all()
    
    nodes = []
    links = []
    
    for m in memories:
        nodes.append({
            "id": f"mem-{m.id}",
            "label": m.reference_code or f"Mem #{m.id}",
            "category": m.category,
            "year": m.year or 2026,
            "content": m.content[:100] + "..."
        })

    # Connect nodes with matching control or recurring tags
    for i, m1 in enumerate(memories):
        for j, m2 in enumerate(memories):
            if i < j:
                # If both have same reference code pattern or tags
                m1_tags = set(m1.tags.split(",")) if m1.tags else set()
                m2_tags = set(m2.tags.split(",")) if m2.tags else set()
                shared = m1_tags.intersection(m2_tags)
                if len(shared) > 0 and "auditmind_org" in m1.bank_id:
                    links.append({
                        "source": f"mem-{m1.id}",
                        "target": f"mem-{m2.id}",
                        "relation": list(shared)[0]
                    })

    return {
        "nodes": nodes,
        "links": links
    }

@router.post("/recall")
async def raw_recall(payload: dict, db: Session = Depends(get_db)):
    query = payload.get("query", "")
    bank_id = payload.get("bank_id", "auditmind_org")
    results = await hindsight_service.recall(db, query, limit=10, bank_id=bank_id)
    return {
        "query": query,
        "results": results
    }

@router.post("/reflect")
async def raw_reflect(payload: dict, db: Session = Depends(get_db)):
    query = payload.get("query", "")
    bank_id = payload.get("bank_id", "auditmind_org")
    result = await hindsight_service.reflect(db, query, bank_id=bank_id)
    return result
