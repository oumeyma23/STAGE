#!/usr/bin/env python3
"""
Script pour remplacer le contenu du formulaire de demande de crédit
avec seulement les champs nécessaires pour le modèle Random Forest
"""

# Nouveau contenu du formulaire (étapes 1 et 2 seulement)
new_form_content = '''        <!-- Step 1: Informations d'identité et personnelles -->
        <div class="step-card" id="step1">
          <div class="step-header">
            <h4><i class="bi-person-circle"></i> 
              {% if current_language == 'ar' %}
                معلومات الهوية والشخصية
              {% elif current_language == 'en' %}
                Identity and Personal Information
              {% else %}
                Informations d'identité et personnelles
              {% endif %}
            </h4>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-calendar3"></i>
                {% if current_language == 'ar' %}
                  الشهر <span class="required">*</span>
                {% elif current_language == 'en' %}
                  Month <span class="required">*</span>
                {% else %}
                  Mois <span class="required">*</span>
                {% endif %}
              </label>
              <select class="form-control" name="Month" required>
                <option value="">Choisir le mois...</option>
                <option value="January">Janvier</option>
                <option value="February">Février</option>
                <option value="March">Mars</option>
                <option value="April">Avril</option>
                <option value="May">Mai</option>
                <option value="June">Juin</option>
                <option value="July">Juillet</option>
                <option value="August">Août</option>
                <option value="September">Septembre</option>
                <option value="October">Octobre</option>
                <option value="November">Novembre</option>
                <option value="December">Décembre</option>
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-person"></i>
                {% if current_language == 'ar' %}
                  الاسم الكامل <span class="required">*</span>
                {% elif current_language == 'en' %}
                  Full Name <span class="required">*</span>
                {% else %}
                  Nom complet <span class="required">*</span>
                {% endif %}
              </label>
              <input type="text" class="form-control" name="Name" required placeholder="Prénom Nom">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-calendar-date"></i>
                Âge <span class="required">*</span>
              </label>
              <input type="number" class="form-control" name="Age" min="18" max="80" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-card-text"></i>
                Numéro de Sécurité Sociale <span class="required">*</span>
              </label>
              <input type="text" class="form-control" name="SSN" required>
            </div>
          </div>

          <div class="row">
            <div class="col-md-12 mb-3">
              <label class="form-label">
                <i class="bi-briefcase"></i>
                Profession <span class="required">*</span>
              </label>
              <select class="form-control" name="Occupation" required>
                <option value="">Choisir la profession...</option>
                <option value="Engineer">Ingénieur</option>
                <option value="Teacher">Enseignant</option>
                <option value="Doctor">Médecin</option>
                <option value="Lawyer">Avocat</option>
                <option value="Manager">Directeur</option>
                <option value="Accountant">Comptable</option>
                <option value="Developer">Développeur</option>
                <option value="Scientist">Scientifique</option>
                <option value="Architect">Architecte</option>
                <option value="Consultant">Consultant</option>
                <option value="Other">Autre</option>
              </select>
            </div>
          </div>

          <div class="step-navigation">
            <button type="button" class="btn btn-primary" onclick="nextStep(1)">Continuer <i class="bi-arrow-right"></i></button>
          </div>
        </div>

        <!-- Step 2: Informations financières -->
        <div class="step-card hidden" id="step2">
          <div class="step-header">
            <h4><i class="bi-cash-stack"></i> Informations financières</h4>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-currency-dollar"></i>
                Revenu annuel <span class="required">*</span>
              </label>
              <input type="number" class="form-control" name="Annual_Income" min="0" step="1000" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-wallet2"></i>
                Salaire mensuel net <span class="required">*</span>
              </label>
              <input type="number" class="form-control" name="Monthly_Inhand_Salary" min="0" step="100" required>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-bank"></i>
                Nombre de comptes bancaires
              </label>
              <input type="number" class="form-control" name="Num_Bank_Accounts" min="0" max="10" value="1">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-credit-card"></i>
                Nombre de cartes de crédit
              </label>
              <input type="number" class="form-control" name="Num_Credit_Card" min="0" max="10" value="0">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-percent"></i>
                Taux d'intérêt (%)
              </label>
              <input type="number" class="form-control" name="Interest_Rate" min="0" max="30" step="0.1" value="10">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-list-ol"></i>
                Nombre de prêts en cours
              </label>
              <input type="number" class="form-control" name="Num_of_Loan" min="0" max="10" value="0">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-house-door"></i>
                Type de prêt
              </label>
              <select class="form-control" name="Type_of_Loan">
                <option value="Not Specified">Non spécifié</option>
                <option value="Auto Loan">Prêt automobile</option>
                <option value="Credit-Builder Loan">Prêt de construction de crédit</option>
                <option value="Personal Loan">Prêt personnel</option>
                <option value="Home Equity Loan">Prêt sur valeur domiciliaire</option>
                <option value="Mortgage Loan">Prêt hypothécaire</option>
                <option value="Student Loan">Prêt étudiant</option>
                <option value="Debt Consolidation Loan">Prêt de consolidation de dettes</option>
                <option value="Payday Loan">Prêt sur salaire</option>
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-clock"></i>
                Retard moyen (jours)
              </label>
              <input type="number" class="form-control" name="Delay_from_due_date" min="0" max="365" value="0">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-exclamation-triangle"></i>
                Nombre de paiements en retard
              </label>
              <input type="number" class="form-control" name="Num_of_Delayed_Payment" min="0" max="50" value="0">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-arrow-up-down"></i>
                Changement limite crédit
              </label>
              <input type="number" class="form-control" name="Changed_Credit_Limit" step="100" value="0">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-search"></i>
                Nombre d'enquêtes crédit
              </label>
              <input type="number" class="form-control" name="Num_Credit_Inquiries" min="0" max="20" value="1">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-pie-chart"></i>
                Mix de crédit
              </label>
              <select class="form-control" name="Credit_Mix">
                <option value="Standard">Standard</option>
                <option value="Good">Bon</option>
                <option value="Bad">Mauvais</option>
              </select>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-currency-dollar"></i>
                Dette en cours
              </label>
              <input type="number" class="form-control" name="Outstanding_Debt" min="0" step="100" value="0">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-percent"></i>
                Ratio d'utilisation crédit (%)
              </label>
              <input type="number" class="form-control" name="Credit_Utilization_Ratio" min="0" max="100" step="0.1" value="25">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-calendar-range"></i>
                Âge historique crédit (années)
              </label>
              <input type="number" class="form-control" name="Credit_History_Age" min="0" max="50" step="0.1" value="5">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-check-circle"></i>
                Paiement montant minimum
              </label>
              <select class="form-control" name="Payment_of_Min_Amount">
                <option value="Yes">Oui</option>
                <option value="No">Non</option>
                <option value="NM">Non spécifié</option>
              </select>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-calculator"></i>
                Total EMI mensuel
              </label>
              <input type="number" class="form-control" name="Total_EMI_per_month" min="0" step="50" value="0">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-graph-up"></i>
                Montant investi mensuel
              </label>
              <input type="number" class="form-control" name="Amount_invested_monthly" min="0" step="50" value="0">
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-activity"></i>
                Comportement de paiement
              </label>
              <select class="form-control" name="Payment_Behaviour">
                <option value="Low_spent_Medium_value_payments">Dépenses faibles, paiements moyens</option>
                <option value="High_spent_Small_value_payments">Dépenses élevées, petits paiements</option>
                <option value="Low_spent_Large_value_payments">Dépenses faibles, gros paiements</option>
                <option value="High_spent_Medium_value_payments">Dépenses élevées, paiements moyens</option>
                <option value="High_spent_Large_value_payments">Dépenses élevées, gros paiements</option>
                <option value="Low_spent_Small_value_payments">Dépenses faibles, petits paiements</option>
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">
                <i class="bi-wallet"></i>
                Solde mensuel moyen
              </label>
              <input type="number" class="form-control" name="Monthly_Balance" step="100" value="1000">
            </div>
          </div>

          <div class="step-navigation">
            <button type="button" class="btn btn-outline-secondary" onclick="prevStep(2)"><i class="bi-arrow-left"></i> Précédent</button>
            <button type="button" class="btn btn-primary" onclick="nextStep(2)">Continuer <i class="bi-arrow-right"></i></button>
          </div>
        </div>

        <!-- Step 3: Révision et envoi -->
        <div class="step-card hidden" id="step3">
          <div class="step-header">
            <h4><i class="bi-check-circle"></i> Révision et envoi</h4>
          </div>
          
          <div class="alert alert-info">
            <i class="bi-info-circle"></i>
            <strong>Information :</strong> Votre score de crédit sera calculé automatiquement par notre système d'intelligence artificielle basé sur les informations fournies.
          </div>

          <!-- Consent -->
          <div class="mb-3 form-check">
            <input type="checkbox" class="form-check-input" id="consent" required>
            <label class="form-check-label" for="consent">
              J'autorise la banque à vérifier les informations fournies et à effectuer des vérifications de crédit. <span class="required">*</span>
            </label>
          </div>

          <div class="step-navigation">
            <button type="button" class="btn btn-outline-secondary" onclick="prevStep(3)"><i class="bi-arrow-left"></i> Précédent</button>
            <button type="submit" class="btn btn-success" id="submitBtn">Soumettre la demande <i class="bi-check-circle"></i></button>
          </div>
          
          <div class="mt-3 text-center">
            <small class="text-muted">
              <i class="bi-robot"></i> 
              Votre demande sera analysée automatiquement par IA
            </small>
          </div>
        </div>'''

def replace_form_content():
    """Remplace le contenu du formulaire dans le fichier HTML"""
    
    file_path = r'c:\Users\MSI\Downloads\stageee\templates\demande_credit.html'
    
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trouver le début et la fin du contenu des étapes
        start_marker = '        <!-- Step 1:'
        end_marker = '        </div>\n      </form>'
        
        start_index = content.find(start_marker)
        end_index = content.find(end_marker)
        
        if start_index == -1 or end_index == -1:
            print("❌ Marqueurs non trouvés dans le fichier")
            return False
        
        # Remplacer le contenu
        new_content = (
            content[:start_index] + 
            new_form_content + 
            '\n      </form>' +
            content[end_index + len(end_marker):]
        )
        
        # Sauvegarder
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Formulaire mis à jour avec succès!")
        print("📋 Nouveau formulaire avec 3 étapes :")
        print("   1. Informations d'identité et personnelles")
        print("   2. Informations financières")
        print("   3. Révision et envoi")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    replace_form_content()
