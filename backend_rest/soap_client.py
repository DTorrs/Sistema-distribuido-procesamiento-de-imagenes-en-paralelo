# Archivo: backend_rest/soap_client.py
# CLIENTE SOAP - Traduce REST/JSON a SOAP/XML

import requests
import xml.etree.ElementTree as ET
import json
import gzip
import base64

class SOAPClient:
    """Cliente que traduce peticiones REST a SOAP"""
    
    def __init__(self, soap_url):
        self.soap_url = soap_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8'
        })
        
        # Namespaces para parsear respuestas
        self.namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://example.org/ImageProcessingService.wsdl'
        }
    
    def register(self, username, password, email, first_name=None, last_name=None):
        """Registrar usuario"""
        
        # Construir XML SOAP
        first_name_xml = f'<first_name>{first_name}</first_name>' if first_name else ''
        last_name_xml = f'<last_name>{last_name}</last_name>' if last_name else ''
        
        soap_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <RegisterRequest xmlns="http://example.org/ImageProcessingService.wsdl">
      <username>{username}</username>
      <password>{password}</password>
      <email>{email}</email>
      {first_name_xml}
      {last_name_xml}
    </RegisterRequest>
  </soap:Body>
</soap:Envelope>'''
        
        print(f"[SOAP CLIENT] Enviando RegisterRequest a {self.soap_url}")
        
        try:
            response = self.session.post(self.soap_url, data=soap_envelope)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                success = root.find('.//ns:success', self.namespaces).text == 'true'
                message = root.find('.//ns:message', self.namespaces).text
                user_id = int(root.find('.//ns:user_id', self.namespaces).text)
                
                return success, {
                    'success': success,
                    'user_id': user_id,
                    'message': message
                }
            else:
                return False, {
                    'success': False,
                    'message': f'Error HTTP: {response.status_code}'
                }
                
        except Exception as e:
            print(f"[SOAP CLIENT] Error: {e}")
            return False, {
                'success': False,
                'message': f'Error de comunicación: {str(e)}'
            }
    
    def login(self, username, password):
        """Login de usuario"""
        
        soap_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <LoginRequest xmlns="http://example.org/ImageProcessingService.wsdl">
      <username>{username}</username>
      <password>{password}</password>
    </LoginRequest>
  </soap:Body>
</soap:Envelope>'''
        
        print(f"[SOAP CLIENT] Enviando LoginRequest")
        
        try:
            response = self.session.post(self.soap_url, data=soap_envelope)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                success = root.find('.//ns:success', self.namespaces).text == 'true'
                message = root.find('.//ns:message', self.namespaces).text
                session_token = root.find('.//ns:session_token', self.namespaces).text
                user_id = int(root.find('.//ns:user_id', self.namespaces).text)
                
                return success, {
                    'success': success,
                    'token': session_token,
                    'user_id': user_id,
                    'message': message
                }
            else:
                return False, {
                    'success': False,
                    'message': f'Error HTTP: {response.status_code}'
                }
                
        except Exception as e:
            print(f"[SOAP CLIENT] Error: {e}")
            return False, {
                'success': False,
                'message': f'Error de comunicación: {str(e)}'
            }
    
    def logout(self, token):
        """Logout de usuario"""
        
        soap_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <LogoutRequest xmlns="http://example.org/ImageProcessingService.wsdl">
      <session_token>{token}</session_token>
    </LogoutRequest>
  </soap:Body>
