# Servidor MCP Local – RAG + Agente + PostgreSQL/SRI

Servidor MCP completo en Python que expone herramientas de IA para búsqueda de documentos (RAG), toma de decisiones con Ollama y consultas a PostgreSQL/SRI de Ecuador.

---

## 📁 Estructura del Proyecto

```
Server_MCP/
│
├── main.py               ← Punto de entrada (python main.py)
├── server.py             ← Instancia FastMCP + registro de herramientas
├── requirements.txt      ← Dependencias Python
├── .env.example          ← Plantilla de variables de entorno
├── mcp_config.json       ← Config para Claude Desktop / clientes MCP
│
├── tools/                ← Herramientas expuestas al cliente MCP
│   ├── rag_tools.py      ← search_documents, index_document
│   ├── agent_tools.py    ← decide_action, analyze_risk
│   └── db_sri_tools.py   ← query_invoice, validate_ruc, query_client
│
├── rag/
│   └── retriever.py      ← ChromaDB: buscar y añadir documentos
│
├── agent/
│   └── decision_agent.py ← Agente Ollama: razonamiento y análisis de riesgo
│
├── db/
│   ├── postgres.py       ← Consultas a PostgreSQL con psycopg2
│   └── sri_client.py     ← Cliente HTTP para el SRI de Ecuador
│
├── scripts/
│   ├── seed_rag.py       ← Carga inicial de documentos en ChromaDB
│   └── init_db.sql       ← Crear tablas en PostgreSQL
│
└── data/
    └── chroma_db/        ← Vector store persistente (auto-creado)
```

---

## 🚀 Instalación Paso a Paso

### 1. Verificar Python

```bash
python --version   # Necesitas Python 3.11 o superior
```

