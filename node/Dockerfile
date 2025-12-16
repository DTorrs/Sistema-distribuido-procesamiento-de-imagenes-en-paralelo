# Dockerfile para nodos de procesamiento
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para procesamiento de imágenes
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Regenerar archivos protobuf con la versión correcta
WORKDIR /app/grpc_server/protos
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. image_processing.proto
WORKDIR /app

# Crear directorio de salida
RUN mkdir -p output

# Exponer puerto gRPC
EXPOSE 50051

# Variables de entorno (se sobrescriben en docker-compose)
ENV NODE_ID=1
ENV GRPC_PORT=50051
ENV NODE_NAME=Node-1

# Comando de inicio
CMD ["sh", "-c", "python app.py"]
