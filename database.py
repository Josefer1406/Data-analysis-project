import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

# =========================
# CREAR TABLA
# =========================
def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP,
            symbol TEXT,
            tipo TEXT,
            precio FLOAT,
            size FLOAT,
            pnl FLOAT,
            capital FLOAT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# =========================
# INSERTAR
# =========================
def insertar_trade(fecha, symbol, tipo, precio, size, pnl, capital):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trades (fecha, symbol, tipo, precio, size, pnl, capital)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (fecha, symbol, tipo, precio, size, pnl, capital))

    conn.commit()
    cur.close()
    conn.close()

# =========================
# OBTENER
# =========================
def obtener_trades():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM trades ORDER BY fecha ASC")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

# =========================
# RESET TOTAL 🔥
# =========================
def reset_database():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("DELETE FROM trades;")

    conn.commit()
    cur.close()
    conn.close()

    print("🧹 Base de datos reiniciada")