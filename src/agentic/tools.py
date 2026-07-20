from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langgraph.config import get_stream_writer
from .schemas import SaveNoteSchema, DeleteNoteSchema, SearchNotesSchema, SummarizeNotesSchema

_NAMESPACE = ("notes",)

def _search(store, query: str) -> list[str]:
    """Private helper to find all notes matching a case-insensitive query."""
    matches = []
    query_lower = query.lower()

    for item in store.search(_NAMESPACE):
        title = item.key
        content = item.value["content"]

        if query_lower in title.lower() or query_lower in content.lower():
            matches.append(f"Title: {title}\nContent: {content}")

    return matches

@tool(args_schema=SaveNoteSchema)
def save_note(title: str, content: str, runtime: ToolRuntime) -> str:
    """Saves a new note to memory. Fails if a note with the exact title already exists."""
    writer = runtime.stream_writer
    store = runtime.store

    writer("saving...")
    title_lower = title.lower()

    # Check against all lowercase titles to prevent "Docker" and "docker" duplicates
    if store.get(_NAMESPACE, title_lower):
        return f"Error: A note with the title '{title}' already exists. Please use a different title or delete the old one first."

    store.put(_NAMESPACE, title_lower, {"content": content})
    writer(f"saved '{title_lower}'")
    return f"Success: Note '{title}' saved."

@tool(args_schema=DeleteNoteSchema)
def delete_note(title: str, runtime: ToolRuntime) -> str:
    """Permanently deletes a note by its exact title."""
    writer = runtime.stream_writer
    store = runtime.store

    writer("deleting...")
    title = title.lower()

    if store.get(_NAMESPACE, title):
        store.delete(_NAMESPACE, title)
        writer(f"deleted '{title}'")
        return f"Success: Note '{title}' has been deleted."

    return f"Error: Note '{title}' not found."

@tool(args_schema=SearchNotesSchema)
def search_notes(query: str, runtime: ToolRuntime) -> str:
    """Searches through all saved notes for a specific keyword. Returns matching notes."""
    writer = runtime.stream_writer

    writer("searching...")
    matches = _search(runtime.store, query)

    if not matches:
        return f"No notes found matching the query: '{query}'."

    # Format the matches clearly so the LLM doesn't get confused
    formatted_results = "\n---\n".join(matches)
    writer(f"Found {len(matches)}")
    return f"Found {len(matches)} matching note(s):\n\n{formatted_results}"

@tool(args_schema=SummarizeNotesSchema)
def summarize_notes(topic: str, runtime: ToolRuntime) -> str:
    """Retrieves all notes related to a topic and instructs the system to summarize them."""
    writer = runtime.stream_writer

    matches = _search(runtime.store, topic)
    writer("summarizing...")

    if not matches:
        return f"Cannot summarize: No notes found related to the topic '{topic}'."

    writer(f"Found {len(matches)} to summarize")
    raw_data = "\n---\n".join(matches)

    # We don't summarize it here in Python. We return the raw data wrapped in an
    # instruction to the LLM. The LLM will read this output and generate the summary.
    return (
        f"Here is all the raw data found for the topic '{topic}'. "
        f"Please read this and provide a structured, concise summary for the user:\n\n{raw_data}"
    )

# Export list of tools for the agent
NOTEBOT_TOOLS = [save_note, delete_note, search_notes, summarize_notes]