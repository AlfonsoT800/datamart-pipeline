import os
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

def filas(cur):
    return [{"id": r[0], "clave": r[1], "valor": float(r[2])} for r in cur.fetchall()]

@app.get("/resultados")
def listar():
    with conexion() as c, c.cursor() as cur:
        cur.execute("SELECT id, clave, valor FROM resultados ORDER BY clave")
        return jsonify(filas(cur))

@app.get("/resultados/<clave>")
def por_clave(clave):
    # Coincidencia por categoria (parte antes del '|') o clave completa
    with conexion() as c, c.cursor() as cur:
        cur.execute(
            "SELECT id, clave, valor FROM resultados "
            "WHERE clave = %s OR clave LIKE %s ORDER BY clave",
            (clave, clave + "|%"),
        )
        return jsonify(filas(cur))

@app.post("/resultados")
def crear():
    d = request.get_json(force=True)
    with conexion() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO resultados (clave, valor) VALUES (%s, %s) RETURNING id",
            (d["clave"], d["valor"]),
        )
        return jsonify({"id": cur.fetchone()[0]}), 201

@app.put("/resultados/<int:rid>")
def actualizar(rid):
    d = request.get_json(force=True)
    with conexion() as c, c.cursor() as cur:
        cur.execute("UPDATE resultados SET valor = %s WHERE id = %s", (d["valor"], rid))
        return jsonify({"actualizados": cur.rowcount})

@app.delete("/resultados/<int:rid>")
def borrar(rid):
    with conexion() as c, c.cursor() as cur:
        cur.execute("DELETE FROM resultados WHERE id = %s", (rid,))
        return jsonify({"borrados": cur.rowcount})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
