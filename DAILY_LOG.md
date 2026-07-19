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
---
