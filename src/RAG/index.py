import requests
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings

DOCS_BASE = "https://docs.langchain.com"

DOC_PATHS = [
    "oss/python/langchain/agents",
    "oss/python/deepagents/rag",
    "oss/python/langchain/tools",
    "oss/python/langchain/models",
    "oss/python/langchain/retrieval",
    "oss/python/langchain/knowledge-base",
    "oss/python/langchain/middleware",
    "oss/python/deepagents/overview",
    "oss/python/deepagents/subagents",
    "oss/python/deepagents/streaming",
    "oss/python/deepagents/frontend/subagent-streaming",
    "oss/python/deepagents/backends",
    "oss/python/langgraph/overview",
    "oss/python/langgraph/quickstart",
]

def load_langchain_docs(doc_paths: list[str] | None = None) -> list[Document]:
    paths = doc_paths or DOC_PATHS
    docs: list[Document]=[]
    for path in paths:
        url = f"{DOCS_BASE}/{path}.md"
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException:
            continue
        source = f"{DOCS_BASE}/{path}"
        docs.append(
            Document(page_content=response.text, metadata={"source":source})
        )
    return docs


docs = load_langchain_docs()
print(f"Loaded {len(docs)} documentation pages.")
total_chars = sum(len(doc.page_content) for doc in docs)
print(f"Total characters: {total_chars}")


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
print(f"Split documentation into {len(all_splits)} chunks.")


embeddings = OllamaEmbeddings(model='qwen3-embedding:0.6b')
client = QdrantClient(path="/tmp/langchain_qdrant")
vector_size = len(embeddings.embed_query("sample text"))

COLLECTION = "test"

if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(
        size=vector_size,
        distance=Distance.COSINE,
    ),
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="test",
    embedding=embeddings,
)

vector_store.add_documents(documents=all_splits)
print(f"Indexed {len(all_splits)} chunks.")
client.close()