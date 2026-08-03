"""
db/postgres.py – Conexión y consultas a PostgreSQL con psycopg2.

Las credenciales se leen desde variables de entorno definidas en .env
"""

import os
import psycopg2
import psycopg2.extras  # para recibir resultados como dicts

# ── Configuración desde variables de entorno ──────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", 5432)),
    "dbname":   os.getenv("POSTGRES_DB", "mi_base_de_datos"),
    "user":     os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
}


def _get_connection():
    """Crea y devuelve una conexión a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def get_invoice_from_db(ruc: str, invoice_id: str) -> dict | None:
    """
    Busca una factura en la tabla 'facturas' de la base de datos local.

    Returns:
        Dict con los datos de la factura, o None si no existe.
    """
    query = """
        SELECT
            numero_factura,
            fecha_emision,
            ruc_emisor,
            razon_social_emisor,
            ruc_receptor,
            razon_social_receptor,
            subtotal,
            iva,
            total,
            estado
        FROM facturas
        WHERE (ruc_emisor = %s OR ruc_receptor = %s)
          AND numero_factura = %s
        LIMIT 1;
    """
    with _get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (ruc, ruc, invoice_id))
            row = cur.fetchone()
            return dict(row) if row else None


def get_client_from_db(client_id: int) -> dict:
    """
    Obtiene los datos de un cliente por su ID.

    Returns:
        Dict con la información del cliente.

    Raises:
        ValueError: Si el cliente no existe.
    """
    query = """
        SELECT
            id,
            nombre,
            ruc,
            email,
            telefono,
            direccion,
            fecha_registro
        FROM clientes
        WHERE id = %s;
    """
    with _get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (client_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Cliente con ID {client_id} no encontrado.")
            return dict(row)


def execute_query(sql: str, params: tuple = ()) -> list[dict]:
    """
    Ejecuta una consulta SELECT arbitraria y devuelve los resultados.
    ADVERTENCIA: Úsala solo con consultas ya validadas, no con entrada del usuario.
    """
    with _get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
