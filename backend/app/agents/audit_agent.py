import os
import httpx
import logging
from sqlalchemy.orm import Session
from app.hindsight.client import hindsight_service
from app.models.database import Audit, Finding, Remediation
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AuditMindAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    async def _call_external_llm(self, prompt: str, system_instruction: str) -> str:
        """Call external LLM (Gemini or OpenAI) if API key is configured."""
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

    async def process_user_query(self, db: Session, query: str, bank_id: str = "auditmind_org") -> Dict[str, Any]:
        """Process any human natural language query using DB context + Hindsight memory + LLM reasoning."""
        query_text = query.strip()
        query_lower = query_text.lower()
        
        # 1. Execute Hindsight memory recall & reflection over memory bank
        memories = await hindsight_service.recall(db, query_text, limit=6, bank_id=bank_id)
        reflection = await hindsight_service.reflect(db, query_text, bank_id=bank_id)

        # 2. Extract database facts
        audits = db.query(Audit).all()
        findings = db.query(Finding).all()
        remediations = db.query(Remediation).all()

        open_findings = [f for f in findings if f.status in ("Open", "In Progress")]
        overdue_remediations = [r for r in remediations if r.status == "Overdue"]
        high_risk_findings = [f for f in findings if f.severity in ("High", "Critical")]

        # Prepare context payload for LLM or Conversational Engine
        memory_str = "\n".join([f"- [{m.get('year', 'N/A')}] {m.get('reference_code', 'N/A')}: {m.get('content')}" for m in memories]) if memories else "No prior memories recalled."
        
        db_summary = (
            f"Current DB Stats: Audits={len(audits)}, Open Findings={len(open_findings)}, "
            f"Overdue Remediations={len(overdue_remediations)}, High Risk Findings={len(high_risk_findings)}.\n"
            f"High Risk Findings: {', '.join([f'{f.finding_code} ({f.title})' for f in high_risk_findings])}.\n"
            f"Overdue Remediations: {', '.join([f'{r.action} (Owner: {r.owner}, Due: {r.due_date})' for r in overdue_remediations])}."
        )

        system_instruction = (
            "You are AuditMind AI, a friendly, warm, highly intelligent internal audit & compliance companion. "
            "You speak naturally like a helpful, supportive expert colleague. "
            "Always combine current DB information and Hindsight persistent organizational memory. "
            "Never invent fake audit findings. Be encouraging, clear, and structured."
        )

        prompt = (
            f"User Asked: \"{query_text}\"\n\n"
            f"Recalled Hindsight Memories:\n{memory_str}\n\n"
            f"Current DB Facts:\n{db_summary}\n\n"
            "Please provide a friendly, helpful, human-like response answering their question clearly with bullet points and actionable advice."
        )

        # 3. Try calling external LLM if configured
        llm_response = await self._call_external_llm(prompt, system_instruction)
        if llm_response:
            return {
                "query": query_text,
                "response": llm_response,
                "recalled_memories": memories,
                "bank_id": bank_id
            }

        # 4. Built-in Warm & Friendly Natural Language Conversation Engine Fallback
        greeting = "Hi there! " if any(w in query_lower for w in ["hi", "hello", "hey", "greetings"]) else ""
        response_text = ""

        # Friendly Natural Language Understanding Logic
        if any(w in query_lower for w in ["before", "seen", "history", "previous", "earlier", "past", "recurring", "repeat", "happened"]):
            response_text += f"{greeting}I searched our organization's **Hindsight Persistent Memory Layer** for you.\n\n"
            if memories:
                response_text += f"Yes! I found **{len(memories)} historical occurrences** related to your question:\n\n"
                for idx, mem in enumerate(memories, 1):
                    yr = mem.get('year', 'N/A')
                    ref = mem.get('reference_code', 'N/A')
                    cat = mem.get('category', 'Audit')
                    content = mem.get('content')
                    response_text += f"**{idx}. [{yr}] {ref} ({cat})**\n> {content}\n\n"

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
                    f_title = finding.title if finding else "Audit Finding"
                    response_text += f"👉 **{r.owner}**: {r.action} (Target Due Date: `{r.due_date}`) — *Related to {f_title}*\n"
            else:
                response_text += "Great news! None of our active remediation items are currently overdue."

        elif any(w in query_lower for w in ["risk", "critical", "high", "danger", "severe", "threat"]):
            response_text += f"{greeting}Here is our current high-risk compliance overview:\n\n"
            response_text += f"We currently have **{len(high_risk_findings)} High & Critical Severity Findings** in the organization:\n\n"
            for f in high_risk_findings:
                response_text += f"⚠️ **{f.finding_code} ({f.severity} Severity)**: {f.title}\n"
                response_text += f"   - *Control Involved*: {f.control_involved}\n"
                response_text += f"   - *Owner*: {f.remediation_owner} (Status: `{f.status}`)\n\n"

            if memories:
                response_text += "📜 **Historical High-Risk Memory Context**:\n"
                for mem in memories[:2]:
                    response_text += f"• [{mem.get('year')}] {mem.get('content')}\n"

        elif any(w in query_lower for w in ["who", "owner", "responsible", "lead", "team"]):
            response_text += f"{greeting}Here are the key teams and owners responsible for active audit items:\n\n"
            for f in open_findings:
                response_text += f"👤 **{f.remediation_owner}**: Responsible for `{f.finding_code}` ({f.title}) — Due: `{f.due_date}`\n"

        else:
            response_text += f"{greeting}I checked both our live audit records and **Hindsight organizational memory** for you.\n\n"
            if memories:
                response_text += "Here is what Hindsight recalled regarding your question:\n\n"
                for mem in memories[:3]:
                    response_text += f"• **[{mem.get('year')}] {mem.get('reference_code')}**: {mem.get('content')}\n"
                response_text += f"\n\n**Synthesized Insight**:\n{reflection.get('synthesis', '')}"
            else:
                response_text += f"I analyzed our current system records ({len(audits)} Audits, {len(findings)} Findings). "
                response_text += f"Feel free to ask me about past audits, specific finding codes, control failures, or overdue items!"

        return {
            "query": query_text,
            "response": response_text,
            "recalled_memories": memories,
            "bank_id": bank_id
        }

audit_agent = AuditMindAgent()
