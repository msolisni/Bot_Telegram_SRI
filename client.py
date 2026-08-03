"""
client.py – Cliente MCP y puente con Ollama.

Se conecta al servidor MCP local mediante stdio, descubre las herramientas
disponibles y permite chatear con el modelo local interactuando con la base de datos y RAG.
"""

import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama

load_dotenv()

# Configuración del modelo local con Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

async def run_chat():
    # Parámetros para conectar con tu servidor MCP actual (server.py)
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=os.environ.copy()
    )

    print("🔌 Conectando al Servidor MCP y cargando herramientas...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializar la sesión MCP
            await session.initialize()

            # Obtener la lista de herramientas disponibles desde tu servidor
            tools_response = await session.list_tools()
            tools = tools_response.tools
            
            print(f"✅ Herramientas cargadas en el agente: {[t.name for t in tools]}\n")
            print("🤖 ¡Asistente fiscal listo! Escribe tu consulta (o 'salir' para terminar).\n")

            # Convertir el esquema de herramientas de MCP al formato que entiende Ollama
            ollama_tools = []
            for t in tools:
                ollama_tools.append({
                    'type': 'function',
                    'function': {
                        'name': t.name,
                        'description': t.description,
                        'parameters': t.inputSchema
                    }
                })

            messages = [{
                'role': 'system', 
                'content': 'Eres un asistente fiscal experto en el SRI de Ecuador y normativas locales. Usa las herramientas provistas cuando sea necesario.'
            }]

            while True:
                try:
                    user_input = input("Tú: ")
                except (KeyboardInterrupt, EOFError):
                    break

                if user_input.lower() in ['salir', 'exit', 'quit']:
                    break

                if not user_input.strip():
                    continue

                messages.append({'role': 'user', 'content': user_input})

                # Llamada inicial a Ollama con las herramientas habilitadas
                response = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=messages,
                    tools=ollama_tools if ollama_tools else None
                )

                response_message = response.get('message', {})

                # Verificar si el modelo decidió invocar una herramienta
                if response_message.get('tool_calls'):
                    messages.append(response_message)
                    
                    for tool_call in response_message['tool_calls']:
                        tool_name = tool_call['function']['name']
                        tool_args = tool_call['function']['arguments']
                        
                        print(f"\n⚙️ [Agente ejecutando herramienta]: {tool_name} con argumentos {tool_args}")

                        try:
                            # Ejecutar la herramienta a través del protocolo MCP
                            result = await session.call_tool(tool_name, tool_args)
                            tool_output = result.content[0].text if result.content else str(result)
                        except Exception as e:
                            tool_output = f"Error ejecutando la herramienta {tool_name}: {str(e)}"

                        print(f"📥 [Resultado obtenido]: {tool_output}\n")

                        # Añadir la respuesta de la herramienta al historial del chat
                        messages.append({
                            'role': 'tool',
                            'content': tool_output,
                        })

                    # Segunda llamada a Ollama para que procese el resultado de la herramienta y le hable al usuario
                    final_response = ollama.chat(
                        model=OLLAMA_MODEL,
                        messages=messages
                    )
                    assistant_reply = final_response['message']['content']
                else:
                    assistant_reply = response_message.get('content', '')

                print(f"Asistente: {assistant_reply}\n")
                messages.append({'role': 'assistant', 'content': assistant_reply})

if __name__ == "__main__":
    asyncio.run(run_chat())