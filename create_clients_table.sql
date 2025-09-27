-- Script SQL pour créer la table Clients
-- Exécutez ce script dans votre base de données MySQL 'stagee'

USE stagee;

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
    
    -- Champs additionnels du formulaire
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

-- Vérifier que la table a été créée
DESCRIBE Clients;

-- Afficher le nombre d'enregistrements
SELECT COUNT(*) as nombre_clients FROM Clients;