Si no tienes Python, descárgalo de [python.org](https://www.python.org/downloads/).

### 2. Crear entorno virtual e instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar (Windows CMD)
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar la plantilla
copy .env.example .env

# Editar .env con tus datos reales (usa Notepad, VS Code, etc.)
notepad .env
```

Variables más importantes en `.env`:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `POSTGRES_HOST` | Host de PostgreSQL | `localhost` |
| `POSTGRES_DB` | Nombre de la base de datos | `mi_base_de_datos` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña | `mi_contraseña` |
| `OLLAMA_MODEL` | Modelo de Ollama a usar | `qwen2.5:14b` |
| `SRI_USE_MOCK` | Usar datos falsos del SRI | `true` (para pruebas) |

### 4. Inicializar la base de datos PostgreSQL

```bash
# Crear las tablas (ajusta usuario y base de datos)
psql -U postgres -d mi_base_de_datos -f scripts/init_db.sql
```

### 5. Cargar documentos iniciales en el RAG

```bash
python scripts/seed_rag.py
```

---

## 🦙 Configurar Ollama (Modelo Local)

### Instalar Ollama

Descarga desde [ollama.com](https://ollama.com/download) e instálalo.

```bash
# Verificar instalación
ollama --version
```

### Descargar el modelo con soporte de herramientas (tool calling)

```bash
# Opción recomendada – buena relación velocidad/calidad
ollama pull qwen2.5:14b

# Alternativa ligera (para GPUs con menos VRAM)
ollama pull qwen2.5:7b

# Opción más potente (requiere 20GB+ VRAM)
ollama pull qwen2.5:32b
```

### Verificar que Ollama está corriendo

```bash
# Debe responder con la lista de modelos descargados
ollama list

# Probar que el modelo funciona
ollama run qwen2.5:14b "Di hola"
```

---

## ▶️ Ejecutar el Servidor MCP

```bash
# Terminal 1 – Asegúrate de estar en la carpeta del proyecto con el venv activo
python main.py
```

Si todo está bien, NO verás output en la terminal (el servidor MCP usa stdio, no imprime logs).

Para ver logs de debug:

```bash
# Con nivel de log MCP activado
MCP_LOG_LEVEL=debug python main.py
```

---

## 🔌 Conectar un Cliente

### Opción A – Claude Desktop

Copia el contenido de `mcp_config.json` en tu configuración de Claude Desktop:

- Ruta Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "servidor_mcp_local": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "C:/Users/asbel/OneDrive/Desktop/General/Server_MCP"
    }
  }
}
```

Reinicia Claude Desktop. Las herramientas aparecerán en el chat.

### Opción B – ollmcp (Ollama + MCP)

```bash
# Instalar ollmcp
pip install ollmcp

# Iniciar cliente Ollama conectado al servidor MCP
# Terminal 2 (mientras Terminal 1 tiene python main.py corriendo)
ollmcp --model qwen2.5:14b --mcp-server "python main.py"
```

### Opción C – Inspector MCP (para pruebas)

```bash
# Herramienta oficial para probar servidores MCP
npx @modelcontextprotocol/inspector python main.py
```

Abre `http://localhost:5173` en tu navegador para ver y llamar las herramientas.

---

## 🧪 Pruebas y Validación

### Verificar que las herramientas están registradas

Una vez conectado con el inspector MCP o Claude Desktop, deberías ver estas herramientas:

| Herramienta | Módulo | Descripción |
|-------------|--------|-------------|
| `search_documents` | RAG | Busca documentos por similitud semántica |
| `index_document` | RAG | Agrega un documento al vector store |
| `decide_action` | Agente | Recomienda una acción dado un contexto |
| `analyze_risk` | Agente | Evalúa el riesgo de un escenario |
| `query_invoice` | DB/SRI | Consulta una factura por RUC y número |
| `validate_ruc` | SRI | Valida un RUC ecuatoriano |
| `query_client` | DB | Busca un cliente en PostgreSQL |

### Prompts de prueba para el chat

```
# Probar RAG
¿Cuál es la política de devoluciones de la empresa?

# Probar Agente
Tengo que decidir si aprobar un crédito de $50,000 a un cliente que 
tiene buen historial pero está en un sector de alto riesgo. ¿Qué hago?

# Probar validación de RUC
Valida el RUC 1790012345001 y dime si es válido.

# Probar consulta de factura
Consulta la factura 001-001-000000001 para el RUC 1790012345001.

# Probar análisis de riesgo
Analiza el riesgo de implementar un nuevo sistema ERP en producción 
sin realizar pruebas de carga previas.
```

---

## ❌ Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|---------|
| `ModuleNotFoundError: mcp` | SDK MCP no instalado | `pip install mcp[cli]` |
| `connection refused localhost:11434` | Ollama no está corriendo | Ejecutar `ollama serve` en otra terminal |
| `psycopg2.OperationalError` | PostgreSQL no accesible o credenciales incorrectas | Verificar `.env` y que PostgreSQL esté corriendo |
| `chromadb: collection not found` | Vector store vacío | Ejecutar `python scripts/seed_rag.py` |
| `Tool not found` | La herramienta no se registró | Verificar que los imports en `server.py` no tienen errores de sintaxis |
| `Port already in use` | Otro proceso usa el puerto | Cambiar `MCP_PORT` en `.env` o cerrar el proceso |
| `ollmcp: command not found` | ollmcp no instalado | `pip install ollmcp` |

---

## 📝 Notas Importantes

- **SRI en modo mock**: Por defecto `SRI_USE_MOCK=false`. Pon `SRI_USE_MOCK=true` en tu `.env` para pruebas sin conexión real.
- **Primera ejecución del RAG**: El modelo de embeddings (`all-MiniLM-L6-v2`) se descarga automáticamente (~80MB).
- **Seguridad**: Nunca subas tu archivo `.env` a Git. Agrega `.env` a tu `.gitignore`.
- **Puerto por defecto**: El servidor MCP usa stdio (no HTTP), por lo que no ocupa un puerto de red.
