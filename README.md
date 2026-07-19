# Agentic (NoteBot)

An iterative AI agent project focused on building robust agent architectures with LangChain and LangGraph. The repository serves as a hands-on codebase for developing **NoteBot**—an AI assistant designed to manage personal notes with structured tool calling, middleware, and memory.

---

## 🛠️ Project Structure

```text
agentic/
├── src/
│   └── agentic/
│       ├── __init__.py
│       ├── main.py        # Agent configuration, middleware, and CLI loop
│       ├── schemas.py     # Pydantic schemas for tool inputs
│       └── tools.py       # NoteBot tool implementations (save, delete, search, summarize)
├── notebooks/
│   └── try.ipynb          # Interactive playground for state inspection and testing
├── DAILY_LOG.md           # Progress log tracking implemented features and learnings
├── pyproject.toml         # Dependencies and project metadata
└── README.md              # Project overview
```

---

## 🤖 NoteBot Capabilities

NoteBot provides structured tools for personal note management:
* **`save_note`**: Saves a note by title and content (requires human approval).
* **`delete_note`**: Permanently deletes a note by exact title (requires human approval).
* **`search_notes`**: Case-insensitive keyword search across saved notes.
* **`summarize_notes`**: Retrieves notes on a topic and outputs structured summaries.

### Agent Middleware
1. **Human-in-the-Loop (HITL)**: Interrupts execution on sensitive tool calls (`save_note`, `delete_note`).
2. **Tool Retry Middleware**: Retries failed tool calls with exponential backoff.
3. **Execution Logging**: Logs requested tools, arguments, and responses.

---

## 🚀 Quickstart

### Setup & Run
1. **Install Dependencies**:
   ```bash
   uv sync
   ```
2. **Environment Variables**:
   Create a `.env` file for any required API keys or configuration:
   ```env
   # Add environment variables here
   ```
3. **Run NoteBot**:
   ```bash
   python -m src.agentic.main
   ```
