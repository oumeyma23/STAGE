#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test SMTP pour diagnostiquer les problèmes d'envoi d'email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import SMTP_CONFIG

def test_smtp_connection():
    """Test de connexion SMTP avec diagnostic détaillé"""
    print("🧪 Test de connexion SMTP")
    print("=" * 50)
    print(f"Serveur: {SMTP_CONFIG['server']}")
    print(f"Port: {SMTP_CONFIG['port']}")
    print(f"Email: {SMTP_CONFIG['email']}")
    print(f"TLS: {SMTP_CONFIG['use_tls']}")
    print("=" * 50)
    
    try:
        print("🔗 Connexion au serveur SMTP...")
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.set_debuglevel(1)  # Debug détaillé
        
        if SMTP_CONFIG['use_tls']:
            print("🔐 Activation TLS...")
            server.starttls()
        
        print("🔑 Test d'authentification...")
        server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
        
        print("✅ Connexion SMTP réussie!")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erreur d'authentification: {e}")
        print("💡 Vérifiez votre email et mot de passe")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ Erreur de connexion: {e}")
        print("💡 Vérifiez le serveur SMTP et le port")
        return False
    except Exception as e:
        print(f"❌ Erreur: {type(e).__name__}: {e}")
        return False

def test_send_email():
    """Test d'envoi d'email"""
    print("\n📧 Test d'envoi d'email")
    print("=" * 30)
    
    # Email de test vers l'expéditeur
    destinataire = SMTP_CONFIG['email']  # Envoyer vers soi-même
    
    subject = "Test SMTP - SecuriBank"
    body = """
    Ceci est un email de test pour vérifier la configuration SMTP.
    
    Si vous recevez cet email, la configuration fonctionne correctement.
    
    Test effectué depuis le système AML SecuriBank.
    """
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['email']
    msg['To'] = destinataire
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.set_debuglevel(1)
        
        if SMTP_CONFIG['use_tls']:
            server.starttls()
        
        server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
        server.sendmail(SMTP_CONFIG['email'], destinataire, msg.as_string())
        server.quit()
        
        print(f"✅ Email de test envoyé vers {destinataire}")
        print("📬 Vérifiez votre boîte de réception")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'envoi: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Diagnostic SMTP pour SecuriBank")
    print("=" * 40)
    
    # Test 1: Connexion
    if test_smtp_connection():
        print("\n" + "="*40)
        # Test 2: Envoi d'email
        test_send_email()
    else:
        print("\n❌ Impossible de continuer - problème de connexion SMTP")
    
    print("\n🏁 Test terminé")
