import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CreditPredictor:
    def __init__(self, model_path='credit_model.pkl'):
        """Initialise le prédicteur de crédit avec le modèle entraîné"""
        try:
            self.model = joblib.load(model_path)
            print(f"✅ Modèle chargé depuis {model_path}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            self.model = None
    
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
    
    def prepare_features(self, form_data):
        """Prépare les features pour la prédiction à partir des données du formulaire"""
        try:
            # Extraction des données du formulaire
            age = self.calculate_age(form_data.get('date_naissance'))
            net_salary = float(form_data.get('revenu', 0))
            other_income = float(form_data.get('autres_revenus', 0))
            household_income = float(form_data.get('revenu_menage', net_salary))
            fixed_expenses = float(form_data.get('depenses', 0))
            existing_loans_amount = float(form_data.get('credits_en_cours', 0))
            credit_amount = float(form_data.get('montant', 0))
            credit_duration = int(form_data.get('duree', 12))
            children = int(form_data.get('enfants', 0))
            seniority_months = int(form_data.get('anciennete', 0)) * 12
            savings = 0  # Pas dans le formulaire, valeur par défaut
            assets_value = 0  # Pas dans le formulaire, valeur par défaut
            
            # Calculs
            dti = self.calculate_dti(fixed_expenses + existing_loans_amount, net_salary)
            risk_score = self.calculate_risk_score(age, dti, credit_amount, net_salary, existing_loans_amount)
            
            # Encodages
            credit_type_encoded = self.encode_credit_type(form_data.get('type_credit'))
            contract_type_encoded = self.encode_contract_type(form_data.get('type_contrat'))
            
            # Groupes de score
            score_groups = self.determine_score_group(risk_score)
            
            # DTI risk (binaire)
            dti_risk = 1 if dti > 0.3 else 0
            
            # Création du DataFrame avec toutes les features attendues par le modèle
            features = pd.DataFrame({
                'age': [age],
                'id_number': [10000000],  # Valeur fictive
                'phone': [20000000],  # Valeur fictive
                'children': [children],
                'seniority_months': [seniority_months],
                'net_salary': [net_salary],
                'other_income': [other_income],
                'household_income': [household_income],
                'fixed_expenses': [fixed_expenses],
                'existing_loans': [existing_loans_amount > 0],
                'existing_loan_amount_remaining': [existing_loans_amount * 10],  # Estimation
                'existing_loan_monthly': [existing_loans_amount],
                'account_number': [1234567890123456],  # Valeur fictive
                'savings': [savings],
                'assets_value': [assets_value],
                'credit_amount': [credit_amount],
                'credit_duration_months': [credit_duration],
                'dti': [dti],
                'risk_score': [risk_score],
                'dti_risk': [dti_risk],
                'score_group_Bon': [score_groups['score_group_Bon']],
                'score_group_Moyen': [score_groups['score_group_Moyen']],
                'score_group_Risque élevé': [score_groups['score_group_Risque élevé']],
                'score_group_Très risqué': [score_groups['score_group_Très risqué']],
                'credit_type_encoded': [credit_type_encoded],
                'contract_type_encoded': [contract_type_encoded]
            })
            
            return features
            
        except Exception as e:
            print(f"❌ Erreur lors de la préparation des features: {e}")
            return None
    
    def predict_credit_approval(self, form_data):
        """Prédit l'approbation du crédit basée sur les données du formulaire"""
        if self.model is None:
            return {
                'approved': False,
                'probability': 0.0,
                'risk_level': 'Erreur',
                'message': 'Modèle non disponible',
                'details': {}
            }
        
        try:
            # Préparer les features
            features = self.prepare_features(form_data)
            if features is None:
                return {
                    'approved': False,
                    'probability': 0.0,
                    'risk_level': 'Erreur',
                    'message': 'Erreur dans la préparation des données',
                    'details': {}
                }
            
            # Prédiction
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0]
            
            # Probabilité d'approbation (classe 0 = pas de défaut = approuvé)
            approval_probability = probability[0]
            
            # Déterminer le niveau de risque
            risk_score = features['risk_score'].iloc[0]
            if risk_score <= 0.2:
                risk_level = 'Faible'
            elif risk_score <= 0.4:
                risk_level = 'Modéré'
            elif risk_score <= 0.7:
                risk_level = 'Élevé'
            else:
                risk_level = 'Très élevé'
            
            # Décision d'approbation
            approved = prediction == 0 and approval_probability > 0.6
            
            # Message personnalisé
            if approved:
                message = f"✅ Crédit approuvé ! Probabilité d'approbation: {approval_probability:.1%}"
            else:
                message = f"❌ Crédit refusé. Probabilité d'approbation: {approval_probability:.1%}"
            
            # Détails pour l'analyse
            details = {
                'dti': features['dti'].iloc[0],
                'risk_score': risk_score,
                'age': features['age'].iloc[0],
                'net_salary': features['net_salary'].iloc[0],
                'credit_amount': features['credit_amount'].iloc[0],
                'credit_duration': features['credit_duration_months'].iloc[0]
            }
            
            return {
                'approved': approved,
                'probability': approval_probability,
                'risk_level': risk_level,
                'message': message,
                'details': details
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction: {e}")
            return {
                'approved': False,
                'probability': 0.0,
                'risk_level': 'Erreur',
                'message': f'Erreur lors de l\'analyse: {str(e)}',
                'details': {}
            }

# Instance globale du prédicteur
credit_predictor = CreditPredictor()
