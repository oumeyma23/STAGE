#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test spécifique pour la détection d'inversion de noms
"""

from AML import check_name, check_word_inversion

def test_inversion_detection():
    """Test de la détection d'inversion de mots"""
    print("🧪 Test de détection d'inversion de noms")
    print("=" * 50)
    
    # Test de la fonction d'inversion directement
    test_cases = [
        ("sokkeh oumeyma", "oumeyma sokkeh"),
        ("john smith", "smith john"),
        ("ahmed ben", "ben ahmed"),
        ("marie dupont", "dupont marie")
    ]
    
    print("\n🔄 Test de la fonction check_word_inversion:")
    for input_name, target_name in test_cases:
        result = check_word_inversion(input_name.lower(), target_name.lower())
        print(f"'{input_name}' vs '{target_name}' → {result}")
    
    print("\n" + "=" * 50)
    
    # Test avec la fonction complète AML
    print("\n🔍 Test avec la base AML complète:")
    test_names = [
        "sokkeh oumeyma",
        "oumeyma sokkeh"
    ]
    
    for name in test_names:
        print(f"\n📝 Test pour: '{name}'")
        result = check_name(name)
        
        if not result.empty:
            print(f"✅ DÉTECTÉ! Nombre de matches: {len(result)}")
            if 'Full Name' in result.columns:
                print(f"Noms trouvés: {result['Full Name'].tolist()}")
        else:
            print(f"❌ Non détecté")

if __name__ == "__main__":
    test_inversion_detection()
