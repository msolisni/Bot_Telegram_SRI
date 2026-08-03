"""
tools/rag_tools.py – Herramientas de Recuperación Aumentada (RAG).

Usa ChromaDB como vector store y sentence-transformers para embeddings.
"""

import os
from server import mcp
from rag.retriever import search_in_vector_store


@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> str:
    """
    Busca documentos relevantes en la base de conocimiento usando similitud semántica.

    Úsala cuando el usuario pregunte algo que requiera información de documentos
    internos, manuales, políticas, contratos o cualquier corpus de texto indexado.

    Args:
        query:  La pregunta o término de búsqueda en lenguaje natural.
        top_k:  Número máximo de fragmentos a devolver (por defecto 5).

    Returns:
        Un texto con los fragmentos más relevantes encontrados.
    """
    try:
        results = search_in_vector_store(query=query, top_k=top_k)

        if not results:
            return "No se encontraron documentos relevantes para la consulta."

        # Formatear los resultados para que la IA los pueda leer fácilmente
        formatted = []
        for i, doc in enumerate(results, 1):
            formatted.append(
                f"[Fragmento {i}] (fuente: {doc.get('source', 'desconocida')})\n"
                f"{doc['content']}\n"
            )

        return "\n---\n".join(formatted)

    except Exception as e:
        return f"Error al buscar documentos: {str(e)}"


@mcp.tool()
def index_document(content: str, source: str = "manual") -> str:
    """
    Añade un nuevo documento al vector store para que esté disponible en búsquedas futuras.

    Úsala cuando el usuario quiera agregar nueva información a la base de conocimiento.

    Args:
        content: El texto completo del documento a indexar.
        source:  Identificador de la fuente (ej. 'manual_ventas', 'politica_rrhh').

    Returns:
        Confirmación de que el documento fue indexado correctamente.
    """
    from rag.retriever import add_document_to_store
    try:
        doc_id = add_document_to_store(content=content, source=source)
        return f"Documento indexado correctamente con ID: {doc_id}"
    except Exception as e:
        return f"Error al indexar el documento: {str(e)}"
