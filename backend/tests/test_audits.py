def test_get_audits(client):
    response = client.get("/api/audits")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_audit(client):
    payload = {
        "name": "2026 IT Risk Assessment Test",
        "department": "IT Security",
        "audit_type": "IT Audit",
        "risk_level": "High",
        "status": "In Progress",
        "start_date": "2026-01-10",
        "end_date": "2026-02-28",
        "auditor": "Senior Auditor",
        "description": "Test IT Risk audit scope."
    }
    response = client.post("/api/audits", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert "audit_code" in data
