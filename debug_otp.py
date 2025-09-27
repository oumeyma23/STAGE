#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug pour le système OTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer les fonctions de l'app
from app import generer_code_otp, sauvegarder_otp, envoyer_code_otp_inscription, mysql, app
from config_email import SMTP_CONFIG

def test_database_connection():
    """Test de connexion à la base de données"""
    print("🧪 Test de connexion à la base de données")
    print("=" * 50)
    
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SHOW TABLES LIKE 'otp_codes'")
            result = cur.fetchone()
            
            if result:
                print("✅ Table otp_codes existe")
                
                # Vérifier la structure de la table
                cur.execute("DESCRIBE otp_codes")
                columns = cur.fetchall()
                print("📋 Structure de la table:")
                for column in columns:
                    print(f"   - {column[0]} ({column[1]})")
                    
            else:
                print("❌ Table otp_codes n'existe pas")
                print("💡 Créez la table avec le script create_otp_table.sql")
                
            cur.close()
            return result is not None
            
    except Exception as e:
        print(f"❌ Erreur de connexion DB: {e}")
        return False

def test_otp_functions():
    """Test des fonctions OTP individuellement"""
    print("\n🧪 Test des fonctions OTP")
    print("=" * 50)
    
    # Test 1: Génération de code
    try:
        code = generer_code_otp()
        print(f"✅ Génération de code: {code}")
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        return False
    
    # Test 2: Sauvegarde en base
    test_email = "debug@test.com"
    try:
        with app.app_context():
            success = sauvegarder_otp(test_email, code)
            print(f"{'✅' if success else '❌'} Sauvegarde en base: {success}")
            if not success:
                return False
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False
    
    # Test 3: Envoi d'email
    try:
        success = envoyer_code_otp_inscription(test_email, code, "Test User")
        print(f"{'✅' if success else '❌'} Envoi d'email: {success}")
        return success
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smtp_config():
    """Vérifier la configuration SMTP"""
    print("\n🧪 Vérification configuration SMTP")
    print("=" * 50)
    
    print(f"Serveur: {SMTP_CONFIG['server']}")
    print(f"Port: {SMTP_CONFIG['port']}")
    print(f"Email: {SMTP_CONFIG['email']}")
    print(f"TLS: {SMTP_CONFIG['use_tls']}")
    print(f"Mot de passe: {'***' + SMTP_CONFIG['password'][-4:] if SMTP_CONFIG['password'] else 'NON DÉFINI'}")
    
    # Vérifier que tous les champs sont remplis
    required_fields = ['server', 'port', 'email', 'password']
    missing_fields = [field for field in required_fields if not SMTP_CONFIG.get(field)]
    
    if missing_fields:
        print(f"❌ Champs manquants: {missing_fields}")
        return False
    else:
        print("✅ Configuration complète")
        return True

def create_otp_table_if_not_exists():
    """Créer la table OTP si elle n'existe pas"""
    print("\n🔧 Création de la table OTP si nécessaire")
    print("=" * 50)
    
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            
            # Créer la table
            create_table_sql = """
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
            """
            
            cur.execute(create_table_sql)
            mysql.connection.commit()
            cur.close()
            
            print("✅ Table otp_codes créée/vérifiée")
            return True
            
    except Exception as e:
        print(f"❌ Erreur création table: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Debug du système OTP SecuriBank")
    print("=" * 60)
    
    # 1. Vérifier la config SMTP
    if not test_smtp_config():
        print("\n❌ Configuration SMTP invalide - Arrêt du debug")
        sys.exit(1)
    
    # 2. Créer la table si nécessaire
    create_otp_table_if_not_exists()
    
    # 3. Tester la connexion DB
    if not test_database_connection():
        print("\n❌ Problème de base de données - Arrêt du debug")
        sys.exit(1)
    
    # 4. Tester les fonctions OTP
    if test_otp_functions():
        print("\n🎉 Tous les tests réussis ! Le système OTP fonctionne.")
    else:
        print("\n❌ Échec des tests - Vérifiez les erreurs ci-dessus")
