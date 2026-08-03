"""
server.py – Núcleo del Servidor MCP.

Aquí se crea la instancia de FastMCP y se registran
todos los módulos de herramientas (tools).
"""

from mcp import FastMCP
from dotenv import load_dotenv

# Carga las variables de entorno desde .env
load_dotenv()

# ── Crear la instancia principal del servidor ─────────────────────────────────
mcp = FastMCP(
    name="servidor_mcp_local",
    instructions=(
        "Eres un asistente con acceso a herramientas de búsqueda de documentos (RAG), "
        "toma de decisiones (agente) y consultas a bases de datos y al SRI de Ecuador. "
        "Usa las herramientas disponibles según el contexto de cada solicitud."
    ),
)

# ── Importar y registrar las herramientas ─────────────────────────────────────
# Cada módulo importa `mcp` y decora sus funciones con @mcp.tool
import tools.rag_tools        # noqa: F401  – registra search_documents
import tools.agent_tools      # noqa: F401  – registra decide_action
import tools.db_sri_tools     # noqa: F401  – registra query_invoice, query_ruc

if __name__ == "__main__":
    mcp.run()