# Dockerfile para db_service
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV DB_HOST=mysql
ENV DB_PORT=3306
ENV REST_HOST=0.0.0.0
ENV REST_PORT=5000

# Comando de inicio
CMD ["python", "app.py"]
