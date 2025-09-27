#!/usr/bin/env python3
"""
Script pour créer un modèle Random Forest de test si le fichier n'existe pas
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def create_sample_data():
    """Crée des données d'exemple pour entraîner le modèle"""
    
    np.random.seed(42)
    n_samples = 1000
    
    # Générer des données synthétiques
    data = {
        'Month': np.random.choice(['January', 'February', 'March', 'April', 'May', 'June',
                                  'July', 'August', 'September', 'October', 'November', 'December'], n_samples),
        'Age': np.random.randint(18, 70, n_samples),
        'Occupation': np.random.choice(['Engineer', 'Teacher', 'Doctor', 'Lawyer', 'Manager', 
                                       'Accountant', 'Developer', 'Other'], n_samples),
        'Annual_Income': np.random.normal(60000, 25000, n_samples).clip(20000, 200000),
        'Monthly_Inhand_Salary': np.random.normal(5000, 2000, n_samples).clip(1500, 15000),
        'Num_Bank_Accounts': np.random.randint(1, 6, n_samples),
        'Num_Credit_Card': np.random.randint(0, 8, n_samples),
        'Interest_Rate': np.random.normal(12, 4, n_samples).clip(5, 25),
        'Num_of_Loan': np.random.randint(0, 5, n_samples),
        'Type_of_Loan': np.random.choice(['Auto Loan', 'Personal Loan', 'Home Equity Loan', 
                                         'Mortgage Loan', 'Student Loan', 'Not Specified'], n_samples),
        'Delay_from_due_date': np.random.exponential(5, n_samples).astype(int).clip(0, 60),
        'Num_of_Delayed_Payment': np.random.poisson(2, n_samples).clip(0, 20),
        'Changed_Credit_Limit': np.random.normal(0, 1000, n_samples),
        'Num_Credit_Inquiries': np.random.poisson(3, n_samples).clip(0, 15),
        'Credit_Mix': np.random.choice(['Standard', 'Good', 'Bad'], n_samples, p=[0.5, 0.3, 0.2]),
        'Outstanding_Debt': np.random.exponential(5000, n_samples).clip(0, 50000),
        'Credit_Utilization_Ratio': np.random.normal(30, 15, n_samples).clip(0, 100),
        'Credit_History_Age': np.random.exponential(8, n_samples).clip(0, 30),
        'Payment_of_Min_Amount': np.random.choice(['Yes', 'No', 'NM'], n_samples, p=[0.6, 0.3, 0.1]),
        'Total_EMI_per_month': np.random.exponential(800, n_samples).clip(0, 5000),
        'Amount_invested_monthly': np.random.exponential(500, n_samples).clip(0, 3000),
        'Payment_Behaviour': np.random.choice([
            'High_spent_Small_value_payments', 'Low_spent_Large_value_payments',
            'High_spent_Medium_value_payments', 'Low_spent_Medium_value_payments',
            'High_spent_Large_value_payments', 'Low_spent_Small_value_payments'
        ], n_samples),
        'Monthly_Balance': np.random.normal(2000, 1500, n_samples).clip(-1000, 10000)
    }
    
    df = pd.DataFrame(data)
    
    # Calculer le Credit Score basé sur plusieurs facteurs
    credit_score = 300 + (
        (df['Annual_Income'] / 1000) * 2 +
        (df['Age'] - 18) * 3 +
        (100 - df['Credit_Utilization_Ratio']) * 2 +
        df['Credit_History_Age'] * 10 +
        (df['Num_Bank_Accounts'] * 20) +
        np.where(df['Payment_of_Min_Amount'] == 'Yes', 50, 0) +
        np.where(df['Credit_Mix'] == 'Good', 30, np.where(df['Credit_Mix'] == 'Bad', -30, 0)) +
        np.random.normal(0, 50, n_samples)  # Bruit aléatoire
    ).clip(300, 850)
    
    df['Credit_Score'] = credit_score.astype(int)
    
    return df

