#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le système OTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generer_code_otp, sauvegarder_otp, verifier_otp, envoyer_code_otp
import time

def test_otp_generation():
    """Test de génération de codes OTP"""
    print("🧪 Test de génération de codes OTP")
    print("=" * 40)
    
    for i in range(5):
        code = generer_code_otp()
        print(f"Code {i+1}: {code}")
        assert len(code) == 6, f"Code doit avoir 6 chiffres, reçu: {len(code)}"
        assert code.isdigit(), f"Code doit contenir seulement des chiffres: {code}"
    
    print("✅ Test de génération réussi")

def test_otp_workflow():
    """Test du workflow complet OTP"""
    print("\n🧪 Test du workflow OTP complet")
    print("=" * 40)
    
    test_email = "test@example.com"
    
    # 1. Générer et sauvegarder un code
    code_otp = generer_code_otp()
    print(f"1. Code généré: {code_otp}")
    
    success = sauvegarder_otp(test_email, code_otp)
    print(f"2. Sauvegarde: {'✅ Réussie' if success else '❌ Échouée'}")
    
    if not success:
        print("❌ Impossible de continuer le test - sauvegarde échouée")
        return
    
    # 2. Vérifier le code correct
    is_valid, message = verifier_otp(test_email, code_otp)
    print(f"3. Vérification code correct: {'✅ Valide' if is_valid else '❌ Invalide'} - {message}")
    
    # 3. Tenter de réutiliser le même code (doit échouer)
    is_valid, message = verifier_otp(test_email, code_otp)
    print(f"4. Réutilisation code: {'❌ Bloquée' if not is_valid else '✅ Autorisée (problème!)'} - {message}")
    
    # 4. Tester un code incorrect
    code_faux = "999999"
    sauvegarder_otp(test_email, generer_code_otp())  # Nouveau code
    is_valid, message = verifier_otp(test_email, code_faux)
    print(f"5. Code incorrect: {'❌ Rejeté' if not is_valid else '✅ Accepté (problème!)'} - {message}")
    
    print("✅ Test du workflow terminé")

def test_otp_expiration():
    """Test de l'expiration des codes (simulation)"""
    print("\n🧪 Test d'expiration des codes")
    print("=" * 40)
    
    test_email = "expiration@example.com"
    code_otp = generer_code_otp()
    
    print(f"Code généré: {code_otp}")
    sauvegarder_otp(test_email, code_otp)
    
    # Vérification immédiate (doit marcher)
    is_valid, message = verifier_otp(test_email, code_otp)
    print(f"Vérification immédiate: {'✅ Valide' if is_valid else '❌ Invalide'} - {message}")
    
    print("ℹ️ Note: Pour tester l'expiration réelle, modifiez temporairement la durée dans sauvegarder_otp()")

def test_email_sending():
    """Test d'envoi d'email (optionnel)"""
    print("\n🧪 Test d'envoi d'email OTP")
    print("=" * 40)
    
    test_email = input("Entrez votre email pour tester l'envoi (ou Entrée pour ignorer): ").strip()
    
    if not test_email:
        print("⏭️ Test d'email ignoré")
        return
    
    code_otp = generer_code_otp()
    print(f"Envoi du code {code_otp} vers {test_email}...")
    
    success = envoyer_code_otp(test_email, code_otp, "Testeur")
    print(f"Résultat: {'✅ Email envoyé' if success else '❌ Échec envoi'}")
    
    if success:
        print("📧 Vérifiez votre boîte mail!")

if __name__ == "__main__":
    print("🚀 Tests du système OTP SecuriBank")
    print("=" * 50)
    
    try:
        test_otp_generation()
        test_otp_workflow()
        test_otp_expiration()
        test_email_sending()
        
        print("\n🎉 Tous les tests terminés!")
        
    except Exception as e:
        print(f"\n❌ Erreur durant les tests: {e}")
        import traceback
        traceback.print_exc()
