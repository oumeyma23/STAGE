#!/usr/bin/env python3
"""
Script pour vérifier et créer la structure de la base de données
"""

import MySQLdb

def check_and_create_table():
    """Vérifie et crée la table Clients si nécessaire"""
    
    try:
        # Connexion à la base de données
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='',
            db='stagee'
        )
        cursor = conn.cursor()
        
        print("✅ Connexion à la base de données réussie")
        
        # Vérifier si la table Clients existe
        cursor.execute("SHOW TABLES LIKE 'Clients'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Table Clients existe")
            
            # Vérifier la structure de la table
            cursor.execute("DESCRIBE Clients")
            columns = cursor.fetchall()
            
            print("📋 Structure actuelle de la table Clients:")
            for column in columns:
                print(f"   - {column[0]} ({column[1]})")
            
            # Vérifier si toutes les colonnes nécessaires existent
            required_columns = [
                'Customer_ID', 'Month', 'Name', 'Age', 'SSN', 'Occupation',
                'Annual_Income', 'Monthly_Inhand_Salary', 'Num_Bank_Accounts',
                'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 'Type_of_Loan',
                'Delay_from_due_date', 'Num_of_Delayed_Payment', 'Changed_Credit_Limit',
                'Num_Credit_Inquiries', 'Credit_Mix', 'Outstanding_Debt',
                'Credit_Utilization_Ratio', 'Credit_History_Age', 'Payment_of_Min_Amount',
                'Total_EMI_per_month', 'Amount_invested_monthly', 'Payment_Behaviour',
                'Monthly_Balance', 'Credit_Score'
            ]
            
            existing_columns = [col[0] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"⚠️ Colonnes manquantes: {missing_columns}")
                print("🔧 Ajout des colonnes manquantes...")
                
                for col in missing_columns:
                    try:
                        if col in ['Customer_ID', 'Age', 'Num_Bank_Accounts', 'Num_Credit_Card', 
                                  'Num_of_Loan', 'Delay_from_due_date', 'Num_of_Delayed_Payment', 
                                  'Num_Credit_Inquiries', 'Credit_Score']:
                            cursor.execute(f"ALTER TABLE Clients ADD COLUMN {col} INT")
                        elif col in ['Annual_Income', 'Monthly_Inhand_Salary', 'Interest_Rate',
                                    'Changed_Credit_Limit', 'Outstanding_Debt', 'Credit_Utilization_Ratio',
                                    'Credit_History_Age', 'Total_EMI_per_month', 'Amount_invested_monthly',
                                    'Monthly_Balance']:
                            cursor.execute(f"ALTER TABLE Clients ADD COLUMN {col} DECIMAL(15,2)")
                        else:
                            cursor.execute(f"ALTER TABLE Clients ADD COLUMN {col} VARCHAR(100)")
                        print(f"   ✅ Colonne {col} ajoutée")
                    except Exception as e:
                        print(f"   ❌ Erreur ajout {col}: {e}")
                
                conn.commit()
            else:
                print("✅ Toutes les colonnes nécessaires sont présentes")
        
        else:
            print("⚠️ Table Clients n'existe pas, création en cours...")
            
            # Créer la table avec toutes les colonnes nécessaires
            create_table_sql = """
            CREATE TABLE Clients (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            print("✅ Table Clients créée avec succès")
        
        # Vérifier le nombre d'enregistrements
        cursor.execute("SELECT COUNT(*) FROM Clients")
        count = cursor.fetchone()[0]
        print(f"📊 Nombre d'enregistrements dans Clients: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    check_and_create_table()
