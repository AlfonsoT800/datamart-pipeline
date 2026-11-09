#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict

ruta = sys.argv[1] if len(sys.argv) > 1 else "data/ventas.csv"
totales = defaultdict(int)

with open(ruta, newline="") as f:
    lector = csv.reader(f)
    next(lector, None)  # encabezado
    for c in lector:
        if len(c) != 9:
            continue
        try:
            fecha = c[1]
            if len(fecha) != 10 or fecha[4] != "-":
                continue
            categoria = c[5].strip()
            if not categoria:
                continue
            totales[f"{categoria}|{fecha[:7]}"] += int(c[6]) * round(float(c[7]) * 100)
        except (ValueError, IndexError):
            continue

for clave in sorted(totales):
    cts = totales[clave]
    print(f"{clave}\t{cts // 100}.{cts % 100:02d}")
