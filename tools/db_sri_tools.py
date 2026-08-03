"""
tools/db_sri_tools.py – Herramientas de Base de Datos y SRI (Ecuador).

Conecta a PostgreSQL con psycopg2 y al SRI via HTTP para consultas
de facturación, validación de RUC y datos tributarios.
"""

from server import mcp
from db.postgres import get_invoice_from_db, get_client_from_db
from db.sri_client import validate_ruc_sri, get_sri_invoices


@mcp.tool()
def query_invoice(ruc: str, invoice_id: str) -> dict:
    """
    Consulta los detalles de una factura específica por RUC y número de factura.

    Úsala cuando el usuario pregunte por el estado, monto o detalles de
    una factura en particular. Primero busca en la base de datos local
    y si no encuentra, consulta al SRI.

    Args:
        ruc:        RUC del emisor o receptor (13 dígitos para Ecuador).
        invoice_id: Número de factura (ej. "001-001-000000123").

    Returns:
        Diccionario con: numero_factura, fecha, emisor, receptor,
        monto_total, iva, estado.
    """
    try:
        # 1. Intentar desde la base de datos local primero (más rápido)
        local_result = get_invoice_from_db(ruc=ruc, invoice_id=invoice_id)
        if local_result:
            return local_result

        # 2. Si no está localmente, consultar al SRI
        sri_result = get_sri_invoices(ruc=ruc, invoice_id=invoice_id)
        return sri_result

    except Exception as e:
        return {"error": str(e), "ruc": ruc, "factura": invoice_id}


@mcp.tool()
def validate_ruc(ruc: str) -> dict:
    """
    Valida un RUC ecuatoriano y obtiene la información del contribuyente.

    Úsala cuando necesites verificar si un RUC es válido o conocer
    el nombre, tipo y estado tributario de un contribuyente.

    Args:
        ruc: Número de RUC ecuatoriano (13 dígitos).

    Returns:
        Diccionario con: ruc, razon_social, tipo_contribuyente,
        estado, actividad_economica, obligado_contabilidad.
    """
    try:
        return validate_ruc_sri(ruc=ruc)
    except Exception as e:
        return {"error": str(e), "ruc": ruc}


@mcp.tool()
def query_client(client_id: int) -> dict:
    """
    Busca la información de un cliente en la base de datos PostgreSQL local.

    Úsala cuando necesites datos de un cliente registrado en el sistema,
    como su nombre, dirección, RUC o historial de compras.

    Args:
        client_id: ID entero del cliente en la base de datos local.

    Returns:
        Diccionario con los datos del cliente o un error si no existe.
    """
    try:
        return get_client_from_db(client_id=client_id)
    except Exception as e:
        return {"error": str(e), "client_id": client_id}
