-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS image_processing_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE image_processing_system;

-- Tabla de usuarios
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de nodos de procesamiento
CREATE TABLE processing_nodes (
    node_id INT AUTO_INCREMENT PRIMARY KEY,
    node_name VARCHAR(100) NOT NULL UNIQUE,
    ip_address VARCHAR(45) NOT NULL,
    port INT NOT NULL,
    status ENUM('active', 'inactive', 'error') DEFAULT 'active',
    last_heartbeat TIMESTAMP NULL,
    cpu_cores INT,
    ram_gb INT,
    weight INT DEFAULT 1,
    current_load INT DEFAULT 0,
    max_concurrent_jobs INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Catálogo de transformaciones disponibles
CREATE TABLE transformations (
    transformation_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    parameters_schema JSON,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de solicitudes de lotes
CREATE TABLE batch_requests (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    batch_name VARCHAR(100),
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    total_images INT DEFAULT 0,
    processed_images INT DEFAULT 0,
    output_format ENUM('jpg', 'png', 'tif') DEFAULT 'jpg',
    compression_type ENUM('zip', 'tar', 'none') DEFAULT 'zip',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Tabla de imágenes
CREATE TABLE images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    file_size INT,
    width INT,
    height INT,
    format VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    FOREIGN KEY (batch_id) REFERENCES batch_requests(batch_id)
);

-- Tabla de transformaciones solicitadas por imagen
CREATE TABLE image_transformations (
    image_transformation_id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    transformation_id INT NOT NULL,
    parameters JSON,
    execution_order INT NOT NULL,
    FOREIGN KEY (image_id) REFERENCES images(image_id),
    FOREIGN KEY (transformation_id) REFERENCES transformations(transformation_id)
);

-- Tabla de resultados procesados
CREATE TABLE processed_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    node_id INT NOT NULL,
    result_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    file_size INT,
    width INT,
    height INT,
    format VARCHAR(10),
    processing_time_ms INT,
    status ENUM('success', 'failed') DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (image_id) REFERENCES images(image_id),
    FOREIGN KEY (node_id) REFERENCES processing_nodes(node_id)
);

-- Tabla de logs de ejecución
CREATE TABLE execution_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NULL,
    batch_id INT NULL,
    image_id INT NULL,
    log_level ENUM('info', 'warning', 'error', 'debug') NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES processing_nodes(node_id),
    FOREIGN KEY (batch_id) REFERENCES batch_requests(batch_id),
    FOREIGN KEY (image_id) REFERENCES images(image_id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_batch_user ON batch_requests(user_id);
CREATE INDEX idx_image_batch ON images(batch_id);
CREATE INDEX idx_result_image ON processed_results(image_id);
CREATE INDEX idx_result_node ON processed_results(node_id);
CREATE INDEX idx_log_batch ON execution_logs(batch_id);
CREATE INDEX idx_log_image ON execution_logs(image_id);
CREATE INDEX idx_log_node ON execution_logs(node_id);
CREATE INDEX idx_image_transformation ON image_transformations(image_id, transformation_id);

-- Insertar las transformaciones disponibles
INSERT INTO transformations (name, description, parameters_schema) VALUES
('grayscale', 'Convertir imagen a escala de grises', '{}'),
('resize', 'Redimensionar imagen', '{"width": "int", "height": "int", "keep_aspect_ratio": "bool"}'),
('crop', 'Recortar imagen', '{"x": "int", "y": "int", "width": "int", "height": "int"}'),
('rotate', 'Rotar imagen', '{"angle": "float"}'),
('flip', 'Reflejar imagen', '{"direction": "string"}'),
('blur', 'Desenfocar imagen', '{"radius": "float"}'),
('brightness', 'Ajustar brillo', '{"factor": "float"}'),
('contrast', 'Ajustar contraste', '{"factor": "float"}'),
('watermark', 'Insertar marca de agua', '{"text": "string", "position": "string", "opacity": "float"}'),
('format_conversion', 'Convertir formato de imagen', '{"target_format": "string"}');

-- Insertar nodos de procesamiento para Docker
INSERT INTO processing_nodes 
(node_name, ip_address, port, status, cpu_cores, ram_gb, weight, current_load, max_concurrent_jobs) 
VALUES
('Node-1', 'node1', 50051, 'active', 4, 8, 1, 0, 5),
('Node-2', 'node2', 50052, 'active', 4, 8, 1, 0, 5),
('Node-3', 'node3', 50053, 'active', 4, 8, 1, 0, 5)
ON DUPLICATE KEY UPDATE 
    status = VALUES(status),
    weight = VALUES(weight),
    max_concurrent_jobs = VALUES(max_concurrent_jobs);

-- No insertar usuarios - el test los creará con el password correcto
