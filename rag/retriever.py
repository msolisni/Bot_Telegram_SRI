"""
rag/retriever.py – Motor de búsqueda semántica con ChromaDB.

ChromaDB almacena los vectores localmente en disco.
Los embeddings se generan con sentence-transformers (sin API externa).
"""

import os
import uuid
import chromadb
from chromadb.utils import embedding_functions

# ── Configuración desde variables de entorno ──────────────────────────────────
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "documentos_empresa")

# Modelo de embeddings local (se descarga automáticamente la primera vez)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 80MB, rápido y preciso para español/inglés

# ── Inicializar cliente ChromaDB ──────────────────────────────────────────────
_client = chromadb.PersistentClient(path=PERSIST_DIR)

_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)

_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_embedding_fn,
    metadata={"hnsw:space": "cosine"},  # similitud coseno para textos
)


def search_in_vector_store(query: str, top_k: int = 5) -> list[dict]:
    """
    Busca los 'top_k' fragmentos más similares a 'query' en ChromaDB.

    Returns:
        Lista de dicts: [{"content": str, "source": str, "distance": float}]
    """
    results = _collection.query(
        query_texts=[query],
        n_results=min(top_k, _collection.count() or 1),
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "content": doc,
            "source": meta.get("source", "desconocida"),
            "distance": round(dist, 4),
        })

    return output


def add_document_to_store(content: str, source: str = "manual") -> str:
    """
    Añade un documento al vector store y devuelve su ID único.
    """
    doc_id = str(uuid.uuid4())
    _collection.add(
        documents=[content],
        metadatas=[{"source": source}],
        ids=[doc_id],
    )
    return doc_id


def load_documents_from_folder(folder_path: str) -> int:
    """
    Carga todos los archivos .txt de una carpeta en el vector store.
    Útil para la carga inicial de documentos.

    Returns:
        Número de documentos indexados.
    """
    import glob

    count = 0
    for filepath in glob.glob(os.path.join(folder_path, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        source = os.path.basename(filepath)
        add_document_to_store(content=content, source=source)
        count += 1

    return count
