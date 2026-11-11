import os
from contextlib import contextmanager

import psycopg2
from flask import Flask, Response, jsonify, request

app = Flask(__name__)
app.json.compact = False
app.json.sort_keys = False


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


PAGINA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Datamart Pipeline</title>
<style>
body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#222}
h1{margin-bottom:.2rem} p{color:#666;margin-top:0}
select{padding:.4rem;font-size:1rem;margin:1rem 0}
table{border-collapse:collapse;width:100%}
th,td{padding:.5rem .8rem;border-bottom:1px solid #ddd;text-align:left}
th{background:#f4f4f4} td.num{text-align:right}
a{color:#0b63c5}
</style></head><body>
<h1>Datamart Pipeline</h1>
<p>Ventas por categoria y mes (resultado del job MapReduce).</p>
<label>Categoria: <select id="cat"></select></label>
<table><thead><tr><th>Mes</th><th>Categoria</th><th style="text-align:right">Valor</th></tr></thead>
<tbody id="filas"></tbody></table>
<p>API: <a href="/resultados">/resultados</a> &middot; <a href="/health">/health</a></p>
<script>
let datos = [];
const sel = document.getElementById("cat");
const cuerpo = document.getElementById("filas");
function pintar() {
  const filtro = sel.value;
  cuerpo.innerHTML = "";
  datos.filter(d => filtro === "Todas" || d.categoria === filtro).forEach(d => {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td>" + d.mes + "</td><td>" + d.categoria + "</td>" +
      '<td class="num">' + d.valor.toLocaleString("es-MX",
      {minimumFractionDigits: 2, maximumFractionDigits: 2}) + "</td>";
    cuerpo.appendChild(tr);
  });
}
fetch("/resultados").then(r => r.json()).then(r => {
  datos = r;
  const cats = ["Todas", ...new Set(r.map(d => d.categoria))];
  cats.forEach(c => sel.add(new Option(c, c)));
  sel.onchange = pintar;
  pintar();
});
</script></body></html>"""


@app.get("/")
def inicio():
    return Response(PAGINA, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
