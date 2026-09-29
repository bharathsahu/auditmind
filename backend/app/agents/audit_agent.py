import os
import httpx
import json
import logging
import asyncio
from typing import Dict, Any, List, AsyncGenerator
from sqlalchemy.orm import Session
from app.hindsight.client import hindsight_service
from app.models.database import Audit, Finding, Remediation

logger = logging.getLogger(__name__)

class AuditMindAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    async def _call_external_llm(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Call external LLM if configured."""
        if self.gemini_api_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{"text": f"{system_instruction}\n\nUser Question:\n{prompt}"}]
                        }]
                    }
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        return data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                logger.warning(f"Gemini API call error: {e}")

        if self.openai_api_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {self.openai_api_key}"}
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ]
                    }
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        return data['choices'][0]['message']['content']
            except Exception as e:
                logger.warning(f"OpenAI API call error: {e}")

        return None

    def _extract_citations(self, memories: List[Dict[str, Any]], findings: List[Finding]) -> List[Dict[str, str]]:
        """Extract explicit citation references for response grounding."""
        citations = []
        for mem in memories:
            ref_code = mem.get("reference_code") or f"MEM-{mem.get('id')}"
            citations.append({
                "type": mem.get("reference_type", "Memory"),
                "code": ref_code,
                "title": f"[{mem.get('year', 'N/A')}] {mem.get('category')}",
                "snippet": mem.get("content", "")[:120] + "..."
            })
        for f in findings[:3]:
            citations.append({
                "type": "Finding",
                "code": f.finding_code,
                "title": f.title,
                "snippet": f"Severity: {f.severity} | Owner: {f.remediation_owner}"
            })
        return citations

    async def process_user_query(self, db: Session, query: str, bank_id: str = "auditmind_org", org_id: Optional[int] = None) -> Dict[str, Any]:
        """Process natural language query with grounded context & citations."""
        query_text = query.strip()
        query_lower = query_text.lower()

        # 1. Hybrid Memory Recall
        memories = await hindsight_service.recall(db, query_text, limit=6, bank_id=bank_id)
        reflection = await hindsight_service.reflect(db, query_text, bank_id=bank_id)

        # 2. Extract live database context
        findings_query = db.query(Finding)
        audits_query = db.query(Audit)
        remediations_query = db.query(Remediation)

        if org_id:
            findings_query = findings_query.filter(Finding.organization_id == org_id)
            audits_query = audits_query.filter(Audit.organization_id == org_id)
            remediations_query = remediations_query.filter(Remediation.organization_id == org_id)

        audits = audits_query.all()
        findings = findings_query.all()
        remediations = remediations_query.all()

        open_findings = [f for f in findings if f.status in ("Open", "In Progress")]
        overdue_remediations = [r for r in remediations if r.status == "Overdue"]
        high_risk_findings = [f for f in findings if f.severity in ("High", "Critical")]

        # Prepare Citations
        citations = self._extract_citations(memories, high_risk_findings if "risk" in query_lower else open_findings)

        # 3. LLM Prompt Construction
        memory_str = "\n".join([f"- [{m.get('year', 'N/A')}] {m.get('reference_code', 'N/A')}: {m.get('content')}" for m in memories]) if memories else "No prior memories recalled."
        db_summary = (
            f"Current DB Stats: Audits={len(audits)}, Open Findings={len(open_findings)}, "
            f"Overdue Remediations={len(overdue_remediations)}, High Risk Findings={len(high_risk_findings)}.\n"
            f"High Risk Findings: {', '.join([f'{f.finding_code} ({f.title})' for f in high_risk_findings])}."
        )

        system_instruction = (
            "You are AuditMind AI, an intelligent internal audit & compliance companion. "
            "Always ground your response strictly in the provided database facts and Hindsight persistent organizational memory. "
            "Never invent fake audit findings. Provide source citations using bracket format, e.g. [Ref: FND-2026-031]."
        )

        prompt = f"User Question: \"{query_text}\"\n\nRecalled Memories:\n{memory_str}\n\nDB Facts:\n{db_summary}"

        llm_response = await self._call_external_llm(prompt, system_instruction)
        if llm_response:
            return {
                "query": query_text,
                "response": llm_response,
                "citations": citations,
                "recalled_memories": memories,
                "bank_id": bank_id
            }

        # 4. Fallback Rule-Based Conversational Engine
        greeting = "Hi there! " if any(w in query_lower for w in ["hi", "hello", "hey", "greetings"]) else ""
        response_text = ""

        if any(w in query_lower for w in ["before", "seen", "history", "previous", "earlier", "past", "recurring", "repeat", "happened"]):
            response_text += f"{greeting}I searched our organization's **Hindsight Persistent Memory Layer** for you.\n\n"
            if memories:
                response_text += f"Yes! I found **{len(memories)} historical occurrences** related to your query:\n\n"
                for idx, mem in enumerate(memories, 1):
                    yr = mem.get('year', 'N/A')
                    ref = mem.get('reference_code', 'N/A')
                    cat = mem.get('category', 'Audit')
                    content = mem.get('content')
                    response_text += f"**{idx}. [{yr}] {ref} ({cat})** [Ref: {ref}]\n> {content}\n\n"

                response_text += "💡 **Pattern & Insights**:\n"
                response_text += "Historically, transaction approval issues recurred across 2024, 2025, and 2026 due to emergency single-approver overrides and API sync lags. Corrective action requires enforcing hard-stop automated dual authorization."
            else:
                response_text += "I checked our Hindsight memory bank, and there are no recorded previous occurrences matching this specific issue."

        elif any(w in query_lower for w in ["overdue", "late", "pending", "unresolved", "delay", "remediation"]):
            response_text += f"{greeting}Here is the latest update on our remediation actions:\n\n"
            response_text += f"• **Overdue Remediations**: `{len(overdue_remediations)}` action(s)\n"
            response_text += f"• **Open Audit Findings**: `{len(open_findings)}` finding(s)\n\n"

            if overdue_remediations:
                response_text += "**Action Items Requiring Immediate Attention:**\n"
                for r in overdue_remediations:
                    finding = db.query(Finding).filter(Finding.id == r.finding_id).first()
                    f_code = finding.finding_code if finding else "FND-000"
                    f_title = finding.title if finding else "Audit Finding"
                    response_text += f"👉 **{r.owner}**: {r.action} (Target Due Date: `{r.due_date}`) — *Related to {f_title}* [Ref: {f_code}]\n"
            else:
                response_text += "Great news! None of our active remediation items are currently overdue."

        elif any(w in query_lower for w in ["risk", "critical", "high", "danger", "severe", "threat"]):
            response_text += f"{greeting}Here is our current high-risk compliance overview:\n\n"
            response_text += f"We currently have **{len(high_risk_findings)} High & Critical Severity Findings**:\n\n"
            for f in high_risk_findings:
                response_text += f"⚠️ **{f.finding_code} ({f.severity} Severity)** [Ref: {f.finding_code}]: {f.title}\n"
                response_text += f"   - *Control Involved*: {f.control_involved}\n"
                response_text += f"   - *Owner*: {f.remediation_owner} (Status: `{f.status}`)\n\n"

            if memories:
                response_text += "📜 **Historical High-Risk Context**:\n"
                for mem in memories[:2]:
                    response_text += f"• [{mem.get('year')}] {mem.get('content')} [Ref: {mem.get('reference_code')}]\n"

        else:
            response_text += f"{greeting}I analyzed our database records ({len(audits)} Audits, {len(findings)} Findings) and **Hindsight organizational memory**.\n\n"
            if memories:
                response_text += "Recalled evidence:\n\n"
                for mem in memories[:3]:
                    response_text += f"• **[{mem.get('year')}] {mem.get('reference_code')}**: {mem.get('content')} [Ref: {mem.get('reference_code')}]\n"
                response_text += f"\n\n**Synthesized Insight**:\n{reflection.get('synthesis', '')}"
            else:
                response_text += f"Feel free to ask me about past audits, finding codes, control failures, or overdue remediations!"

        return {
            "query": query_text,
            "response": response_text,
            "citations": citations,
            "recalled_memories": memories,
            "bank_id": bank_id
        }

    async def stream_user_query(self, db: Session, query: str, bank_id: str = "auditmind_org", org_id: Optional[int] = None) -> AsyncGenerator[str, None]:
        """Stream AI answer tokens in Server-Sent Events (SSE) format."""
        result = await self.process_user_query(db, query, bank_id=bank_id, org_id=org_id)
        full_text = result.get("response", "")
        citations = result.get("citations", [])

        # Stream text token chunks
        words = full_text.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            event_data = json.dumps({"token": chunk, "type": "content"})
            yield f"data: {event_data}\n\n"
            await asyncio.sleep(0.02)

        # Stream final citations event
        citation_event = json.dumps({"citations": citations, "type": "citations_done"})
        yield f"data: {citation_event}\n\n"

audit_agent = AuditMindAgent()
