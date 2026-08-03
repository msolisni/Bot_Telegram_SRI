"""
scripts/seed_rag.py – Script de carga inicial de documentos en ChromaDB.

Ejecutar UNA VEZ para poblar el vector store con documentos de prueba:
    python scripts/seed_rag.py
"""

import sys
import os

# Asegurar que podemos importar desde la raíz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from rag.retriever import add_document_to_store, load_documents_from_folder

# ── Documentos de prueba hardcodeados ────────────────────────────────────────
SAMPLE_DOCS = [
    {
        "source": "politica_devoluciones",
        "content": (
            "Política de Devoluciones: El cliente tiene hasta 30 días desde la fecha "
            "de compra para devolver un producto. El producto debe estar en perfectas "
            "condiciones y con su empaque original. Para iniciar una devolución, el cliente "
            "debe presentar la factura original y contactar al servicio al cliente."
        ),
    },
    {
        "source": "manual_facturacion",
        "content": (
            "Manual de Facturación Electrónica: Para emitir una factura electrónica en Ecuador, "
            "debes tener un certificado digital vigente. La factura debe incluir: RUC del emisor, "
            "razón social, fecha de emisión, descripción del bien o servicio, subtotal, IVA (15%), "
            "y total. Las facturas deben ser autorizadas por el SRI antes de ser entregadas."
        ),
    },
    {
        "source": "contrato_tipo",
        "content": (
            "Contrato de Prestación de Servicios: Las partes acuerdan que el proveedor entregará "
            "los servicios acordados en un plazo de 30 días hábiles. El pago se realizará en dos "
            "cuotas: 50% al inicio y 50% a la entrega. Cualquier disputa será resuelta por "
            "mediación ante el Centro de Mediación de la Cámara de Comercio de Quito."
        ),
    },
]


def main():
    print("🔄 Iniciando carga de documentos en ChromaDB...")

    for doc in SAMPLE_DOCS:
        doc_id = add_document_to_store(content=doc["content"], source=doc["source"])
        print(f"  ✅ Indexado: {doc['source']} → ID: {doc_id[:8]}...")

    print(f"\n✨ {len(SAMPLE_DOCS)} documentos indexados correctamente.")
    print("💡 Ahora puedes buscarlos con la herramienta search_documents.")


if __name__ == "__main__":
    main()
