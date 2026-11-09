#!/usr/bin/env python3
import os
import sys
import psycopg2

ruta = sys.argv[1] if len(sys.argv) > 1 else "output/job1/part-00000"

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=os.environ.get("DB_PORT", "5432"),
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
n = 0
with conn, conn.cursor() as cur:
    cur.execute("TRUNCATE resultados RESTART IDENTITY")  # recarga limpia
    with open(ruta) as f:
        for linea in f:
            partes = linea.rstrip("\n").split("\t")
            if len(partes) != 2:
                continue
            cur.execute("INSERT INTO resultados (clave, valor) VALUES (%s, %s)", partes)
            n += 1
print(f"Insertados {n} registros")