</soap:Envelope>'''
        
        print(f"[SOAP CLIENT] Enviando LogoutRequest")
        
        try:
            response = self.session.post(self.soap_url, data=soap_envelope)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                success = root.find('.//ns:success', self.namespaces).text == 'true'
                message = root.find('.//ns:message', self.namespaces).text
                
                return success, {
                    'success': success,
                    'message': message
                }
            else:
                return False, {
                    'success': False,
                    'message': f'Error HTTP: {response.status_code}'
                }
                
        except Exception as e:
            print(f"[SOAP CLIENT] Error: {e}")
            return False, {
                'success': False,
                'message': f'Error de comunicación: {str(e)}'
            }
    
    def process_batch(self, token, batch_name, images):
        """Procesar lote de imágenes"""
        
        print(f"[SOAP CLIENT] Preparando lote con {len(images)} imágenes")
        
        # Convertir a JSON
        images_json = json.dumps(images)
        print(f"[SOAP CLIENT] JSON generado: {len(images_json)} bytes ({len(images_json)/1024:.1f} KB)")
        
        # ✅ OPTIMIZACIÓN: SIN GZIP - Solo base64 (mucho más rápido)
        images_json_base64 = base64.b64encode(images_json.encode('utf-8')).decode('utf-8')
        print(f"[SOAP CLIENT] Tamaño final: {len(images_json_base64)} bytes ({len(images_json_base64)/1024:.1f} KB)")
        
        # Construir XML SOAP
        soap_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ProcessBatchRequest xmlns="http://example.org/ImageProcessingService.wsdl">
      <session_token>{token}</session_token>
      <batch_name>{batch_name}</batch_name>
      <images_json>{images_json_base64}</images_json>
    </ProcessBatchRequest>
  </soap:Body>
</soap:Envelope>'''
        
        print(f"[SOAP CLIENT] Enviando ProcessBatchRequest")
        
        try:
            response = self.session.post(self.soap_url, data=soap_envelope)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                success = root.find('.//ns:success', self.namespaces).text == 'true'
                message = root.find('.//ns:message', self.namespaces).text
                batch_id = int(root.find('.//ns:batch_id', self.namespaces).text)
                total_images = int(root.find('.//ns:total_images', self.namespaces).text)
                processed_images = int(root.find('.//ns:processed_images', self.namespaces).text)
                failed_images = int(root.find('.//ns:failed_images', self.namespaces).text)
                processing_time_ms = int(root.find('.//ns:processing_time_ms', self.namespaces).text)
                
                # ⭐ NUEVO: Parsear download_url
                download_url_elem = root.find('.//ns:download_url', self.namespaces)
                download_url = download_url_elem.text if download_url_elem is not None else ''
                
                print(f"[SOAP CLIENT] Lote procesado exitosamente")
                print(f"[SOAP CLIENT] Download URL: {download_url}")
                
                return success, {
                    'success': success,
                    'message': message,
                    'batch_id': batch_id,
                    'total_images': total_images,
                    'processed_images': processed_images,
                    'failed_images': failed_images,
                    'processing_time_ms': processing_time_ms,
                    'download_url': download_url  # ⭐ NUEVO
                }
            else:
                return False, {
                    'success': False,
                    'message': f'Error HTTP: {response.status_code}'
                }
                
        except Exception as e:
            print(f"[SOAP CLIENT] Error: {e}")
            import traceback
            traceback.print_exc()
            return False, {
                'success': False,
                'message': f'Error de comunicación: {str(e)}'
            }
    
    def get_nodes_metrics(self):
        """Obtener métricas de nodos vía SOAP"""
        soap_envelope = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetNodesMetricsRequest xmlns="http://example.org/ImageProcessingService.wsdl">
    </GetNodesMetricsRequest>
  </soap:Body>
</soap:Envelope>'''
        
        print(f"[SOAP CLIENT] Enviando GetNodesMetricsRequest")
        
        try:
            response = self.session.post(self.soap_url, data=soap_envelope)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                success = root.find('.//ns:success', self.namespaces).text == 'true'
                nodes_json = root.find('.//ns:nodes_json', self.namespaces).text
                
                if success:
                    nodes_list = json.loads(nodes_json)
                    return success, {'nodes': nodes_list}
                else:
                    return False, {'nodes': []}
            else:
                return False, {'nodes': []}
                
        except Exception as e:
            print(f"[SOAP CLIENT] Error: {e}")
            import traceback
            traceback.print_exc()
            return False, {'nodes': []}
    
    def get_batch_metrics(self, batch_id):
        """Obtener métricas de lote vía SOAP"""
        soap_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBatchMetricsRequest xmlns="http://example.org/ImageProcessingService.wsdl">
      <batch_id>{batch_id}</batch_id>
    </GetBatchMetricsRequest>
  </soap:Body>
</soap:Envelope>'''
        
        print(f"[SOAP CLIENT] Enviando GetBatchMetricsRequest para batch {batch_id}")
        
        try:
            response = self.session.post(self.soap_url, data=soap_envelope)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                success = root.find('.//ns:success', self.namespaces).text == 'true'
                metrics_json = root.find('.//ns:metrics_json', self.namespaces).text
                
                if success:
                    return success, json.loads(metrics_json)
                else:
                    return False, {}
            else:
                return False, {}
                
        except Exception as e:
            print(f"[SOAP CLIENT] Error: {e}")
            return False, {}