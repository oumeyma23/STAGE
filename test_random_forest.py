#!/usr/bin/env python3
"""
Script de test pour le nouveau modèle Random Forest
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credit_prediction import CreditPredictor

def test_random_forest_model():
    """Test du modèle Random Forest avec des données d'exemple"""
    
    print("🧪 Test du modèle Random Forest pour la prédiction de Credit Score")
    print("=" * 70)
    
    # Initialiser le prédicteur
    predictor = CreditPredictor()
    
    if predictor.model is None:
        print("❌ Modèle non chargé. Vérifiez que random_forest.pkl existe.")
        return False
    
    # Données de test d'exemple
    test_data = {
        'Month': 'January',
        'Age': '35',
        'Occupation': 'Engineer',
        'Annual_Income': '75000',
        'Monthly_Inhand_Salary': '6000',
        'Num_Bank_Accounts': '2',
        'Num_Credit_Card': '3',
        'Interest_Rate': '12.5',
        'Num_of_Loan': '1',
        'Type_of_Loan': 'Personal Loan',
        'Delay_from_due_date': '5',
        'Num_of_Delayed_Payment': '2',
        'Changed_Credit_Limit': '1000',
        'Num_Credit_Inquiries': '3',
        'Credit_Mix': 'Good',
        'Outstanding_Debt': '5000',
        'Credit_Utilization_Ratio': '25.5',
        'Credit_History_Age': '8.5',
        'Payment_of_Min_Amount': 'Yes',
        'Total_EMI_per_month': '1200',
        'Amount_invested_monthly': '500',
        'Payment_Behaviour': 'Low_spent_Medium_value_payments',
        'Monthly_Balance': '2000'
    }
    
    print("📋 Données de test:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    print("\n🔮 Prédiction en cours...")
    
    # Faire la prédiction
    try:
        result = predictor.predict_credit_approval(test_data)
        
        print("\n📊 Résultats de la prédiction:")
        print("-" * 50)
        print(f"✅ Score de crédit prédit: {result.get('credit_score', 'N/A'):.0f}")
        print(f"📈 Probabilité d'approbation: {result['probability']:.1%}")
        print(f"⚠️  Niveau de risque: {result['risk_level']}")
        print(f"🎯 Décision: {'APPROUVÉ' if result['approved'] else 'REFUSÉ'}")
        print(f"💬 Message: {result['message']}")
        
        if result.get('details'):
            print("\n🔍 Détails de l'analyse:")
            details = result['details']
            for key, value in details.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n✅ Test réussi!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_scenarios():
    """Test avec plusieurs scénarios différents"""
    
    print("\n" + "=" * 70)
    print("🧪 Test de plusieurs scénarios")
    print("=" * 70)
    
    predictor = CreditPredictor()
    
    scenarios = [
        {
            'name': 'Client Excellent',
            'data': {
                'Month': 'March',
                'Age': '40',
                'Occupation': 'Doctor',
                'Annual_Income': '120000',
                'Monthly_Inhand_Salary': '10000',
                'Num_Bank_Accounts': '3',
                'Num_Credit_Card': '2',
                'Interest_Rate': '8.0',
                'Num_of_Loan': '0',
                'Type_of_Loan': 'Not Specified',
                'Delay_from_due_date': '0',
                'Num_of_Delayed_Payment': '0',
                'Changed_Credit_Limit': '0',
                'Num_Credit_Inquiries': '1',
                'Credit_Mix': 'Good',
                'Outstanding_Debt': '0',
                'Credit_Utilization_Ratio': '15.0',
                'Credit_History_Age': '15.0',
                'Payment_of_Min_Amount': 'Yes',
                'Total_EMI_per_month': '0',
                'Amount_invested_monthly': '2000',
                'Payment_Behaviour': 'Low_spent_Large_value_payments',
                'Monthly_Balance': '5000'
            }
        },
        {
            'name': 'Client Risqué',
            'data': {
                'Month': 'June',
                'Age': '25',
                'Occupation': 'Other',
                'Annual_Income': '25000',
                'Monthly_Inhand_Salary': '2000',
                'Num_Bank_Accounts': '1',
                'Num_Credit_Card': '5',
                'Interest_Rate': '18.0',
                'Num_of_Loan': '3',
                'Type_of_Loan': 'Payday Loan',
                'Delay_from_due_date': '30',
                'Num_of_Delayed_Payment': '8',
                'Changed_Credit_Limit': '-500',
                'Num_Credit_Inquiries': '10',
                'Credit_Mix': 'Bad',
                'Outstanding_Debt': '15000',
                'Credit_Utilization_Ratio': '85.0',
                'Credit_History_Age': '2.0',
                'Payment_of_Min_Amount': 'No',
                'Total_EMI_per_month': '1500',
                'Amount_invested_monthly': '0',
                'Payment_Behaviour': 'High_spent_Small_value_payments',
                'Monthly_Balance': '100'
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 Scénario: {scenario['name']}")
        print("-" * 30)
        
        result = predictor.predict_credit_approval(scenario['data'])
        
        print(f"Score prédit: {result.get('credit_score', 'N/A'):.0f}")
        print(f"Décision: {'✅ APPROUVÉ' if result['approved'] else '❌ REFUSÉ'}")
        print(f"Risque: {result['risk_level']}")
        print(f"Probabilité: {result['probability']:.1%}")

if __name__ == "__main__":
    success = test_random_forest_model()
    
    if success:
        test_multiple_scenarios()
    
    print("\n" + "=" * 70)
    print("🏁 Tests terminés")
