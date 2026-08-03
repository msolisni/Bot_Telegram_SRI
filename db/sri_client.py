"""
db/sri_client.py – Cliente HTTP para consultas al SRI de Ecuador.

El SRI no tiene una API REST oficial pública documentada para todos los servicios,
por lo que se usa la URL de consulta de RUC que sí está disponible públicamente.

Para entornos de desarrollo se incluye un modo MOCK que devuelve datos de prueba.
"""

import os
import httpx

SRI_API_URL = os.getenv(
    "SRI_API_URL",
    "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest",
)
SRI_API_KEY = os.getenv("SRI_API_KEY", "")  # solo si tu integración lo requiere

# Poner en True para pruebas sin conexión real al SRI
USE_MOCK = os.getenv("SRI_USE_MOCK", "false").lower() == "true"


def validate_ruc_sri(ruc: str) -> dict:
    """
    Consulta el RUC en el servicio público del SRI y devuelve datos del contribuyente.

    Endpoint real:
      GET /SujetoInformante/obtenerInformacion?nombreUnidad=SRI&tipoIdentificacion=R&identificacion={ruc}
    """
    if USE_MOCK:
        return _mock_ruc_response(ruc)

    url = f"{SRI_API_URL}/SujetoInformante/obtenerInformacion"
    params = {
        "nombreUnidad": "SRI",
        "tipoIdentificacion": "R",  # R = RUC
        "identificacion": ruc,
    }
    headers = {"Accept": "application/json"}
    if SRI_API_KEY:
        headers["Authorization"] = f"Bearer {SRI_API_KEY}"

    with httpx.Client(timeout=15.0) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

    # Normalizar la respuesta al formato esperado por nuestras herramientas
    return {
        "ruc": ruc,
        "razon_social": data.get("nombreComercial") or data.get("razonSocial", ""),
        "tipo_contribuyente": data.get("tipoContribuyente", ""),
        "estado": data.get("estadoContribuyente", ""),
        "actividad_economica": data.get("actividadEconomicaPrincipal", ""),
        "obligado_contabilidad": data.get("obligadoLlevarContabilidad", "NO"),
        "fuente": "SRI",
    }


def get_sri_invoices(ruc: str, invoice_id: str) -> dict:
    """
    Busca una factura en el sistema del SRI.

    NOTA: El SRI no expone una API pública directa para esto.
    Esta función sirve como punto de integración si tienes acceso
    a los servicios web del SRI por certificado digital o convenio.

    Por ahora devuelve un resultado mock con la estructura esperada.
    """
    if USE_MOCK or True:  # Siempre mock hasta tener acceso real
        return _mock_invoice_response(ruc, invoice_id)

    # ── Código para integración real (requiere certificado digital SRI) ────────
    # Aquí iría la llamada SOAP o REST según el convenio con el SRI
    # url = f"{SRI_API_URL}/comprobantes/consultar"
    # ...
    raise NotImplementedError("Integración real con SRI pendiente de configurar.")


# ── Respuestas de prueba (MOCK) ───────────────────────────────────────────────

def _mock_ruc_response(ruc: str) -> dict:
    """Datos simulados para pruebas sin conexión al SRI."""
    return {
        "ruc": ruc,
        "razon_social": "EMPRESA DEMO S.A.",
        "tipo_contribuyente": "SOCIEDAD",
        "estado": "ACTIVO",
        "actividad_economica": "ACTIVIDADES DE CONSULTORÍA DE GESTIÓN",
        "obligado_contabilidad": "SI",
        "fuente": "MOCK",
    }


def _mock_invoice_response(ruc: str, invoice_id: str) -> dict:
    """Factura simulada para pruebas."""
    return {
        "numero_factura": invoice_id,
        "fecha_emision": "2024-01-15",
        "ruc_emisor": ruc,
        "razon_social_emisor": "EMPRESA DEMO S.A.",
        "ruc_receptor": "0999999999001",
        "razon_social_receptor": "CLIENTE DEMO CIA. LTDA.",
        "subtotal": 1000.00,
        "iva": 150.00,
        "total": 1150.00,
        "estado": "AUTORIZADA",
        "fuente": "MOCK",
    }
