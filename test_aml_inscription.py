#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour la vérification AML lors de l'inscription
"""

from AML import check_name
import pandas as pd

def test_aml_verification():
    """Test de la fonction de vérification AML"""
    print("🧪 Test de la vérification AML lors de l'inscription")
    print("=" * 50)
    
    # Test avec des noms fictifs
    test_names = [
        "John Smith",
        "Ahmed Ben Ali", 
        "Mohamed Trabelsi",
        "Sarah Johnson",
        "Ali Hassan"
    ]
    
    for name in test_names:
        print(f"\n🔍 Test pour le nom: '{name}'")
        try:
            result = check_name(name)
            if not result.empty:
                print(f"🚨 ALERTE: '{name}' figure sur la liste rouge!")
                print("Colonnes disponibles:", result.columns.tolist())
                if 'Full Name' in result.columns:
                    print("Noms trouvés:", result['Full Name'].tolist())
            else:
                print(f"✅ '{name}' n'est pas sur la liste rouge")
        except Exception as e:
            print(f"❌ Erreur lors de la vérification de '{name}': {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

def test_email_simulation():
    """Simulation d'envoi d'email (sans vraiment envoyer)"""
    print("\n📧 Simulation d'envoi d'email")
    print("=" * 30)
    
    nom_test = "Test User"
    email_test = "test@example.com"
    
    print(f"📨 Email d'avertissement simulé pour:")
    print(f"   Nom: {nom_test}")
    print(f"   Email: {email_test}")
    print(f"   Sujet: Avertissement d'inscription - SecuriBank")
    print("✅ Simulation terminée")

if __name__ == "__main__":
    test_aml_verification()
    test_email_simulation()
