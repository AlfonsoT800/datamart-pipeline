#!/usr/bin/env python3
import sys

clave_actual, total = None, 0

def emitir(clave, centavos):
    print(f"{clave}\t{centavos // 100}.{centavos % 100:02d}")

for linea in sys.stdin:
    try:
        clave, valor = linea.rstrip("\n").split("\t")
        valor = int(valor)
    except ValueError:
        continue
    if clave == clave_actual:
        total += valor
    else:
        if clave_actual is not None:
            emitir(clave_actual, total)
        clave_actual, total = clave, valor

if clave_actual is not None:
    emitir(clave_actual, total)
