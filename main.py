"""
main.py – Punto de entrada del Servidor MCP.

Ejecutar con:
    python main.py
"""

from server import mcp

if __name__ == "__main__":
    # mcp.run() inicia el servidor usando stdio (protocolo MCP estándar).
    # Esto es lo que los clientes como Claude Desktop u ollmcp esperan.
    mcp.run()
