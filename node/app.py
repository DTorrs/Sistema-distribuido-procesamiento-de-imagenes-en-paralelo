# Archivo: node/app.py
# NODO CON HEARTBEAT

import time
import os
import threading
import requests
import psutil
from grpc_server.server import serve

# Variables de entorno
GRPC_PORT = int(os.getenv('GRPC_PORT', 50051))
NODE_ID = int(os.getenv('NODE_ID', 1))
SOAP_SERVER_URL = os.getenv('SOAP_SERVER_URL', 'http://localhost:8000')  # ← Cambio a SOAP Server

def get_system_metrics():
    """Obtener métricas del sistema usando psutil"""
    try:
        cpu_count = psutil.cpu_count(logical=True)
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent
        
        return {
            'cpu_cores': cpu_count,
            'ram_gb': ram_gb,
            'cpu_usage': cpu_percent,
            'ram_usage': ram_percent
        }
    except Exception as e:
        print(f"[NODO {NODE_ID}] Error obteniendo métricas: {e}")
        return {
            'cpu_cores': None,
            'ram_gb': None,
            'cpu_usage': 0,
            'ram_usage': 0
        }

def send_heartbeat():
    """Envía heartbeat al SOAP Server (no directamente a DB Service)"""
    while True:
        try:
            metrics = get_system_metrics()
            
            # Construir SOAP XML
            soap_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <NodeHeartbeatRequest xmlns="http://example.org/ImageProcessingService.wsdl">
      <node_id>{NODE_ID}</node_id>
      <ip_address>localhost</ip_address>
      <port>{GRPC_PORT}</port>
      <cpu_cores>{metrics['cpu_cores']}</cpu_cores>
      <ram_gb>{metrics['ram_gb']}</ram_gb>
      <current_load>0</current_load>
      <status>active</status>
    </NodeHeartbeatRequest>
  </soap:Body>
</soap:Envelope>'''
            
            response = requests.post(
                f'{SOAP_SERVER_URL}/soap',
                data=soap_envelope,
                headers={'Content-Type': 'text/xml'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"[NODO {NODE_ID}] Heartbeat enviado ✓ (CPU: {metrics['cpu_usage']:.1f}%, RAM: {metrics['ram_usage']:.1f}%)")
            else:
                print(f"[NODO {NODE_ID}] Error en heartbeat: {response.status_code}")
        except Exception as e:
            print(f"[NODO {NODE_ID}] Error enviando heartbeat: {e}")
        
        time.sleep(30)  # Cada 30 segundos

def main():
    """Función principal del nodo"""
    
    # Crear directorio de salida
    os.makedirs('output', exist_ok=True)
    
    print("\n" + "="*60)
    print(f"NODO DE PROCESAMIENTO #{NODE_ID}")
    print("="*60)
    print(f"Puerto gRPC:   {GRPC_PORT}")
    print(f"SOAP Server:   {SOAP_SERVER_URL}")
    print("="*60 + "\n")
    
    # Iniciar servidor gRPC
    server = serve(port=GRPC_PORT)
    
    # Iniciar thread de heartbeat
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()
    print(f"[NODO {NODE_ID}] Thread de heartbeat iniciado\n")
    
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)
        print(f"\n[NODO {NODE_ID}] Detenido.")

if __name__ == "__main__":
    main()