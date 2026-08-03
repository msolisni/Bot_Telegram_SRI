import os
import glob
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def limpiar_e_importar():
    print("Conectando a PostgreSQL...")
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT")
    )
    cursor = conn.cursor()

    print("Limpiando datos ficticios y registros anteriores en la base de datos...")
    cursor.execute("TRUNCATE TABLE sri_contribuyentes RESTART IDENTITY CASCADE;")
    conn.commit()
    print("¡Tabla vaciada correctamente!")

    ruta_archivos = "./data_sri/*.csv"
    archivos = glob.glob(ruta_archivos)

    if not archivos:
        print(f"⚠️ No se encontraron archivos CSV en la ruta: {ruta_archivos}")
        cursor.close()
        conn.close()
        return

    for archivo in archivos:
        print(f"Procesando archivo: {archivo}...")
        try:
            # Lectura optimizada para archivos delimitados por pipe (|)
            df = pd.read_csv(archivo, encoding='latin1', sep='|', low_memory=False, on_bad_lines='skip')
            
            # Limpiar nombres de columnas
            df.columns = [str(col).strip().upper() for col in df.columns]

            # Mapeo exacto según la estructura del SRI
            col_ruc = 'NUMERO_RUC' if 'NUMERO_RUC' in df.columns else next((c for c in df.columns if 'RUC' in c), None)
            col_razon = 'RAZON_SOCIAL' if 'RAZON_SOCIAL' in df.columns else next((c for c in df.columns if 'RAZON' in c), None)
            col_estado = 'ESTADO_CONTRIBUYENTE' if 'ESTADO_CONTRIBUYENTE' in df.columns else next((c for c in df.columns if 'ESTADO' in c), None)

            if not col_ruc:
                print(f"⚠️ El archivo {archivo} no contiene la columna NUMERO_RUC. Saltando...")
                continue

            for _, row in df.iterrows():
                ruc = str(row.get(col_ruc, '')).strip()
                razon_social = str(row.get(col_razon, '')).strip() if col_razon else 'N/D'
                estado = str(row.get(col_estado, 'ACTIVO')).strip() if col_estado else 'ACTIVO'

                # Filtrar valores vacíos o nulos
                if not ruc or ruc.lower() in ['nan', 'none'] or len(ruc) < 10:
                    continue

                cursor.execute("""
                    INSERT INTO sri_contribuyentes (ruc, razon_social, estado)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (ruc) DO NOTHING;
                """, (ruc, razon_social, estado))
            
            conn.commit()
            print(f"-> Archivo {archivo} importado con éxito.")
            
        except Exception as e:
            print(f"❌ Error al procesar el archivo {archivo}: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
    print("🎉 Proceso de importación masiva finalizado.")

if __name__ == "__main__":
    limpiar_e_importar()