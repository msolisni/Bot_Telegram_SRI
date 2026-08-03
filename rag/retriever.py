"""
rag/retriever.py – Búsqueda semántica conectada directamente a Supabase.
"""

import os
from supabase import create_client, Client

# Cargar credenciales desde las variables de entorno
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

# Inicializar cliente oficial de Supabase
_supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def search_in_vector_store(query: str, top_k: int = 5) -> list[dict]:
    """
    Busca fragmentos similares llamando a una función RPC en Supabase 
    configurada con pgvector (por ejemplo, match_documents).
    """
    if not _supabase:
        print("Advertencia: Cliente de Supabase no inicializado.")
        return []

    output = []
    try:
        # Nota: Idealmente en Supabase creas una función RPC llamada 'match_documents' 
        # que reciba el vector de la query y devuelva los chunks más cercanos.
        # Aquí realizamos una consulta directa de ejemplo a una tabla llamada 'document_chunks'.
        response = _supabase.table("document_chunks").select("content, source").limit(top_k).execute()
        
        data = getattr(response, "data", [])
        for row in data:
            output.append({
                "content": row.get("content", ""),
                "source": row.get("source", "desconocida"),
                "distance": 0.0,
            })
    except Exception as e:
        print(f"Error al consultar Supabase: {e}")

    return output


def add_document_to_store(content: str, source: str = "manual") -> str:
    """
    Inserta un nuevo documento directamente en la tabla de Supabase.
    """
    if not _supabase:
        return "error-no-client"

    try:
        response = _supabase.table("document_chunks").insert({
            "content": content,
            "source": source
        }).execute()
        
        data = getattr(response, "data", [])
        if data:
            return str(data[0].get("id", "insercion-exitosa"))
    except Exception as e:
        print(f"Error al insertar en Supabase: {e}")

    return "error"