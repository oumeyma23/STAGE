#!/usr/bin/env python3
"""
Test simple pour vérifier les composants
"""

print("🧪 Test des composants SecuriBank")
print("=" * 50)

# Test 1: Import du modèle de prédiction
try:
    from credit_prediction import CreditPredictor
    predictor = CreditPredictor()
    print("✅ CreditPredictor importé avec succès")
    print(f"   Modèle chargé: {'Oui' if predictor.model is not None else 'Non'}")
except Exception as e:
    print(f"❌ Erreur CreditPredictor: {e}")

# Test 2: Test de base de données
try:
    import MySQLdb
    conn = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='',
        db='stagee'
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"✅ Base de données accessible")
    print(f"   Tables trouvées: {len(tables)}")
    for table in tables:
        print(f"     - {table[0]}")
    
    # Vérifier la table Clients
    cursor.execute("SHOW TABLES LIKE 'Clients'")
    clients_table = cursor.fetchone()
    if clients_table:
        print("✅ Table Clients existe")
        cursor.execute("SELECT COUNT(*) FROM Clients")
        count = cursor.fetchone()[0]
        print(f"   Nombre d'enregistrements: {count}")
    else:
        print("⚠️ Table Clients n'existe pas")
    
    conn.close()
except Exception as e:
    print(f"❌ Erreur base de données: {e}")

# Test 3: Test simple de prédiction
try:
    if 'predictor' in locals() and predictor.model is not None:
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
        print("✅ Test de prédiction réussi")
        print(f"   Score prédit: {result.get('credit_score', 'N/A')}")
        print(f"   Approuvé: {'Oui' if result['approved'] else 'Non'}")
        print(f"   Message: {result['message']}")
    else:
        print("⚠️ Impossible de tester la prédiction (modèle non chargé)")
except Exception as e:
    print(f"❌ Erreur test prédiction: {e}")

print("\n🏁 Tests terminés")
