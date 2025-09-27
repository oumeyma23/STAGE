-- Table pour stocker les codes OTP temporaires
CREATE TABLE IF NOT EXISTS otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_used BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at)
);

-- Nettoyer les anciens codes expirés (optionnel)
-- DELETE FROM otp_codes WHERE expires_at < NOW() OR is_used = TRUE;
