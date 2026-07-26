from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent

@tool
def search_langchain_docs(query: str) -> str:
    """Search the LangChain documentation."""
    client = QdrantClient(path="/tmp/langchain_qdrant")
    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="test",
        embedding=embeddings,
    )

    try:
        docs_and_scores = vector_store.similarity_search_with_score(query, k=10)
    finally:
        client.close()

    if not docs_and_scores:
        return "No relevant documentation found."

    formatted = []

    for i, (doc, score) in enumerate(docs_and_scores, 1):
        formatted.append(
            f"""## Document {i}
Similarity Score: {score:.4f}
Source: {doc.metadata.get("source", "unknown")}

{doc.page_content}
"""
        )
    return "\n\n---\n\n".join(formatted)


import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.agents.middleware import ToolCallLimitMiddleware

checkpointer = SqliteSaver(conn=sqlite3.connect("db/checkpoint.db", check_same_thread=False))

model = ChatOllama(
    model="qwen3.5:4b-mlx",
    reasoning=False,
    temperature=0.0,
    top_p=0.5
)

search_agent = create_agent(
    model=model,
    system_prompt="""
        You are an expert LangChain documentation assistant.

        You have access to exactly one tool:
        - search_langchain_docs(query)

        Workflow:
        1. Analyze the user's question.
        2. Create the best search query you can.
        3. Call the search tool. The tool has a limit of 5 calls per run.
        4. If the retrieved documentation is insufficient, ambiguous, or only partially answers the question, reformulate the search query and search again.
        5. Continue until you have enough information.
        6. Base your answer ONLY on the retrieved documentation.
        7. If the documentation does not answer the question, clearly say so instead of guessing.
        8. Cite relevant source paths mentioned by the tool whenever possible.
    """,
    tools=[search_langchain_docs],
    middleware=[ToolCallLimitMiddleware(tool_name=search_langchain_docs.name, run_limit=5)],
    checkpointer=checkpointer,
)

@tool
def langchain_search_agent(query: str) -> str:
    """Queries a search agent specialized in LangChain documentation.

    Passes a user query to the underlying LangChain agent to retrieve answers, 
    code examples, or API specifications directly from LangChain docs.

    Args:
        query (str): The natural language query or technical question about LangChain.

    Returns:
        str: The final textual response extracted from the agent's message stack.
    """
    result = search_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        },
    )

    return result["messages"][-1].content

if __name__ == "__main__":
    msg = input("Enter: ")
    while msg:
        try:
            print(langchain_search_agent.invoke({"query": msg}))
        except Exception as e:
            print(f"Error: {e}")
        msg = input("Enter: ")
