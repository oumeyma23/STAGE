import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CreditPredictor:
    def __init__(self, model_path='random_forest_model.pkl'):
        """Initialise le prédicteur de crédit avec le modèle Random Forest"""
        self.model = None
        self.use_fallback = False
        
        try:
            self.model = joblib.load(model_path)
            print(f"✅ Modèle Random Forest chargé depuis {model_path}")
            
            # Test rapide pour vérifier la compatibilité
            import pandas as pd
            test_data = pd.DataFrame([[1, 30, 1, 50000, 4000, 2, 1, 10, 0, 1, 0, 0, 0, 1, 1, 0, 25, 5, 1, 0, 500, 1, 2000]], 
                                   columns=['Month', 'Age', 'Occupation', 'Annual_Income', 'Monthly_Inhand_Salary',
                                           'Num_Bank_Accounts', 'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 
                                           'Type_of_Loan', 'Delay_from_due_date', 'Num_of_Delayed_Payment', 
                                           'Changed_Credit_Limit', 'Num_Credit_Inquiries', 'Credit_Mix', 
                                           'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Credit_History_Age',
                                           'Payment_of_Min_Amount', 'Total_EMI_per_month', 'Amount_invested_monthly', 
                                           'Payment_Behaviour', 'Monthly_Balance'])
            
            # Test de prédiction
            _ = self.model.predict(test_data)
            print(f"✅ Test de compatibilité réussi")
            
            # Colonnes attendues par le modèle
            self.expected_features = [
                'Month', 'Age', 'Occupation', 'Annual_Income', 'Monthly_Inhand_Salary',
                'Num_Bank_Accounts', 'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 
                'Type_of_Loan', 'Delay_from_due_date', 'Num_of_Delayed_Payment', 
                'Changed_Credit_Limit', 'Num_Credit_Inquiries', 'Credit_Mix', 
                'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Credit_History_Age',
                'Payment_of_Min_Amount', 'Total_EMI_per_month', 'Amount_invested_monthly', 
                'Payment_Behaviour', 'Monthly_Balance'
            ]
            print(f"📋 Features attendues: {len(self.expected_features)} colonnes")
            
        except Exception as e:
            print(f"⚠️ Problème de compatibilité avec le modèle: {e}")
            print(f"🔄 Activation du mode de prédiction alternatif")
            self.model = None
            self.use_fallback = True
    
    def calculate_age(self, birth_date):
        """Calcule l'âge à partir de la date de naissance"""
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return 30  # Valeur par défaut
    
    def calculate_dti(self, monthly_expenses, net_salary):
        """Calcule le ratio dette/revenu (DTI)"""
        try:
            if net_salary > 0:
                return monthly_expenses / net_salary
            return 0
        except:
            return 0
    
    def calculate_risk_score(self, age, dti, credit_amount, net_salary, existing_loans):
        """Calcule un score de risque basé sur plusieurs facteurs"""
        try:
            risk_score = 0
            
            # Facteur âge (risque plus élevé pour les très jeunes et très âgés)
            if age < 25 or age > 65:
                risk_score += 0.1
            elif 25 <= age <= 45:
                risk_score += 0.05
            
            # Facteur DTI
            if dti > 0.4:
                risk_score += 0.3
            elif dti > 0.3:
                risk_score += 0.2
            elif dti > 0.2:
                risk_score += 0.1
            
            # Facteur montant du crédit par rapport au salaire
            if net_salary > 0:
                credit_salary_ratio = credit_amount / (net_salary * 12)
                if credit_salary_ratio > 5:
                    risk_score += 0.2
                elif credit_salary_ratio > 3:
                    risk_score += 0.1
            
            # Facteur crédits existants
            if existing_loans > 0:
                risk_score += 0.15
            
            return min(risk_score, 1.0)  # Limiter à 1.0
        except:
            return 0.5  # Valeur par défaut modérée
    
    def encode_credit_type(self, credit_type):
        """Encode le type de crédit"""
        credit_mapping = {
            'Crédit consommation': 1,
            'Crédit personnel': 1,
            'Crédit auto': 2,
            'Crédit immobilier': 3,
            'Regroupement de crédits': 4
        }
        return credit_mapping.get(credit_type, 1)
    
    def encode_contract_type(self, contract_type):
        """Encode le type de contrat"""
        contract_mapping = {
            'CDI': 1.0,
            'CDD': 0.8,
            'Indépendant / Freelance': 0.6,
            'Retraité': 0.7,
            'Autre': 0.5
        }
        return contract_mapping.get(contract_type, 0.5)
    
    def determine_score_group(self, risk_score):
        """Détermine le groupe de score basé sur le risk_score"""
        if risk_score <= 0.2:
            return {'score_group_Bon': True, 'score_group_Moyen': False, 
                   'score_group_Risque élevé': False, 'score_group_Très risqué': False}
        elif risk_score <= 0.4:
            return {'score_group_Bon': False, 'score_group_Moyen': True, 
                   'score_group_Risque élevé': False, 'score_group_Très risqué': False}
        elif risk_score <= 0.7:
            return {'score_group_Bon': False, 'score_group_Moyen': False, 
                   'score_group_Risque élevé': True, 'score_group_Très risqué': False}
        else:
            return {'score_group_Bon': False, 'score_group_Moyen': False, 
                   'score_group_Risque élevé': False, 'score_group_Très risqué': True}
    
    def encode_categorical_features(self, form_data):
        """Encode les variables catégorielles pour le modèle"""
        
        # Encodage du mois
        month_mapping = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        month = month_mapping.get(form_data.get('Month', 'January'), 1)
        
        # Encodage de l'occupation
        occupation_mapping = {
            'Engineer': 1, 'Teacher': 2, 'Doctor': 3, 'Lawyer': 4, 'Manager': 5,
            'Accountant': 6, 'Developer': 7, 'Scientist': 8, 'Architect': 9,
            'Consultant': 10, 'Other': 11
        }
        occupation = form_data.get('Occupation', 'Other')
        occupation_encoded = occupation_mapping.get(occupation, 11)
        
        # Encodage du type de prêt
        loan_type_mapping = {
            'Auto Loan': 1, 'Credit-Builder Loan': 2, 'Personal Loan': 3,
            'Home Equity Loan': 4, 'Mortgage Loan': 5, 'Student Loan': 6,
            'Debt Consolidation Loan': 7, 'Payday Loan': 8, 'Not Specified': 9
        }
        loan_type = form_data.get('Type_of_Loan', 'Not Specified')
        loan_type_encoded = loan_type_mapping.get(loan_type, 9)
        
        # Encodage du Credit Mix
        credit_mix_mapping = {'Standard': 1, 'Good': 2, 'Bad': 3}
        credit_mix = form_data.get('Credit_Mix', 'Standard')
        credit_mix_encoded = credit_mix_mapping.get(credit_mix, 1)
        
        # Encodage du Payment of Min Amount
        payment_min_mapping = {'Yes': 1, 'No': 0, 'NM': 2}
        payment_min = form_data.get('Payment_of_Min_Amount', 'NM')
        payment_min_encoded = payment_min_mapping.get(payment_min, 2)
        
        # Encodage du Payment Behaviour
        payment_behaviour_mapping = {
            'High_spent_Small_value_payments': 1,
            'Low_spent_Large_value_payments': 2,
            'High_spent_Medium_value_payments': 3,
            'Low_spent_Medium_value_payments': 4,
            'High_spent_Large_value_payments': 5,
            'Low_spent_Small_value_payments': 6
        }
        payment_behaviour = form_data.get('Payment_Behaviour', 'Low_spent_Medium_value_payments')
        payment_behaviour_encoded = payment_behaviour_mapping.get(payment_behaviour, 4)
        
        return {
            'Month': month,
            'Occupation': occupation_encoded,
            'Type_of_Loan': loan_type_encoded,
            'Credit_Mix': credit_mix_encoded,
            'Payment_of_Min_Amount': payment_min_encoded,
            'Payment_Behaviour': payment_behaviour_encoded
        }

    def prepare_features(self, form_data):
        """Prépare les features pour la prédiction à partir des données du formulaire"""
        try:
            # Encodage des variables catégorielles
            encoded_features = self.encode_categorical_features(form_data)
            
            # Extraction et conversion des données numériques
            def safe_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default
            
            def safe_int(value, default=0):
                try:
                    return int(value) if value else default
                except (ValueError, TypeError):
                    return default
            
            # Création du DataFrame avec toutes les features attendues par le modèle
            features_dict = {
                'Month': encoded_features['Month'],
                'Age': safe_int(form_data.get('Age'), 30),
                'Occupation': encoded_features['Occupation'],
                'Annual_Income': safe_float(form_data.get('Annual_Income'), 50000),
                'Monthly_Inhand_Salary': safe_float(form_data.get('Monthly_Inhand_Salary'), 4000),
                'Num_Bank_Accounts': safe_int(form_data.get('Num_Bank_Accounts'), 1),
                'Num_Credit_Card': safe_int(form_data.get('Num_Credit_Card'), 0),
                'Interest_Rate': safe_float(form_data.get('Interest_Rate'), 10.0),
                'Num_of_Loan': safe_int(form_data.get('Num_of_Loan'), 0),
                'Type_of_Loan': encoded_features['Type_of_Loan'],
                'Delay_from_due_date': safe_int(form_data.get('Delay_from_due_date'), 0),
                'Num_of_Delayed_Payment': safe_int(form_data.get('Num_of_Delayed_Payment'), 0),
                'Changed_Credit_Limit': safe_float(form_data.get('Changed_Credit_Limit'), 0),
                'Num_Credit_Inquiries': safe_int(form_data.get('Num_Credit_Inquiries'), 0),
                'Credit_Mix': encoded_features['Credit_Mix'],
                'Outstanding_Debt': safe_float(form_data.get('Outstanding_Debt'), 0),
                'Credit_Utilization_Ratio': safe_float(form_data.get('Credit_Utilization_Ratio'), 25.0),
                'Credit_History_Age': safe_float(form_data.get('Credit_History_Age'), 5.0),
                'Payment_of_Min_Amount': encoded_features['Payment_of_Min_Amount'],
                'Total_EMI_per_month': safe_float(form_data.get('Total_EMI_per_month'), 0),
                'Amount_invested_monthly': safe_float(form_data.get('Amount_invested_monthly'), 0),
                'Payment_Behaviour': encoded_features['Payment_Behaviour'],
                'Monthly_Balance': safe_float(form_data.get('Monthly_Balance'), 1000)
            }
            
            # Créer le DataFrame
            features = pd.DataFrame([features_dict])
            
            print(f"✅ Features préparées: {features.shape}")
            print(f"📊 Colonnes: {list(features.columns)}")
            
            return features
            
        except Exception as e:
            print(f"❌ Erreur lors de la préparation des features: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def calculate_credit_score_fallback(self, form_data):
        """Calcule un score de crédit basé sur des règles métier (mode de secours)"""
        try:
            # Extraction des données importantes
            age = int(form_data.get('Age', 30))
            annual_income = float(form_data.get('Annual_Income', 50000))
            monthly_salary = float(form_data.get('Monthly_Inhand_Salary', 4000))
            credit_utilization = float(form_data.get('Credit_Utilization_Ratio', 30))
            credit_history_age = float(form_data.get('Credit_History_Age', 5))
            num_delayed_payments = int(form_data.get('Num_of_Delayed_Payment', 0))
            outstanding_debt = float(form_data.get('Outstanding_Debt', 0))
            num_credit_inquiries = int(form_data.get('Num_Credit_Inquiries', 2))
            payment_min_amount = form_data.get('Payment_of_Min_Amount', 'Yes')
            credit_mix = form_data.get('Credit_Mix', 'Standard')
            
            # Score de base
            base_score = 500
            
            # Facteur revenu (0-100 points)
            if annual_income >= 100000:
                income_score = 100
            elif annual_income >= 75000:
                income_score = 80
            elif annual_income >= 50000:
                income_score = 60
            elif annual_income >= 30000:
                income_score = 40
            else:
                income_score = 20
            
            # Facteur âge (0-50 points)
            if 25 <= age <= 55:
                age_score = 50
            elif 18 <= age <= 65:
                age_score = 35
            else:
                age_score = 20
            
            # Facteur utilisation crédit (0-100 points)
            if credit_utilization <= 10:
                utilization_score = 100
            elif credit_utilization <= 30:
                utilization_score = 80
            elif credit_utilization <= 50:
                utilization_score = 60
            elif credit_utilization <= 70:
                utilization_score = 40
            else:
                utilization_score = 10
            
            # Facteur historique crédit (0-80 points)
            if credit_history_age >= 10:
                history_score = 80
            elif credit_history_age >= 5:
                history_score = 60
            elif credit_history_age >= 2:
                history_score = 40
            else:
                history_score = 20
            
            # Pénalités
            penalty = 0
            penalty += num_delayed_payments * 15  # -15 points par paiement en retard
            penalty += num_credit_inquiries * 5   # -5 points par enquête crédit
            penalty += min(outstanding_debt / 1000, 50)  # Pénalité basée sur la dette
            
            if payment_min_amount == 'No':
                penalty += 30
            
            # Bonus pour bon credit mix
            bonus = 0
            if credit_mix == 'Good':
                bonus += 20
            elif credit_mix == 'Bad':
                penalty += 20
            
            # Calcul final
            final_score = base_score + income_score + age_score + utilization_score + history_score + bonus - penalty
            
            # Limiter entre 300 et 850
            final_score = max(300, min(850, int(final_score)))
            
            print(f"🧮 Score calculé (mode alternatif): {final_score}")
            print(f"   Base: {base_score}, Revenu: +{income_score}, Âge: +{age_score}")
            print(f"   Utilisation: +{utilization_score}, Historique: +{history_score}")
            print(f"   Bonus: +{bonus}, Pénalités: -{penalty}")
            
            return final_score
            
        except Exception as e:
            print(f"❌ Erreur calcul score alternatif: {e}")
            return 650  # Score moyen par défaut
    
    def interpret_credit_score(self, credit_score):
        """Interprète le score de crédit prédit"""
        if credit_score >= 750:
            return {
                'category': 'Excellent',
                'risk_level': 'Très faible',
                'approved': True,
                'probability': 0.95
            }
        elif credit_score >= 700:
            return {
                'category': 'Bon',
                'risk_level': 'Faible',
                'approved': True,
                'probability': 0.85
            }
        elif credit_score >= 650:
            return {
                'category': 'Moyen',
                'risk_level': 'Modéré',
                'approved': True,
                'probability': 0.70
            }
        elif credit_score >= 600:
            return {
                'category': 'Passable',
                'risk_level': 'Élevé',
                'approved': False,
                'probability': 0.40
            }
        else:
            return {
                'category': 'Faible',
                'risk_level': 'Très élevé',
                'approved': False,
                'probability': 0.15
            }

    def predict_credit_approval(self, form_data):
        """Prédit le score de crédit et l'approbation basée sur les données du formulaire"""
        
        # Utiliser le mode de secours si le modèle n'est pas disponible ou en cas d'erreur de compatibilité
        if self.model is None or self.use_fallback:
            print("🔄 Utilisation du mode de prédiction alternatif")
            predicted_credit_score = self.calculate_credit_score_fallback(form_data)
            
            # Interprétation du score
            score_interpretation = self.interpret_credit_score(predicted_credit_score)
            
            # Message personnalisé
            if score_interpretation['approved']:
                message = f"✅ Crédit approuvé ! Score de crédit calculé: {predicted_credit_score:.0f} ({score_interpretation['category']}) - Mode alternatif"
            else:
                message = f"❌ Crédit refusé. Score de crédit calculé: {predicted_credit_score:.0f} ({score_interpretation['category']}) - Mode alternatif"
            
            # Détails pour l'analyse
            details = {
                'predicted_credit_score': predicted_credit_score,
                'score_category': score_interpretation['category'],
                'calculation_method': 'Règles métier (mode alternatif)',
                'age': form_data.get('Age', 'N/A'),
                'annual_income': form_data.get('Annual_Income', 'N/A'),
                'credit_utilization': form_data.get('Credit_Utilization_Ratio', 'N/A'),
                'credit_history_age': form_data.get('Credit_History_Age', 'N/A')
            }
            
            return {
                'approved': score_interpretation['approved'],
                'credit_score': predicted_credit_score,
                'probability': score_interpretation['probability'],
                'risk_level': score_interpretation['risk_level'],
                'message': message,
                'details': details
            }
        
        try:
            # Préparer les features pour le modèle ML
            features = self.prepare_features(form_data)
            if features is None:
                # Fallback en cas d'erreur de préparation
                print("⚠️ Erreur préparation features, utilisation du mode alternatif")
                predicted_credit_score = self.calculate_credit_score_fallback(form_data)
                score_interpretation = self.interpret_credit_score(predicted_credit_score)
                return {
                    'approved': score_interpretation['approved'],
                    'credit_score': predicted_credit_score,
                    'probability': score_interpretation['probability'],
                    'risk_level': score_interpretation['risk_level'],
                    'message': f"Score calculé (mode alternatif): {predicted_credit_score:.0f}",
                    'details': {'calculation_method': 'Règles métier'}
                }
            
            # Prédiction du Credit Score avec le modèle ML
            predicted_credit_score = self.model.predict(features)[0]
            
            # Interprétation du score
            score_interpretation = self.interpret_credit_score(predicted_credit_score)
            
            # Message personnalisé
            if score_interpretation['approved']:
                message = f"✅ Crédit approuvé ! Score de crédit prédit: {predicted_credit_score:.0f} ({score_interpretation['category']})"
            else:
                message = f"❌ Crédit refusé. Score de crédit prédit: {predicted_credit_score:.0f} ({score_interpretation['category']})"
            
            # Détails pour l'analyse
            details = {
                'predicted_credit_score': predicted_credit_score,
                'score_category': score_interpretation['category'],
                'age': features['Age'].iloc[0],
                'annual_income': features['Annual_Income'].iloc[0],
                'monthly_salary': features['Monthly_Inhand_Salary'].iloc[0],
                'num_bank_accounts': features['Num_Bank_Accounts'].iloc[0],
                'num_credit_cards': features['Num_Credit_Card'].iloc[0],
                'credit_utilization': features['Credit_Utilization_Ratio'].iloc[0],
                'credit_history_age': features['Credit_History_Age'].iloc[0],
                'num_loans': features['Num_of_Loan'].iloc[0],
                'delayed_payments': features['Num_of_Delayed_Payment'].iloc[0]
            }
            
            return {
                'approved': score_interpretation['approved'],
                'credit_score': predicted_credit_score,
                'probability': score_interpretation['probability'],
                'risk_level': score_interpretation['risk_level'],
                'message': message,
                'details': details
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction: {e}")
            import traceback
            traceback.print_exc()
            return {
                'approved': False,
                'credit_score': 0,
                'probability': 0.0,
                'risk_level': 'Erreur',
                'message': f'Erreur lors de l\'analyse: {str(e)}',
                'details': {}
            }

# Instance globale du prédicteur
credit_predictor = CreditPredictor()
