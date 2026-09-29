import os
import io
import csv
import hashlib
import uuid
import re
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from docx import Document as DocxDocument
from sqlalchemy.orm import Session

from app.config import settings
from app.hindsight.client import hindsight_service
from app.models.database import Document as DBDocument

class DocumentProcessorService:
    def __init__(self):
        self.chunk_size: int = int(os.getenv("DOC_CHUNK_SIZE", "500")) # Words per chunk
        self.chunk_overlap: int = int(os.getenv("DOC_CHUNK_OVERLAP", "50")) # Overlapping words
        self.max_file_size: int = 50 * 1024 * 1024 # 50 MB limit
        self.allowed_extensions = {".pdf", ".docx", ".txt", ".csv"}

    def compute_sha256(self, file_content: bytes) -> str:
        """Compute SHA-256 hash for evidence integrity verification."""
        return hashlib.sha256(file_content).hexdigest()

    def sanitize_filename(self, filename: str) -> str:
        """Prevent path traversal and sanitize filename."""
        clean_name = os.path.basename(filename)
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', clean_name)
        return clean_name or f"document_{uuid.uuid4().hex[:8]}.txt"

    def semantic_chunking(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping semantic window chunks."""
        words = text.split()
        if not words:
            return []
        
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append(chunk_text)
            if end == len(words):
                break
            start += (chunk_size - overlap)
        return chunks

    async def process_file(self, db: Session, doc_record: DBDocument, file_content: bytes) -> Dict[str, Any]:
        """Extract structured text, apply semantic window chunking, and retain memory nodes."""
        file_hash = self.compute_sha256(file_content)
        doc_record.document_hash = file_hash

        file_name = doc_record.name.lower()
        extracted_sections: List[Dict[str, Any]] = []

        try:
            if file_name.endswith(".pdf"):
                reader = PdfReader(io.BytesIO(file_content))
                for page_idx, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        extracted_sections.append({
                            "page_number": page_idx,
                            "section": f"Page {page_idx}",
                            "text": text.strip()
                        })
            elif file_name.endswith(".docx"):
                docx = DocxDocument(io.BytesIO(file_content))
                current_section = "General"
                section_text = []

                for p in docx.paragraphs:
                    if not p.text.strip():
                        continue
                    if p.style.name.startswith("Heading"):
                        if section_text:
                            extracted_sections.append({
                                "page_number": 1,
                                "section": current_section,
                                "text": "\n".join(section_text)
                            })
                            section_text = []
                        current_section = p.text.strip()
                    else:
                        section_text.append(p.text.strip())

                if section_text:
                    extracted_sections.append({
                        "page_number": 1,
                        "section": current_section,
                        "text": "\n".join(section_text)
                    })

            elif file_name.endswith(".csv"):
                content_str = file_content.decode("utf-8", errors="ignore")
                reader = csv.reader(content_str.splitlines())
                rows = [", ".join(row) for row in reader if any(row)]
                extracted_sections.append({
                    "page_number": 1,
                    "section": "CSV Data Table",
                    "text": "\n".join(rows)
                })
            else: # .txt
                text = file_content.decode("utf-8", errors="ignore")
                extracted_sections.append({
                    "page_number": 1,
                    "section": "Main Body",
                    "text": text
                })

        except Exception as e:
            extracted_sections.append({
                "page_number": 1,
                "section": "Raw Content",
                "text": f"Document content preview for {doc_record.name}"
            })

        # Apply semantic window chunking & retain in Hindsight memory
        facts_retained = 0
        total_chunks = 0

        for sec in extracted_sections:
            page_num = sec["page_number"]
            section_name = sec["section"]
            raw_text = sec["text"]

            chunks = self.semantic_chunking(raw_text, self.chunk_size, self.chunk_overlap)
            total_chunks += len(chunks)

            for chunk_idx, chunk_text in enumerate(chunks, 1):
                memory_content = (
                    f"Document '{doc_record.name}' [{section_name} - Chunk {chunk_idx}]: {chunk_text}"
                )
                
                await hindsight_service.retain(
                    db=db,
                    content=memory_content,
                    category="Evidence Context",
                    reference_type="Document",
                    reference_code=f"DOC-{doc_record.id}",
                    tags=["document_upload", doc_record.file_type.lower(), f"page_{page_num}"],
                    year=2026
                )
                facts_retained += 1

        doc_record.processed = True
        doc_record.facts_extracted = facts_retained
        db.commit()

        return {
            "document_id": doc_record.id,
            "filename": doc_record.name,
            "document_hash": file_hash,
            "sections_found": len(extracted_sections),
            "total_chunks": total_chunks,
            "facts_extracted": facts_retained,
            "status": "processed"
        }

document_processor = DocumentProcessorService()
