# Daily Log

Quick notes tracking daily progress, changes, and learnings.

---

## Log Template

```markdown
## YYYY-MM-DD - Day X: [Short Title]

- **Done**: What was built or changed.
- **Explored / Tried**: What was explored and digged further into to learn.
- **Learned / Notes**: Technical takeaways, bugs, or quirks.
- **Keep in mind for tomorrow (Optional)**: Anything specific to explore or keep in mind while planning tomorrow.
```

---


## 2026-07-19 - Day 5: Project Reorganization & HITL Interactions

- **Done**: 
  - Restructured the project directory to separate exploratory work (`try.ipynb`) from core application code (`src/agentic`).
  - Implemented Human-in-the-Loop (HITL) interactions for the console.
  - Added custom Tranformers to stream tool running status.
  - Fixed relative Python import paths for Jupyter notebooks.
  - Initialized project `README.md`.
- **Explored / Tried**:
  - Debugging LangChain stream events (StreamWriter) rendering inside Jupyter notebook.
  - Custom Projections using Transformers
  - Automating the daily git log updates workflow.
- **Learned / Notes**:
  - How relative imports work when reffering between ipynb and py files
  - Need for Transformers, Projections
  - stream v2 vs stream_events v3
  - Different stream modes
- **Keep in mind for tomorrow (Optional)**: 
  - whenever got a chance explore stream_writer more
  - explore streaming possibilities more

## 2026-07-20 - Day 6: Persistent Memory & Context Trimming

- **Done**: 
  - Implemented persistent short-term memory using `SqliteSaver`.
  - Implemented persistent long-term memory replacing the in-memory dictionary with `SqliteStore`.
  - Added a custom `before_model` middleware to trim old messages, limiting token usage and preventing context overflow.
  - Updated `pyproject.toml` dependencies with `langgraph-checkpoint-sqlite`.
  - Updated `.gitignore` to avoid committing SQLite database files (`checkpoint.db`, `store.db`).
- **Explored / Tried**:
  - Investigated custom State and Context usage in LangGraph (`notebooks/context.ipynb`).
  - Experimented with the persistent SQLite checkpointer and store implementations within Jupyter notebooks.
- **Learned / Notes**:
  - Transitioning from in-memory to SQLite-based persistence in LangGraph is straightforward but requires managing connection threading (`check_same_thread=False`).
  - State and Context serve different purposes in LangGraph; understanding when to update which is crucial for complex agent workflows.
  - Unbounded message history quickly eats up context windows; implementing message trimming middleware before the model call is an effective safeguard.
- **Keep in mind for tomorrow (Optional)**: 
  - Explore and experiment more on Context, State, Store.
  - Observe the CRUD on all three when revisiting these on Langgraph 

---

## 2026-07-21 - Day 7: Structured Tool Output & Input Guardrails

- **Done**: 
  - Enhanced `summarize_notes` tool to use an internal LLM agent with a Pydantic `NoteSummary` schema to generate structured summaries (`topic`, `key_points`, `overall_summary`).
  - Added `block_profanity` `@before_agent` middleware as a deterministic guardrail blocking banned keywords, jailbreak attempts, and prompt injection attacks with `jump_to="end"`.
  - Integrated `PIIMiddleware` to redact email addresses from incoming inputs.
  - Created `notebooks/structured_output.ipynb` to experiment with structured LLM responses.
- **Explored / Tried**:
  - Sub-agent creation inside custom tool calls to enforce structured data schemas.
  - Input sanitization and middleware routing in LangGraph (`PIIMiddleware` and `@before_agent` guardrails).
- **Learned / Notes**:
  - Running a sub-agent within a tool function allows returning typed structured dicts to the main agent instead of unstructured plain text.
  - `@before_agent` middleware can intercept human messages and short-circuit execution via `jump_to="end"`, providing lightweight prompt safety without LLM overhead.


## 2026-07-23 - Day 8: Agentic RAG over LangChain Docs

- **Done**: 
  - Built a document ingestion script (`src/RAG/index.py`) to scrape LangChain documentation, split text with `RecursiveCharacterTextSplitter`, and generate embeddings using `OllamaEmbeddings` (`qwen3-embedding:0.6b`).
  - Stored the generated vectors in a local Qdrant database (`QdrantVectorStore`).
  - Created a RAG-enabled agent (`src/RAG/agent.py`) equipped with a `search_langchain_docs` tool, allowing it to autonomously search and retrieve relevant documentation.
  - Added `notebooks/rag.ipynb` to experiment with the retrieval pipeline.
- **Explored / Tried**:
  - Iterative retrieval: The agent evaluates search results and can recursively call the search tool (up to 3 times) with refined queries if the initial context is insufficient.
  - Local, offline vector storage with Qdrant client (`/tmp/langchain_qdrant`).
- **Learned / Notes**:
  - Agentic RAG drastically improves answer quality over standard single-pass RAG because the LLM can dynamically course-correct and fetch missing context.
  - Ollama embeddings combined with local Qdrant provide a fast, private, and lightweight stack for building RAG applications.
  - Chunking is where the machine make or break

---
