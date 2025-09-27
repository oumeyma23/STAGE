#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour initialiser la table OTP dans la base de données
Utilise Flask-MySQLdb comme l'application principale
"""

from flask import Flask
from flask_mysqldb import MySQL

def create_otp_table():
    """Crée la table OTP dans la base de données"""
    
    # Configuration Flask temporaire
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'stagee'
    
    mysql = MySQL(app)
    
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            
            # Créer la table OTP
            create_table_query = """
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                otp_code VARCHAR(6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                INDEX idx_email (email),
                INDEX idx_expires_at (expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cur.execute(create_table_query)
            print("✅ Table 'otp_codes' créée avec succès")
            
            # Nettoyer les anciens codes expirés (optionnel)
            cleanup_query = "DELETE FROM otp_codes WHERE expires_at < NOW() OR is_used = TRUE"
            cur.execute(cleanup_query)
            deleted_rows = cur.rowcount
            print(f"🧹 {deleted_rows} anciens codes supprimés")
            
            mysql.connection.commit()
            cur.close()
            print("✅ Base de données initialisée pour le système OTP")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table OTP: {e}")
        print("💡 Assurez-vous que MySQL est démarré et que la base 'stagee' existe")

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données OTP...")
    create_otp_table()
