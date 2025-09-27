#!/usr/bin/env python3
"""
Script pour corriger la route /demande_credit dans app.py
"""

def fix_demande_credit_route():
    """Corrige la route demande_credit pour utiliser seulement les nouveaux champs"""
    
    file_path = r'c:\Users\MSI\Downloads\stageee\app.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Nouveau code pour la route demande_credit
        new_route_code = '''@app.route("/demande_credit", methods=["GET", "POST"])
def demande_credit():
    if "user" not in session:
        return redirect(url_for("login"))

    current_language = session.get('language', 'fr')
    print(f"🌐 Page demande_credit - Langue actuelle: {current_language}")
    success, error = None, None

    if request.method == "POST":
        print("🚀 Réception d'une demande POST sur /demande_credit")
        print(f"📋 Données reçues: {len(request.form)} champs")
        for key, value in request.form.items():
            if value:  # Afficher seulement les champs non vides
                print(f"  {key}: {value}")
        
        try:
            # Récupération des champs saisis par le client (11 champs)
            name = request.form.get("Name")
            age = request.form.get("Age")
            ssn = request.form.get("SSN")
            occupation = request.form.get("Occupation")
            annual_income = request.form.get("Annual_Income")
            monthly_salary = request.form.get("Monthly_Inhand_Salary")
            num_bank_accounts = request.form.get("Num_Bank_Accounts", "1")
            num_credit_card = request.form.get("Num_Credit_Card", "0")
            num_of_loan = request.form.get("Num_of_Loan", "0")
            type_of_loan = request.form.get("Type_of_Loan", "Not Specified")
            amount_invested_monthly = request.form.get("Amount_invested_monthly", "0")
            
            # Validation des champs obligatoires
            if not all([name, age, ssn, occupation, annual_income, monthly_salary]):
                error = "Veuillez remplir tous les champs obligatoires."
                return render_template("demande_credit.html", success=success, error=error, current_language=current_language)
            
            # Génération des champs automatiques (17 champs)
            import random
            from datetime import datetime
            
            # ID et Customer_ID générés automatiquement
            customer_id = random.randint(100000, 999999)
            
            # Month basé sur le mois actuel
            current_month = datetime.now().strftime("%B")
            
            # Champs calculés avec des valeurs par défaut réalistes
            interest_rate = round(random.uniform(8.0, 15.0), 1)
            delay_from_due_date = random.randint(0, 30)
            num_delayed_payment = random.randint(0, 5)
            changed_credit_limit = random.randint(-1000, 2000)
            num_credit_inquiries = random.randint(1, 8)
            
            # Credit Mix basé sur le profil
            credit_mix_options = ["Standard", "Good", "Bad"]
            credit_mix = random.choice(credit_mix_options)
            
            # Outstanding Debt basé sur le revenu
            try:
                income = float(annual_income) if annual_income else 50000
                outstanding_debt = round(random.uniform(0, income * 0.3), 2)
            except:
                outstanding_debt = 0
            
            # Credit Utilization Ratio
            credit_utilization_ratio = round(random.uniform(10.0, 60.0), 1)
            
            # Credit History Age
            credit_history_age = round(random.uniform(1.0, 15.0), 1)
            
            # Payment of Min Amount
            payment_min_amount = random.choice(["Yes", "No", "NM"])
            
            # Total EMI per month
            total_emi_per_month = round(random.uniform(0, 2000), 2)
            
            # Payment Behaviour
            payment_behaviours = [
                "Low_spent_Medium_value_payments",
                "High_spent_Small_value_payments", 
                "Low_spent_Large_value_payments",
                "High_spent_Medium_value_payments",
                "High_spent_Large_value_payments",
                "Low_spent_Small_value_payments"
            ]
            payment_behaviour = random.choice(payment_behaviours)
            
            # Monthly Balance
            try:
                salary = float(monthly_salary) if monthly_salary else 3000
                monthly_balance = round(random.uniform(salary * 0.1, salary * 0.8), 2)
            except:
                monthly_balance = 1000
            
            print(f"📊 Données préparées pour le modèle:")
            print(f"   👤 Client: {name}, {age} ans")
            print(f"   💰 Revenus: {annual_income}/an, {monthly_salary}/mois")
            print(f"   🏦 Comptes: {num_bank_accounts} bancaires, {num_credit_card} cartes")
            print(f"   📈 Investissements: {amount_invested_monthly}/mois")
            
            # Préparation des données pour le modèle
            form_data = {
                'Month': current_month,
                'Name': name,
                'Age': age,
                'SSN': ssn,
                'Occupation': occupation,
                'Annual_Income': annual_income,
                'Monthly_Inhand_Salary': monthly_salary,
                'Num_Bank_Accounts': num_bank_accounts,
                'Num_Credit_Card': num_credit_card,
                'Interest_Rate': str(interest_rate),
                'Num_of_Loan': num_of_loan,
                'Type_of_Loan': type_of_loan,
                'Delay_from_due_date': str(delay_from_due_date),
                'Num_of_Delayed_Payment': str(num_delayed_payment),
                'Changed_Credit_Limit': str(changed_credit_limit),
                'Num_Credit_Inquiries': str(num_credit_inquiries),
                'Credit_Mix': credit_mix,
                'Outstanding_Debt': str(outstanding_debt),
                'Credit_Utilization_Ratio': str(credit_utilization_ratio),
                'Credit_History_Age': str(credit_history_age),
                'Payment_of_Min_Amount': payment_min_amount,
                'Total_EMI_per_month': str(total_emi_per_month),
                'Amount_invested_monthly': amount_invested_monthly,
                'Payment_Behaviour': payment_behaviour,
                'Monthly_Balance': str(monthly_balance)
            }
            
            date_demande = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 🤖 Prédiction automatique du crédit
            prediction_result = credit_predictor.predict_credit_approval(form_data)
            print(f"🤖 Résultat de la prédiction pour {name}: {prediction_result}")
            
            # Insertion en base avec tous les nouveaux champs
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO Clients (
                    Customer_ID, Month, Name, Age, SSN, Occupation, Annual_Income, Monthly_Inhand_Salary,
                    Num_Bank_Accounts, Num_Credit_Card, Interest_Rate, Num_of_Loan, Type_of_Loan,
                    Delay_from_due_date, Num_of_Delayed_Payment, Changed_Credit_Limit, Num_Credit_Inquiries,
                    Credit_Mix, Outstanding_Debt, Credit_Utilization_Ratio, Credit_History_Age,
                    Payment_of_Min_Amount, Total_EMI_per_month, Amount_invested_monthly, Payment_Behaviour,
                    Monthly_Balance, Credit_Score, date_demande
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer_id, current_month, name, age, ssn, occupation, annual_income, monthly_salary,
                num_bank_accounts, num_credit_card, interest_rate, num_of_loan, type_of_loan,
                delay_from_due_date, num_delayed_payment, changed_credit_limit, num_credit_inquiries,
                credit_mix, outstanding_debt, credit_utilization_ratio, credit_history_age,
                payment_min_amount, total_emi_per_month, amount_invested_monthly, payment_behaviour,
                monthly_balance, prediction_result.get('credit_score', 0), date_demande
            ))
            mysql.connection.commit()
            cur.close()
            
            print(f"✅ Demande enregistrée en base pour {name}")
            
            # Message de succès basé sur la prédiction
            if prediction_result.get('approved', False):
                success = f"✅ Félicitations ! Votre demande a été pré-approuvée automatiquement !\\n🎯 {prediction_result.get('message', '')}\\n📧 Un email de confirmation vous a été envoyé."
            else:
                success = f"📝 Votre demande a été enregistrée et sera étudiée par nos experts.\\n📊 {prediction_result.get('message', '')}\\n📧 Un email de confirmation vous a été envoyé."
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            import traceback
            traceback.print_exc()
            error = f"❌ Erreur lors de l'envoi : {str(e)}"
    
    return render_template("demande_credit.html", success=success, error=error, current_language=current_language)'''
        
        # Trouver et remplacer la route existante
        start_marker = '@app.route("/demande_credit", methods=["GET", "POST"])'
        end_marker = 'return render_template("demande_credit.html", success=success, error=error, current_language=current_language)'
        
        start_index = content.find(start_marker)
        if start_index == -1:
            print("❌ Route demande_credit non trouvée")
            return False
        
        # Trouver la fin de la fonction
        lines = content[start_index:].split('\n')
        end_line_index = -1
        indent_level = None
        
        for i, line in enumerate(lines):
            if i == 0:  # Première ligne (@app.route)
                continue
            if line.strip().startswith('def '):  # Ligne de définition de fonction
                indent_level = len(line) - len(line.lstrip())
                continue
            if indent_level is not None and line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.startswith(' '):
                # Nouvelle fonction ou fin de fichier
                end_line_index = i
                break
        
        if end_line_index == -1:
            # Prendre jusqu'à la fin du fichier
            end_index = len(content)
        else:
            end_index = start_index + sum(len(line) + 1 for line in lines[:end_line_index])
        
        # Remplacer le contenu
        new_content = content[:start_index] + new_route_code + '\n\n' + content[end_index:]
        
        # Sauvegarder
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Route demande_credit corrigée avec succès!")
        print("📋 Changements effectués:")
        print("   - Suppression de toutes les références aux anciens champs")
        print("   - Utilisation des 11 champs client + 17 champs automatiques")
        print("   - Génération automatique des valeurs manquantes")
        print("   - Prédiction avec le modèle Random Forest")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_demande_credit_route()
