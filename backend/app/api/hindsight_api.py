from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.database import get_db, MemoryNode, Finding, User
from app.models.schemas import MemoryNodeResponse
from app.hindsight.client import hindsight_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/hindsight", tags=["Hindsight Memory Explorer"])

@router.get("/memories", response_model=List[MemoryNodeResponse])
def get_memories(
    bank_id: str = "auditmind_org", 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == bank_id).order_by(MemoryNode.id.desc()).all()
    return memories

@router.get("/categories")
def get_memory_categories(
    bank_id: str = "auditmind_org", 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
def get_memory_graph(
    bank_id: str = "auditmind_org", 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate interactive visual network graph nodes, links & lineage chains for Memory Explorer."""
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == bank_id).all()
    findings = db.query(Finding).all()
    
    nodes = []
    links = []
    
    # 1. Map Memory Nodes
    for m in memories:
        nodes.append({
            "id": f"mem-{m.id}",
            "label": m.reference_code or f"Mem #{m.id}",
            "category": m.category,
            "year": m.year or 2026,
            "reference_type": m.reference_type,
            "reference_code": m.reference_code,
            "content": m.content,
            "tags": m.tags.split(",") if m.tags else []
        })

    # 2. Build Edge Links between related nodes
    for i, m1 in enumerate(memories):
        for j, m2 in enumerate(memories):
            if i < j:
                m1_tags = set(m1.tags.split(",")) if m1.tags else set()
                m2_tags = set(m2.tags.split(",")) if m2.tags else set()
                shared = m1_tags.intersection(m2_tags)
                
                # If they share tags or reference codes across years
                if shared:
                    rel_name = list(shared)[0]
                    relation_type = "lineage" if (m1.year and m2.year and m1.year != m2.year) else "related"
                    links.append({
                        "source": f"mem-{m1.id}",
                        "target": f"mem-{m2.id}",
                        "relation": rel_name,
                        "type": relation_type
                    })

    # 3. Detect Lineage Chains (e.g. 2024 -> 2025 -> 2026)
    lineage_chains = []
    controls_map = {}
    for f in findings:
        ctrl = f.control_involved or "General Control"
        if ctrl not in controls_map:
            controls_map[ctrl] = []
        controls_map[ctrl].append(f)

    for ctrl, items in controls_map.items():
        if len(items) >= 2:
            chain_nodes = [
                {
                    "finding_code": item.finding_code,
                    "title": item.title,
                    "severity": item.severity,
                    "year": item.fiscal_year or 2026
                }
                for item in sorted(items, key=lambda x: x.fiscal_year or 2026)
            ]
            lineage_chains.append({
                "control": ctrl,
                "chain": chain_nodes
            })

    return {
        "bank_id": bank_id,
        "total_nodes": len(nodes),
        "total_links": len(links),
        "nodes": nodes,
        "links": links,
        "lineage_chains": lineage_chains
    }

@router.post("/recall")
async def raw_recall(
    payload: dict, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = payload.get("query", "")
    bank_id = payload.get("bank_id", "auditmind_org")
    results = await hindsight_service.recall(db, query, limit=10, bank_id=bank_id)
    return {
        "query": query,
        "results": results
    }

@router.post("/reflect")
async def raw_reflect(
    payload: dict, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = payload.get("query", "")
    bank_id = payload.get("bank_id", "auditmind_org")
    result = await hindsight_service.reflect(db, query, bank_id=bank_id)
    return result
