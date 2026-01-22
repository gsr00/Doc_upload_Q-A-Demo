

### Architecture — High-Level Overview

This application follows a layered architecture with explicit boundaries between orchestration, core services, and external integrations. The goal is to keep the system easy to reason about, test, and explain, while limiting the impact of external dependencies.


### UI / Controller Layer

Responsibilities:
FastAPI endpoints
Input validation
Request orchestration

The controller layer does not contain business logic. Its role is to validate inputs, route requests to the appropriate services, and shape responses.

### Service Layer

Responsibilities:

Document parsing and temporary storage
Text normalisation and chunking
Embedding generation
Vector search
Document rewrite and document-based Q&A logic

Each service has a single, well-defined responsibility and can be reasoned about independently.

### Integration Boundaries (Demarcation)

External systems are accessed only through explicit boundary modules:
llm_gateway.py
The only place in the system that calls the LLM API.
vector_store.py
The only place in the system that interacts with Pinecone.

This separation is intentional. It reduces coupling, simplifies testing, and limits the blast radius if an external dependency changes or fails.

### RAG and LLM Approach — High-Level Flow

A DOCX file is uploaded and parsed locally.
The extracted text is normalised and chunked into clause-sized units.
Each chunk is embedded and stored in Pinecone with associated metadata.

No LLM is involved during ingestion.

### Document Search / Q&A

The user query is embedded using the same embedding model as the documents.
Semantic search retrieves the most relevant chunks from the vector store.
Results are ranked by similarity score and returned with text excerpts.
Only when relevant evidence exists does the system call the LLM.
Any generated answer is constrained to the retrieved text and includes citations.

If the similarity score falls below a minimum threshold, the system refuses to answer rather than hallucinate.

### Key Decisions and Trade-offs

### LLM Usage
Used only where language generation is required.
Never used for document parsing, searching, or formatting.
All generation is gated by retrieval quality.

This ensures the system remains explainable and avoids ungrounded answers.

### Embeddings

A single embedding model is used consistently for both documents and queries.
Chunking occurs before embedding to preserve clause-level retrieval.

### Vector Database

Pinecone is used to model a production-style vector store.
Chunk text is stored as metadata to allow evidence display without maintaining a second datastore.

### Prompt and Context Management

System prompts are explicit and restrictive.
For document-based Q&A, the LLM is instructed to answer only from the provided sources.

If the information is not present in the retrieved text, the model must say so.

### Guardrails and Safety

File type validation (DOCX only)
Input length limits for queries and notes
Minimum similarity threshold for document-based answers
No document content is logged
Temporary files are deleted after processing
Requests are tagged with IDs for traceability without leaking content
The goal is not to be “clever”, but to be predictable and defensible, particularly in a legal context.

### Engineering Standards Followed

Clear separation of responsibilities
Explicit service boundaries
Environment-based configuration
Deterministic document parsing and document writing (no AI involved)
Manual smoke tests for critical paths (ingest, search, rewrite)

### Considered but Deliberately Skipped (MVP)

Full authentication and authorisation
Automated test suite and CI
Async or background ingestion
Formal evaluation metrics (precision/recall)
Persistent document management UI

These were consciously deferred to keep the focus on core architecture and explainability.

### Smoke Tests

Manual smoke tests are provided under tests/ to validate key behaviour:
Pinecone connectivity and vector round-trip
Document ingest and chunking
Semantic search retrieval
Grounded document Q&A with citations

These tests were used throughout development to validate each architectural layer independently.

### Closing Notes

This system is intentionally small, but architected to make trade-offs, failure modes, and AI behaviour explicit.