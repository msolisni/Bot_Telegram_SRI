"""
tools/agent_tools.py – Herramientas del Agente de Toma de Decisiones.

Llama a un modelo local via Ollama para razonar sobre un contexto dado
y recomendar la mejor acción a tomar.
"""

from server import mcp
from agent.decision_agent import run_agent


@mcp.tool()
def decide_action(context: str, options: str = "") -> str:
    """
    Analiza una situación y recomienda la mejor acción a tomar.

    Úsala cuando el usuario presente un problema complejo que requiera
    razonamiento, análisis de opciones o planificación de pasos a seguir.

    Args:
        context: Descripción detallada de la situación o problema actual.
        options: (Opcional) Lista de opciones posibles separadas por coma.
                 Ej: "aprobar solicitud, rechazar solicitud, pedir más info"

    Returns:
        La acción recomendada con una breve justificación.
    """
    try:
        result = run_agent(context=context, options=options)
        return result
    except Exception as e:
        return f"Error en el agente de decisiones: {str(e)}"


@mcp.tool()
def analyze_risk(scenario: str, threshold: str = "medio") -> dict:
    """
    Evalúa el nivel de riesgo de un escenario dado y produce un reporte.

    Úsala cuando necesites que la IA evalúe si una situación representa
    un riesgo bajo, medio o alto, con recomendaciones específicas.

    Args:
        scenario:  Descripción del escenario a evaluar.
        threshold: Nivel de tolerancia al riesgo: 'bajo', 'medio' o 'alto'.

    Returns:
        Diccionario con: nivel_riesgo, justificacion, recomendaciones (lista).
    """
    try:
        from agent.decision_agent import evaluate_risk
        return evaluate_risk(scenario=scenario, threshold=threshold)
    except Exception as e:
        return {"error": str(e), "nivel_riesgo": "desconocido"}
