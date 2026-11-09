#!/usr/bin/env bash
# Prepara lo que no se sube al repo: carpetas, llave SSH y .env
set -e
mkdir -p data output ssh docs
chmod 777 output
[ -f ssh/api_key ] || ssh-keygen -t ed25519 -N "" -f ssh/api_key -q
chmod 600 ssh/api_key
[ -f .env ] || cp .env.example .env
echo "Listo. Edita .env si quieres otra contraseña."
