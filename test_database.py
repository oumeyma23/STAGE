#!/usr/bin/env python3
"""
Script de test pour vérifier la structure de la base de données
"""

import MySQLdb
import sys

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'stagee'
}

def test_database_connection():
    """Teste la connexion à la base de données"""
    try:
        conn = MySQLdb.connect(**DB_CONFIG)
        print("✅ Connexion à la base de données réussie")
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def check_table_exists(cursor, table_name):
    """Vérifie si une table existe"""
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la table {table_name}: {e}")
        return False

def show_table_structure(cursor, table_name):
    """Affiche la structure d'une table"""
    try:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"\n📋 Structure de la table {table_name}:")
        print("-" * 60)
        for column in columns:
            print(f"  {column[0]:<30} {column[1]:<20} {column[2]}")
        print("-" * 60)
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage de la structure de {table_name}: {e}")
        return False

def create_clients_table(cursor):
    """Crée la table Clients si elle n'existe pas"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Clients (
        Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
        Month VARCHAR(20),
        Name VARCHAR(100),
        Age INT,
        SSN VARCHAR(20),
        Occupation VARCHAR(100),
        Annual_Income DECIMAL(15,2),
        Monthly_Inhand_Salary DECIMAL(15,2),
        Num_Bank_Accounts INT,
        Num_Credit_Card INT,
        Interest_Rate DECIMAL(5,2),
        Num_of_Loan INT,
        Type_of_Loan VARCHAR(50),
        Delay_from_due_date INT,
        Num_of_Delayed_Payment INT,
        Changed_Credit_Limit DECIMAL(15,2),
        Num_Credit_Inquiries INT,
        Credit_Mix VARCHAR(20),
        Outstanding_Debt DECIMAL(15,2),
        Credit_Utilization_Ratio DECIMAL(5,2),
        Credit_History_Age DECIMAL(5,2),
        Payment_of_Min_Amount VARCHAR(10),
        Total_EMI_per_month DECIMAL(15,2),
        Amount_invested_monthly DECIMAL(15,2),
        Payment_Behaviour VARCHAR(50),
        Monthly_Balance DECIMAL(15,2),
        Credit_Score INT,
        Sexe VARCHAR(1),
        Situation_familiale VARCHAR(50),
        Nb_personnes_a_charge INT,
        Statut_residence VARCHAR(50),
        Anciennete_domicile DECIMAL(5,2),
        Statut_professionnel VARCHAR(50),
        Anciennete_emploi DECIMAL(5,2),
        Type_contrat VARCHAR(50),
        Taille_entreprise VARCHAR(50),
        Autres_revenus_mensuels DECIMAL(15,2),
        Revenu_total_foyer DECIMAL(15,2),
        Stabilite_revenus VARCHAR(50),
        Charges_fixes_mensuelles DECIMAL(15,2),
        Autres_obligations_financieres DECIMAL(15,2),
        Taux_endettement_DTI DECIMAL(5,2),
        Capacite_remboursement DECIMAL(15,2),
        Ratio_revenu_mensualite DECIMAL(5,2),
        Loan_to_value_LTV DECIMAL(5,2),
        Montant_credit_demande DECIMAL(15,2),
        Duree_remboursement_souhaitee INT,
        Objet_credit VARCHAR(100),
        Apport_personnel DECIMAL(15,2),
        Garanties_collateraux TEXT,
        date_demande DATETIME,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Table Clients créée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table Clients: {e}")
        return False

def count_records(cursor, table_name):
    """Compte le nombre d'enregistrements dans une table"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"📊 Nombre d'enregistrements dans {table_name}: {count}")
        return count
    except Exception as e:
        print(f"❌ Erreur lors du comptage des enregistrements de {table_name}: {e}")
        return 0

def main():
    print("🔍 Test de la base de données SecuriBank")
    print("=" * 50)
    
    # Test de connexion
    conn = test_database_connection()
    if not conn:
        sys.exit(1)
    
    cursor = conn.cursor()
    
    # Vérification de la table Clients
    if check_table_exists(cursor, 'Clients'):
        print("✅ Table Clients existe")
        show_table_structure(cursor, 'Clients')
        count_records(cursor, 'Clients')
    else:
        print("⚠️ Table Clients n'existe pas, création en cours...")
        if create_clients_table(cursor):
            conn.commit()
            show_table_structure(cursor, 'Clients')
        else:
            print("❌ Impossible de créer la table Clients")
            sys.exit(1)
    
    # Vérification des autres tables
    other_tables = ['signup', 'demandes_credit']
    for table in other_tables:
        if check_table_exists(cursor, table):
            print(f"✅ Table {table} existe")
            count_records(cursor, table)
        else:
            print(f"⚠️ Table {table} n'existe pas")
    
    cursor.close()
    conn.close()
    print("\n✅ Test terminé avec succès")

if __name__ == "__main__":
    main()
