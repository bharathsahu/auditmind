import unittest
from app.services.auth_service import auth_service
from app.services.hybrid_search_service import hybrid_search_service
from app.services.document_processor import document_processor
from app.models.database import MemoryNode

class TestAuditMindBackend(unittest.TestCase):
    def test_01_password_hashing_and_verification(self):
        password = "test_secure_password_2026"
        hashed = auth_service.hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(auth_service.verify_password(password, hashed))
        self.assertFalse(auth_service.verify_password("wrong_password", hashed))

    def test_02_jwt_token_lifecycle(self):
        token_data = {"sub": "qa_auditor", "role": "Lead Auditor", "org_id": 1}
        token = auth_service.create_access_token(token_data)
        self.assertIsNotNone(token)
        
        decoded = auth_service.decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "qa_auditor")
        self.assertEqual(decoded["role"], "Lead Auditor")
        self.assertEqual(decoded["org_id"], 1)

    def test_03_invalid_jwt_token_handling(self):
        self.assertIsNone(auth_service.decode_access_token("invalid.token.signature"))
        self.assertIsNone(auth_service.decode_access_token(""))

    def test_04_document_path_traversal_sanitization(self):
        dangerous_filename = "../../../etc/passwd"
        clean = document_processor.sanitize_filename(dangerous_filename)
        self.assertNotIn("..", clean)
        self.assertEqual(clean, "passwd")

    def test_05_sha256_evidence_hashing(self):
        content = b"Legal Audit Evidence Document Content 2026"
        hash1 = document_processor.compute_sha256(content)
        hash2 = document_processor.compute_sha256(content)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_06_semantic_window_chunking(self):
        sample_text = " ".join([f"word_{i}" for i in range(1000)])
        chunks = document_processor.semantic_chunking(sample_text, chunk_size=500, overlap=50)
        self.assertTrue(len(chunks) > 1)
        self.assertIn("word_0", chunks[0])

    def test_07_bm25_scoring_algorithm(self):
        node = MemoryNode(
            id=101,
            bank_id="auditmind_org",
            content="Transaction approval failure due to API timeout lag.",
            category="Finding History",
            reference_type="Finding",
            reference_code="FND-2026-031",
            tags="finding,high,transaction",
            year=2026
        )
        query_tokens = {"fnd-2026-031", "approval", "transaction"}
        score = hybrid_search_service.bm25_score(query_tokens, node)
        self.assertGreater(score, 15.0)

    def test_08_reciprocal_rank_fusion(self):
        bm25_ranked = [{"id": 1, "code": "FND-001"}, {"id": 2, "code": "FND-002"}]
        dense_ranked = [{"id": 2, "code": "FND-002"}, {"id": 1, "code": "FND-001"}]
        fused = hybrid_search_service.reciprocal_rank_fusion(bm25_ranked, dense_ranked, top_k=2)
        self.assertEqual(len(fused), 2)
        self.assertIn("rrf_score", fused[0])

if __name__ == "__main__":
    unittest.main()
