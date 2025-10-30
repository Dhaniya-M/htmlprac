-- Create the database
CREATE DATABASE IF NOT EXISTS agri_db;
USE agri_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mobile VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Soil tests table
CREATE TABLE IF NOT EXISTS soil_tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ph_level DECIMAL(4,2),
    nitrogen_level DECIMAL(5,2),
    phosphorus_level DECIMAL(5,2),
    potassium_level DECIMAL(5,2),
    organic_matter DECIMAL(5,2),
    moisture_content DECIMAL(5,2),
    recommendations TEXT,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Market prices table
CREATE TABLE IF NOT EXISTS market_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    market_location VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Pest detection history
CREATE TABLE IF NOT EXISTS pest_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    pest_name VARCHAR(100),
    confidence_score DECIMAL(5,2),
    recommendations TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Weather alerts
CREATE TABLE IF NOT EXISTS weather_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20),
    alert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_soil_tests_user_id ON soil_tests(user_id);
CREATE INDEX idx_pest_detections_user_id ON pest_detections(user_id);
CREATE INDEX idx_weather_alerts_user_id ON weather_alerts(user_id);