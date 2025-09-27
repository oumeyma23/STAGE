#!/usr/bin/env python3
"""
Test du chargement du modèle Random Forest
"""

import os
import sys

print("🧪 Test de chargement du modèle Random Forest")
print("=" * 50)

# Vérifier l'existence des fichiers
files_to_check = ['random_forest.pkl', 'random_forest_model.pkl', 'credit_model.pkl']

print("📁 Fichiers dans le répertoire:")
for file in files_to_check:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"  ✅ {file} ({size:,} bytes)")
    else:
        print(f"  ❌ {file} (non trouvé)")

print("\n🔧 Test d'import du CreditPredictor...")

try:
    from credit_prediction import CreditPredictor
    print("✅ Import réussi")
    
    # Créer une instance
    predictor = CreditPredictor()
    
    if predictor.model is not None:
        print("✅ Modèle chargé avec succès!")
        print(f"📊 Type de modèle: {type(predictor.model)}")
        
        # Test simple de prédiction
        print("\n🧪 Test de prédiction simple...")
        test_data = {
            'Month': 'January',
            'Age': '30',
            'Occupation': 'Engineer',
            'Annual_Income': '60000',
            'Monthly_Inhand_Salary': '5000',
            'Num_Bank_Accounts': '2',
            'Num_Credit_Card': '1',
            'Interest_Rate': '10',
            'Num_of_Loan': '0',
            'Type_of_Loan': 'Not Specified',
            'Delay_from_due_date': '0',
            'Num_of_Delayed_Payment': '0',
            'Changed_Credit_Limit': '0',
            'Num_Credit_Inquiries': '1',
            'Credit_Mix': 'Good',
            'Outstanding_Debt': '0',
            'Credit_Utilization_Ratio': '20',
            'Credit_History_Age': '5',
            'Payment_of_Min_Amount': 'Yes',
            'Total_EMI_per_month': '0',
            'Amount_invested_monthly': '500',
            'Payment_Behaviour': 'Low_spent_Medium_value_payments',
            'Monthly_Balance': '2000'
        }
        
        result = predictor.predict_credit_approval(test_data)
        print(f"✅ Prédiction réussie!")
        print(f"   Score de crédit: {result.get('credit_score', 'N/A')}")
        print(f"   Approuvé: {'Oui' if result.get('approved') else 'Non'}")
        print(f"   Message: {result.get('message', 'N/A')}")
        
    else:
        print("❌ Modèle non chargé")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Test terminé")
