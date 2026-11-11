import os
from contextlib import contextmanager

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def conexion():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


@contextmanager
def cursor():
    """Abre conexion, hace commit (o rollback si hay error) y SIEMPRE la cierra."""
    c = conexion()
    try:
        with c, c.cursor() as cur:
            yield cur
    finally:
        c.close()


def filas(cur):
    salida = []
    for r in cur.fetchall():
        categoria, _, mes = r[1].partition("|")
        salida.append({
            "id": r[0],
            "clave": r[1],
            "categoria": categoria,
            "mes": mes,
            "valor": float(r[2]),
        })
    return salida


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/resultados")
def listar():
    with cursor() as cur:
        cur.execute("SELECT id, clave, valor FROM resultados ORDER BY clave")
        return jsonify(filas(cur))


@app.get("/resultados/<clave>")
def por_clave(clave):
    # Coincidencia por categoria (parte antes del '|') o clave completa
    with cursor() as cur:
        cur.execute(
            "SELECT id, clave, valor FROM resultados "
            "WHERE clave = %s OR clave LIKE %s ORDER BY clave",
            (clave, clave + "|%"),
        )
        datos = filas(cur)
    if not datos:
        return jsonify({"error": "no encontrado"}), 404
    return jsonify(datos)


@app.post("/resultados")
def crear():
    d = request.get_json(force=True, silent=True) or {}
    if "clave" not in d or "valor" not in d:
        return jsonify({"error": "se requieren 'clave' y 'valor'"}), 400
    with cursor() as cur:
        cur.execute(
            "INSERT INTO resultados (clave, valor) VALUES (%s, %s) RETURNING id",
            (d["clave"], d["valor"]),
        )
        return jsonify({"id": cur.fetchone()[0]}), 201


@app.put("/resultados/<int:rid>")
def actualizar(rid):
    d = request.get_json(force=True, silent=True) or {}
    if "valor" not in d:
        return jsonify({"error": "se requiere 'valor'"}), 400
    with cursor() as cur:
        cur.execute("UPDATE resultados SET valor = %s WHERE id = %s", (d["valor"], rid))
        if cur.rowcount == 0:
            return jsonify({"error": "no encontrado"}), 404
        return jsonify({"actualizados": cur.rowcount})


@app.delete("/resultados/<int:rid>")
def borrar(rid):
    with cursor() as cur:
        cur.execute("DELETE FROM resultados WHERE id = %s", (rid,))
        if cur.rowcount == 0:
            return jsonify({"error": "no encontrado"}), 404
        return jsonify({"borrados": cur.rowcount})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
