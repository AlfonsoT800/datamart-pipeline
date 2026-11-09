#!/usr/bin/env python3
import sys

# Posiciones de columna (ajustar si el CSV del profe es distinto)
IDX_FECHA, IDX_CATEGORIA, IDX_CANTIDAD, IDX_PRECIO = 1, 5, 6, 7
NUM_COLS = 9

for linea in sys.stdin:
    campos = linea.strip().split(",")
    # Ignora encabezado y lineas mal formadas sin tumbar el job
    if len(campos) != NUM_COLS or campos[0] == "id_venta":
        continue
    try:
        fecha = campos[IDX_FECHA]
        if len(fecha) != 10 or fecha[4] != "-":
            continue
        mes = fecha[:7]                      # AAAA-MM
        categoria = campos[IDX_CATEGORIA].strip()
        if not categoria:
            continue
        # Centavos enteros: evita errores de punto flotante
        centavos = int(campos[IDX_CANTIDAD]) * round(float(campos[IDX_PRECIO]) * 100)
    except (ValueError, IndexError):
        continue
    print(f"{categoria}|{mes}\t{centavos}")