def encode_categorical_features(df):
    """Encode les variables catégorielles"""
    
    # Copie du DataFrame
    df_encoded = df.copy()
    
    # Encodage manuel pour correspondre à notre système
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df_encoded['Month'] = df_encoded['Month'].map(month_mapping)
    
    occupation_mapping = {
        'Engineer': 1, 'Teacher': 2, 'Doctor': 3, 'Lawyer': 4, 'Manager': 5,
        'Accountant': 6, 'Developer': 7, 'Other': 8
    }
    df_encoded['Occupation'] = df_encoded['Occupation'].map(occupation_mapping)
    
    loan_type_mapping = {
        'Auto Loan': 1, 'Personal Loan': 2, 'Home Equity Loan': 3,
        'Mortgage Loan': 4, 'Student Loan': 5, 'Not Specified': 6
    }
    df_encoded['Type_of_Loan'] = df_encoded['Type_of_Loan'].map(loan_type_mapping)
    
    credit_mix_mapping = {'Standard': 1, 'Good': 2, 'Bad': 3}
    df_encoded['Credit_Mix'] = df_encoded['Credit_Mix'].map(credit_mix_mapping)
    
    payment_min_mapping = {'Yes': 1, 'No': 0, 'NM': 2}
    df_encoded['Payment_of_Min_Amount'] = df_encoded['Payment_of_Min_Amount'].map(payment_min_mapping)
    
    payment_behaviour_mapping = {
        'High_spent_Small_value_payments': 1,
        'Low_spent_Large_value_payments': 2,
        'High_spent_Medium_value_payments': 3,
        'Low_spent_Medium_value_payments': 4,
        'High_spent_Large_value_payments': 5,
        'Low_spent_Small_value_payments': 6
    }
    df_encoded['Payment_Behaviour'] = df_encoded['Payment_Behaviour'].map(payment_behaviour_mapping)
    
    return df_encoded

def create_random_forest_model():
    """Crée et sauvegarde un modèle Random Forest"""
    
    print("🌲 Création d'un modèle Random Forest pour la prédiction de Credit Score")
    print("=" * 70)
    
    # Vérifier si le modèle existe déjà
    if os.path.exists('random_forest.pkl'):
        print("✅ Le modèle random_forest.pkl existe déjà")
        return True
    
    print("📊 Génération des données d'entraînement...")
    df = create_sample_data()
    
    print(f"📈 Données générées: {df.shape[0]} échantillons, {df.shape[1]} colonnes")
    print(f"📊 Statistiques du Credit Score:")
    print(f"   Min: {df['Credit_Score'].min()}")
    print(f"   Max: {df['Credit_Score'].max()}")
    print(f"   Moyenne: {df['Credit_Score'].mean():.1f}")
    print(f"   Médiane: {df['Credit_Score'].median():.1f}")
    
    # Encoder les variables catégorielles
    print("\n🔧 Encodage des variables catégorielles...")
    df_encoded = encode_categorical_features(df)
    
    # Préparer les features et le target
    feature_columns = [
        'Month', 'Age', 'Occupation', 'Annual_Income', 'Monthly_Inhand_Salary',
        'Num_Bank_Accounts', 'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 
        'Type_of_Loan', 'Delay_from_due_date', 'Num_of_Delayed_Payment', 
        'Changed_Credit_Limit', 'Num_Credit_Inquiries', 'Credit_Mix', 
        'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Credit_History_Age',
        'Payment_of_Min_Amount', 'Total_EMI_per_month', 'Amount_invested_monthly', 
        'Payment_Behaviour', 'Monthly_Balance'
    ]
    
    X = df_encoded[feature_columns]
    y = df_encoded['Credit_Score']
    
    print(f"📋 Features utilisées: {len(feature_columns)} colonnes")
    print(f"🎯 Target: Credit_Score")
    
    # Diviser les données
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"\n🔄 Division des données:")
    print(f"   Entraînement: {X_train.shape[0]} échantillons")
    print(f"   Test: {X_test.shape[0]} échantillons")
    
    # Créer et entraîner le modèle
    print("\n🌲 Entraînement du modèle Random Forest...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Évaluer le modèle
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"📊 Performance du modèle:")
    print(f"   Score d'entraînement (R²): {train_score:.3f}")
    print(f"   Score de test (R²): {test_score:.3f}")
    
    # Sauvegarder le modèle
    print("\n💾 Sauvegarde du modèle...")
    joblib.dump(model, 'random_forest.pkl')
    
    print("✅ Modèle Random Forest créé et sauvegardé avec succès!")
    print(f"📁 Fichier: random_forest.pkl")
    
    # Test rapide
    print("\n🧪 Test rapide du modèle...")
    sample_prediction = model.predict(X_test[:1])[0]
    actual_value = y_test.iloc[0]
    print(f"   Prédiction: {sample_prediction:.0f}")
    print(f"   Valeur réelle: {actual_value}")
    print(f"   Différence: {abs(sample_prediction - actual_value):.0f}")
    
    return True

if __name__ == "__main__":
    success = create_random_forest_model()
    if success:
        print("\n🎉 Modèle prêt à être utilisé!")
    else:
        print("\n❌ Échec de la création du modèle")
