from app.services.hybrid_search_service import hybrid_search_service
from app.models.database import MemoryNode

def test_bm25_scoring(db_session):
    node = MemoryNode(
        bank_id="auditmind_org",
        content="Transaction approval failure due to API timeout.",
        category="Finding History",
        reference_type="Finding",
        reference_code="FND-2026-031",
        tags="finding,high,transaction",
        year=2026
    )
    db_session.add(node)
    db_session.commit()

    tokens = {"fnd-2026-031", "approval", "transaction"}
    score = hybrid_search_service.bm25_score(tokens, node)
    assert score > 10.0

def test_hybrid_search_rrf(db_session):
    results = hybrid_search_service.hybrid_search(db_session, query="transaction approval", limit=3)
    assert isinstance(results, list)
