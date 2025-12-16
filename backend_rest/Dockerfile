# Dockerfile para backend_rest
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 3000

# Variables de entorno
ENV REST_HOST=0.0.0.0
ENV REST_PORT=3000

# Comando de inicio
CMD ["python", "app.py"]
