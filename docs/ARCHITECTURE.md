# AuditMind — Production Architecture Specifications (Phase 0)

> **Document Status**: Architectural Specification Baseline  
> **System Name**: AuditMind (AI Compliance & Audit Organizational Memory Platform)  

---

## 1. System Topology & Data Flow

```mermaid
flowchart TD
    subgraph ClientLayer ["Client Layer (Frontend)"]
        UI["React 18 + Vite App"]
        Router["React Router v6"]
        AxiosClient["API Client / Axios Interceptor"]
        StateContext["Auth & Tenant Context"]
    end

    subgraph APILayer ["API & Gateways (Backend FastAPI)"]
        CORSMiddleware["CORS Middleware"]
        AuthGuard["JWT & RBAC Auth Middleware"]
        AuditRouter["Audit & Findings API"]
        DocRouter["Document Ingestion API"]
        AIRouter["Streaming AI Chat API"]
        ReportRouter["Report Generation API"]
    end

    subgraph ServiceLayer ["Service & Business Logic"]
        AuditService["Audit & Finding Service"]
        DocProcessor["Semantic Window Chunking Engine"]
        AgentEngine["AuditMind AI Agent Engine"]
        HindsightService["Hindsight Hybrid Memory Manager"]
    end

    subgraph MemoryLayer ["Vector & Memory Layer"]
        RemoteHindsight["Hindsight Remote Server (Vectorize)"]
        LocalChromaDB["Local ChromaDB / Dense Vector Store"]
        EmbeddingEngine["Sentence Transformers (all-MiniLM-L6-v2)"]
    end

    subgraph StorageLayer ["Persistence Layer"]
        RelationalDB[("PostgreSQL / SQLite\n(Audits, Findings, Actions, Users, AuditLogs)")]
        DocVault["Document Store / Uploads"]
    end

    UI --> AxiosClient
    AxiosClient --> CORSMiddleware
    CORSMiddleware --> AuthGuard

    AuthGuard --> AuditRouter
    AuthGuard --> DocRouter
    AuthGuard --> AIRouter
    AuthGuard --> ReportRouter

    AuditRouter --> AuditService
    DocRouter --> DocProcessor
    AIRouter --> AgentEngine

    AuditService --> RelationalDB
    DocProcessor --> DocVault
    DocProcessor --> HindsightService

    AgentEngine --> HindsightService
    AgentEngine --> RelationalDB

    HindsightService <--> RemoteHindsight
    HindsightService <--> LocalChromaDB
    LocalChromaDB <--> EmbeddingEngine
```

---

## 2. Layered Backend Architecture

To ensure maintainability and testability, the backend is organized into explicit domain layers:

```text
HTTP Request
    │
    ▼
[ API Controller / Router ]   <── Handles HTTP status codes, request schemas
    │
    ▼
[ Service Layer ]              <── Executes business rules, orchestration, AI prompt formatting
    │
    ▼
[ Repository Layer ]           <── Encapsulates database queries & persistence
    │
    ▼
[ Data Storage / ORM ]        <── SQLAlchemy models & PostgreSQL/SQLite DB
```

---

## 3. Persistent Data Model Specifications

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ DEPARTMENTS : has
    ORGANIZATIONS ||--o{ USERS : employs
    DEPARTMENTS ||--o{ AUDITS : contains
    USERS ||--o{ AUDITS : leads
    AUDITS ||--|{ FINDINGS : contains
    FINDINGS ||--|{ REMEDIATIONS : requires
    FINDINGS ||--o{ MEMORY_NODES : linked_to
    DOCUMENTS ||--o{ MEMORY_NODES : extracts
    USERS ||--o{ AUDIT_LOGS : generates

    USERS {
        int id PK
        string email UK
        string username UK
        string password_hash
        string full_name
        string role
        int organization_id FK
        boolean is_active
        datetime created_at
    }

    ORGANIZATIONS {
        int id PK
        string name UK
        string code UK
        datetime created_at
    }

    DEPARTMENTS {
        int id PK
        int organization_id FK
        string name
    }

    AUDITS {
        int id PK
        string audit_code UK
        int organization_id FK
        string name
        string department
        string audit_type
        string risk_level
        string status
        int fiscal_year
        date start_date
        date end_date
        string auditor
    }

    FINDINGS {
        int id PK
        string finding_code UK
        int audit_id FK
        string title
        string description
        string severity
        string control_involved
        string root_cause
        string business_impact
        string recommendation
        string remediation_owner
        date due_date
        string status
        string evidence
        int fiscal_year
    }

    REMEDIATIONS {
        int id PK
        int finding_id FK
        string action
        string owner
        string status
        date due_date
        date completion_date
        string evidence
        text comments
    }

    MEMORY_NODES {
        int id PK
        string bank_id
        int organization_id FK
        text content
        string category
        string reference_type
        string reference_code
        string tags
        int year
        string vector_id
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        int organization_id FK
        string action_type
        string entity_name
        string entity_id
        text details
        string ip_address
        datetime timestamp
    }
```

---

## 4. Hybrid Search & Memory Layer Architecture

```mermaid
flowchart TD
    Query["User Search / Recall Query"] --> Splitter{"Search Router"}
    
    Splitter --> BM25["BM25 Exact Keyword Search\n(Finding Codes, Control Numbers, Tags)"]
    Splitter --> DenseVector["Dense Vector Semantic Search\n(ChromaDB / Hindsight Memory Bank)"]
    
    BM25 --> Ranker["Reciprocal Rank Fusion (RRF)"]
    DenseVector --> Ranker
    
    Ranker --> TopK["Top-K Grounded Context Chunks"]
    TopK --> LLM["LLM Reasoner (Gemini / OpenAI / Ollama)"]
    LLM --> Answer["Grounded Response + Source Citations"]
```

---

## 5. Security & Isolation Model

1. **Authentication**: OAuth2 Password Flow + JWT Bearer Tokens with HS256 / RS256 signatures.
2. **Authorization**: Dependency-injected role checking (`@require_roles(["Admin", "Lead Auditor"])`).
3. **Data Isolation**: All queries enforced with `organization_id` filter (Multi-tenant context).
4. **Audit Immutability**: `AuditLog` records append-only; standard users cannot modify or purge logs.
