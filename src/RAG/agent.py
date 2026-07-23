from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent

client = QdrantClient(path="/tmp/langchain_qdrant")

embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")

vector_store = QdrantVectorStore(
    client=client,
    collection_name="test",
    embedding=embeddings,
)


@tool
def search_langchain_docs(query: str) -> str:
    """Search the LangChain documentation."""

    docs_and_scores = vector_store.similarity_search_with_score(query, k=10)

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


SYSTEM_PROMPT = """
You are an expert LangChain documentation assistant.

You have access to exactly one tool:
- search_langchain_docs(query)

Workflow:
1. Analyze the user's question.
2. Create the best search query you can.
3. Call the search tool IF YOU HAVENT CALLED IT MORE THAN 3 TIMES
3.B If called more than 3 times answer immediately.
4. If the retrieved documentation is insufficient, ambiguous, or only partially answers the question, reformulate the search query and search again.
5. Continue until you have enough information.
6. Base your answer ONLY on the retrieved documentation.
7. If the documentation does not answer the question, clearly say so instead of guessing.
8. Cite relevant source paths mentioned by the tool whenever possible.
"""


def rag_agent(query: str) -> str:
    model = ChatOllama(
        model="qwen3.5:4b-mlx",
        reasoning=False,
        temperature=0.0,
        top_p=0.5,
    )

    agent = create_agent(
        model=model,
        tools=[search_langchain_docs],
        system_prompt=SYSTEM_PROMPT,
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )

    # Return the final assistant response.
    client.close()
    return result["messages"][-1].text

query = input("Enter: ")
print(rag_agent(query))