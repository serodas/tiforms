#!/bin/bash
set -e  # hace que el script falle si algo falla

echo "🧩 Generando /etc/odbc.ini desde la plantilla..."
envsubst < /etc/odbc.ini.template > /etc/odbc.ini

echo "📦 Ejecutando collectstatic..."
python manage.py collectstatic --noinput

echo "🚀 Iniciando aplicación..."
exec "$@"
