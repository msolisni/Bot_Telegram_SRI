"""
agent/decision_agent.py – Agente de Toma de Decisiones con Anthropic Claude.

Llama a la API de Claude configurada mediante la variable de entorno ANTHROPIC_API_KEY.
Diseñado para correr de forma estable en la nube (Render).
"""

import os
import json
import anthropic

# ── Configuración desde variables de entorno ──────────────────────────────────
# Usamos un modelo rápido, económico y excelente para texto/JSON como Claude 3 Haiku
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")


# Inicializar cliente de Anthropic
_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def run_agent(context: str, options: str = "") -> str:
    """
    Envía el contexto a la API de Claude y obtiene una recomendación de acción.

    Args:
        context: Descripción de la situación actual.
        options: Opciones posibles (separadas por coma), o vacío para libre elección.

    Returns:
        Texto con la acción recomendada y su justificación.
    """
    system_prompt = (
        "Eres un agente experto en toma de decisiones. "
        "Analiza el contexto dado y recomienda la mejor acción. "
        "Sé conciso, directo y justifica brevemente tu elección."
    )

    user_message = f"Contexto:\n{context}"
    if options.strip():
        user_message += f"\n\nOpciones disponibles: {options}"
        user_message += "\n\nRecomienda UNA de las opciones anteriores y explica por qué."
    else:
        user_message += "\n\nRecomienda la mejor acción a tomar."

    try:
        response = _client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # temperatura baja = respuestas más deterministas
        )
        return response.content[0].text
    except Exception as e:
        return f"Error al consultar la API de Anthropic: {str(e)}"


def evaluate_risk(scenario: str, threshold: str = "medio") -> dict:
    """
    Evalúa el nivel de riesgo de un escenario usando Claude y devuelve un reporte estructurado.

    Returns:
        Dict con: nivel_riesgo, justificacion, recomendaciones
    """
    system_prompt = (
        "Eres un analista de riesgos. Evalúa el escenario dado y responde SOLO con un objeto JSON válido "
        "en el siguiente formato exacto, sin bloques de código markdown adicionales si es posible:\n"
        '{"nivel_riesgo": "bajo|medio|alto", '
        '"justificacion": "...", '
        '"recomendaciones": ["...", "..."]}'
    )

    user_message = (
        f"Escenario a evaluar:\n{scenario}\n\n"
        f"Umbral de tolerancia al riesgo configurado: {threshold}\n"
        "Responde ÚNICAMENTE con el JSON solicitado."
    )

    try:
        response = _client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
        )
        
        raw = response.content[0].text.strip()
        
        # Limpieza básica por si el modelo incluye marcas de código markdown como ```json ... ```
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:].strip()
        
        return json.loads(raw)
        
    except (json.JSONDecodeError, Exception) as e:
        # Fallback si ocurre un error o el modelo no devuelve JSON puro
        return {
            "nivel_riesgo": "desconocido",
            "justificacion": f"Error procesando respuesta o formato JSON: {str(e)}",
            "recomendaciones": ["Revisar manualmente el escenario."],
        }