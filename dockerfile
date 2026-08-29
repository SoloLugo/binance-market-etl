FROM python:3.11-slim

# Evita que Python genere archivos .pyc innecesarios
ENV PYTHONDONTWRITEBYTECODE=1
# Obliga a Python a mostrar los logs en la consola en tiempo real
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt