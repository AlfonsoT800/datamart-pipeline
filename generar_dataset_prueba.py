import sys
import numpy as np
import pandas as pd

semilla = int(sys.argv[1]) if len(sys.argv) > 1 else 123456789
N, CHUNK = 5_000_000, 500_000
rng = np.random.default_rng(semilla)

tiendas = [f"T{i:03d}" for i in range(1, 51)]
categorias = ["Abarrotes", "Lacteos", "Bebidas", "Limpieza", "Electronica", "Ropa", "Hogar", "Juguetes"]
productos = [f"P{i:04d}" for i in range(1, 501)]
pagos = ["efectivo", "tarjeta", "transferencia", "vales"]

primero = True
for inicio in range(0, N, CHUNK):
    n = min(CHUNK, N - inicio)
    fechas = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    df = pd.DataFrame({
        "id_venta": np.arange(inicio + 1, inicio + n + 1),
        "fecha": fechas.strftime("%Y-%m-%d"),
        "hora": rng.integers(0, 24, n),
        "tienda": rng.choice(tiendas, n),
        "producto": rng.choice(productos, n),
        "categoria": rng.choice(categorias, n),
        "cantidad": rng.integers(1, 10, n),
        "precio_unitario": np.round(rng.uniform(5, 500, n), 2),
        "metodo_pago": rng.choice(pagos, n),
    })
    df.to_csv("data/ventas.csv", mode="w" if primero else "a", header=primero, index=False)
    primero = False
print("Listo: data/ventas.csv")
