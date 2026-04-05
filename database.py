import psycopg2
import os
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL")

def conectar():
    result = urlparse(DATABASE_URL)

    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

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

def insertar_trade(fecha, symbol, tipo, precio, size, pnl, capital):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trades (fecha, symbol, tipo, precio, size, pnl, capital)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (fecha, symbol, tipo, precio, size, pnl, capital))

    conn.commit()
    cur.close()
    conn.close()

def obtener_trades():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM trades ORDER BY fecha ASC;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows