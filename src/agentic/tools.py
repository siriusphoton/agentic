from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langgraph.config import get_stream_writer
from .schemas import SaveNoteSchema, DeleteNoteSchema, SearchNotesSchema, SummarizeNotesSchema
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from langchain.messages import HumanMessage

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
def summarize_notes(topic: str, runtime: ToolRuntime) -> dict:
    """Always use this to summarize notes. Retrieves all notes related to a topic and instructs the system to summarize them. Once this returns return its output exactly the same"""

    class NoteSummary(BaseModel):
        topic :str = Field(description="Topic name of the whole summary in 2-3 words")
        key_points :list[str] = Field(description="Key points in sentences in a List")
        overall_summary :str = Field(description="Whole topic summarized in a few paragraphs")
        
    writer = runtime.stream_writer

    matches = _search(runtime.store, topic)
    writer("summarizing...")

    if not matches:
        return f"Cannot summarize: No notes found related to the topic '{topic}'."

    writer(f"Found {len(matches)} to summarize")
    raw_data = "\n---\n".join(matches)
    
    prompt = f"Please read this and provide a structured summary:\n\n{raw_data}"

    model = ChatOllama(
        model="gemma4:e2b-mlx",
        reasoning=False,
        temperature=0.0,
        top_p=0.5
    )
    
    agent = create_agent(
        model=model,
        response_format=NoteSummary,
        system_prompt="You are summaring bot. You will be given a few notes and asked to summarize. Always complex English while summarizing"
    )

    res = agent.invoke({"messages":[HumanMessage(prompt)]})

    return dict(res["structured_response"])


# Export list of tools for the agent
NOTEBOT_TOOLS = [save_note, delete_note, search_notes, summarize_notes]