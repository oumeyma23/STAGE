from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
try:
    from flask_babel import Babel, gettext, ngettext, get_locale
    BABEL_AVAILABLE = True
except ImportError:
    BABEL_AVAILABLE = False
from werkzeug.security import generate_password_hash, check_password_hash
from extraction import extraire_donnees
import os
from deepface import DeepFace
from PIL import Image
from io import BytesIO
import base64
import uuid
import cv2
import traceback
from AML import check_name
from credit_prediction import credit_predictor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import SMTP_CONFIG


app = Flask(__name__)
app.secret_key = 'secret_key'

# Configuration Babel
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français', 
    'ar': 'العربية'
}

def get_locale():
    # 1. Si l'utilisateur a choisi une langue, l'utiliser
    if 'language' in session:
        return session['language']
    # 2. Sinon, utiliser la langue préférée du navigateur
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'fr'

if BABEL_AVAILABLE:
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    babel = Babel(app, locale_selector=get_locale)

# 🔗 Connexion à MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stagee'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route pour changer de langue
@app.route('/set_language/<language>')
def set_language(language=None):
    if language in app.config['LANGUAGES']:
        session['language'] = language
        print(f"🌐 Langue changée vers: {language}")
        print(f"🌐 Session language: {session.get('language')}")
    return redirect(request.referrer or url_for('accueil'))
def envoyer_mail(destinataire, nom_complet):
    subject = "Refus de crédit - SecuriBank"
    body = f"""
    Bonjour {nom_complet},

    Votre demande a été refusée car votre nom figure sur une liste de surveillance AML.

    Vous ne pouvez pas obtenir un crédit pour le moment.

    Cordialement,
    SecuriBank
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['email']
    msg['To'] = destinataire
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        print(f"🔗 Connexion au serveur SMTP {SMTP_CONFIG['server']}:{SMTP_CONFIG['port']}")
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.set_debuglevel(1)  # Active le debug SMTP
        
        if SMTP_CONFIG['use_tls']:
            print("🔐 Activation TLS...")
            server.starttls()
        
        print(f"🔑 Authentification avec {SMTP_CONFIG['email']}")
        server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
        
        print(f"📤 Envoi email vers {destinataire}")
        server.sendmail(SMTP_CONFIG['email'], destinataire, msg.as_string())
        server.quit()
        print("📨 Email envoyé avec succès.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erreur d'authentification SMTP: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Destinataire refusé: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ Serveur SMTP déconnecté: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur d'envoi de mail: {type(e).__name__}: {e}")
        return False

def envoyer_mail_confirmation_demande(destinataire, nom_complet, prediction_result=None):
    """Envoie un email de confirmation d'enregistrement de demande de crédit"""
    if prediction_result and prediction_result['approved']:
        subject = "✅ Pré-approbation de crédit - SecuriBank"
        body = f"""
    Bonjour {nom_complet},

    Excellente nouvelle ! Votre demande de crédit a reçu une pré-approbation automatique.

    📊 Résultats de l'analyse :
    • Probabilité d'approbation : {prediction_result['probability']:.1%}
    • Niveau de risque : {prediction_result['risk_level']}
    
    Votre dossier sera finalisé par nos équipes dans les plus brefs délais.

    Cordialement,
    L'équipe SecuriBank
    """
    elif prediction_result and not prediction_result['approved']:
        subject = "❌ Demande de crédit - Analyse requise - SecuriBank"
        body = f"""
    Bonjour {nom_complet},

    Nous avons bien reçu votre demande de crédit.

    📊 Résultats de l'analyse préliminaire :
    • Probabilité d'approbation : {prediction_result['probability']:.1%}
    • Niveau de risque : {prediction_result['risk_level']}
    
    Votre dossier nécessite une étude approfondie par nos experts.
    Nous vous répondrons dans les plus brefs délais.

    Cordialement,
    L'équipe SecuriBank
    """
    else:
        subject = "Confirmation de demande de crédit - SecuriBank"
        body = f"""
    Bonjour {nom_complet},

    Nous avons bien reçu votre demande de crédit.

    Votre dossier est actuellement en cours d'étude par nos équipes.

    Nous vous répondrons dans les plus brefs délais concernant la suite à donner à votre demande.

    En cas de questions, n'hésitez pas à nous contacter.

    Cordialement,
    L'équipe SecuriBank
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['email']
    msg['To'] = destinataire
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        print(f"🔗 Connexion au serveur SMTP {SMTP_CONFIG['server']}:{SMTP_CONFIG['port']}")
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.set_debuglevel(1)  # Active le debug SMTP
        
        if SMTP_CONFIG['use_tls']:
            print("🔐 Activation TLS...")
            server.starttls()
        
        print(f"🔑 Authentification avec {SMTP_CONFIG['email']}")
        server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
        
        print(f"📤 Envoi email de confirmation vers {destinataire}")
        server.sendmail(SMTP_CONFIG['email'], destinataire, msg.as_string())
        server.quit()
        print("📨 Email de confirmation envoyé avec succès.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erreur d'authentification SMTP: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Destinataire refusé: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ Serveur SMTP déconnecté: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur d'envoi de mail de confirmation: {type(e).__name__}: {e}")
        return False

# 📝 Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    current_language = session.get('language', 'fr')
    if request.method == 'POST':
        name = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        verifiedpass = request.form['confirm']

        if password != verifiedpass:
            if current_language == 'ar':
                error = "كلمات المرور غير متطابقة"
            elif current_language == 'en':
                error = "Passwords do not match"
            else:
                error = "Les mots de passe ne correspondent pas"
        else:
            # Inscription normale sans vérification AML
            hashed = generate_password_hash(password)
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM signup WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                if current_language == 'ar':
                    error = "المستخدم موجود بالفعل"
                elif current_language == 'en':
                    error = "User already exists"
                else:
                    error = "Utilisateur déjà existant"
            else:
                cur.execute("INSERT INTO signup (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed))
                mysql.connection.commit()
                print(f"✅ Inscription réussie pour : {name}")
                return redirect(url_for('login'))
    return render_template('signup.html', error=error, current_language=current_language)

# 🔐 Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    current_language = session.get('language', 'fr')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE email = %s", (email,))
        user = cur.fetchone()
        if user and check_password_hash(user[3], password):
            session['user'] = email
            return redirect(url_for('accueil'))
        else:
            if current_language == 'ar':
                error = "بيانات الاعتماد غير صحيحة"
            elif current_language == 'en':
                error = "Invalid credentials"
            else:
                error = "Identifiants incorrects"
    return render_template('login.html', error=error, current_language=current_language)
# 📝 Formulaire de demande de crédit
@app.route("/demande_credit", methods=["GET", "POST"])
def demande_credit():
    if "user" not in session:
        return redirect(url_for("login"))

    success, error = None, None

    if request.method == "POST":
        try:
            # Récupération des champs
            nom = request.form.get("nom")
            prenom = request.form.get("prenom")
            date_naissance = request.form.get("date_naissance")
            lieu_naissance = request.form.get("lieu_naissance")
            cin = request.form.get("document_id")
            nationalite = request.form.get("nationalite")
            adresse = request.form.get("adresse")
            telephone = request.form.get("telephone")
            email = request.form.get("email")
            situation_familiale = request.form.get("situation_familiale")
            enfants = request.form.get("enfants")

            profession = request.form.get("profession")
            employeur = request.form.get("employeur")
            secteur = request.form.get("secteur")
            type_contrat = request.form.get("type_contrat")
            anciennete = request.form.get("anciennete")
            revenu = request.form.get("revenu")
            autres_revenus = request.form.get("autres_revenus")

            revenu_menage = request.form.get("revenu_menage")
            depenses = request.form.get("depenses")
            credits_en_cours = request.form.get("credits_en_cours")
            compte_banque = request.form.get("compte_banque")
            epargne = request.form.get("epargne")

            type_credit = request.form.get("type_credit")
            montant = request.form.get("montant")
            duree = request.form.get("duree")
            objet = request.form.get("objet")
            garanties = request.form.get("garanties")
            
            nom_complet = f"{prenom} {nom}"

            # 🤖 Prédiction automatique du crédit
            prediction_result = credit_predictor.predict_credit_approval(request.form)
            print(f"🤖 Résultat de la prédiction pour {nom_complet}: {prediction_result}")
            
            # Insertion en base avec le résultat de la prédiction
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO demandes_credit
                (nom, prenom, date_naissance, lieu_naissance, cin, nationalite, adresse, telephone, email, situation_familiale, enfants,
                profession, employeur, secteur, type_contrat, anciennete, revenu, autres_revenus,
                revenu_menage, depenses, credits_en_cours, compte_banque, epargne,
                type_credit, montant, duree, objet, garanties)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s)
            """, (nom, prenom, date_naissance, lieu_naissance, cin, nationalite, adresse, telephone, email, situation_familiale, enfants,
                  profession, employeur, secteur, type_contrat, anciennete, revenu, autres_revenus,
                  revenu_menage, depenses, credits_en_cours, compte_banque, epargne,
                  type_credit, montant, duree, objet, garanties))
            mysql.connection.commit()
            cur.close()
            
            # Envoi de l'email de confirmation avec résultat de prédiction
            envoyer_mail_confirmation_demande(email, nom_complet, prediction_result)
            
            # Message de succès personnalisé selon la prédiction
            if prediction_result['approved']:
                success = f"✅ Félicitations ! Votre demande a été pré-approuvée automatiquement !\n🎯 {prediction_result['message']}\n📧 Un email de confirmation vous a été envoyé."
            else:
                success = f"📝 Votre demande a été enregistrée et sera étudiée par nos experts.\n📊 {prediction_result['message']}\n📧 Un email de confirmation vous a été envoyé."
        except Exception as e:
            mysql.connection.rollback()
            error = f"❌ Erreur lors de l’envoi : {e}"

    return render_template("demande_credit.html", success=success, error=error)


# 🏠 Page d'accueil
@app.route('/accueil')
def accueil():
    current_language = session.get('language', 'fr')
    print(f"🌐 Page accueil - Langue actuelle: {current_language}")
    return render_template('accueil.html', current_language=current_language)

# Route racine qui redirige vers accueil
@app.route('/')
def index():
    return redirect(url_for('accueil'))

@app.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_language = session.get('language', 'fr')
    data = None
    error_popup = None

    if request.method == 'POST':
        file = request.files['image']
        email_utilisateur = request.form.get('email')  # récupère l'email du formulaire

        if file:
            filename = f"cin_{uuid.uuid4().hex}.jpg"
            cin_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(cin_path)
            session['cin_path'] = cin_path

            try:
                cin, nom, prenom, date = extraire_donnees(cin_path)
                nom_complet = f"{prenom} {nom}"
                data = {
                    'cin': cin,
                    'nom': nom,
                    'prenom': prenom,
                    'date': date
                }

                # 🔍 Vérification AML
                result = check_name(nom_complet)
                if not result.empty:
                    envoyer_mail(email_utilisateur, nom_complet)
                    error_popup = "❌ Votre nom figure sur une liste AML. Vous ne pouvez pas obtenir un crédit."
                    return render_template('formulaire.html', data=data, error_popup=error_popup, current_language=current_language)
                print(f"🧪 Résultat AML pour '{nom_complet}' : {result}")


            except ValueError:
                error_popup = "❌ This is not a Tunisian ID card. Please upload a valid document."

    return render_template('formulaire.html', data=data, error_popup=error_popup, current_language=current_language)


@app.route('/save', methods=['POST'])
def save():
    cin = request.form['cin']
    nom = request.form['nom']
    prenom = request.form['prenom']
    date = request.form['date']
    email = request.form['email']
    nom_complet = f"{prenom} {nom}"

    print(f"🧪 Comparaison AML déclenchée pour : {nom_complet}")
    result = check_name(nom_complet)
    print(f"🧪 Résultat AML : {result}")

    if not result.empty:
        envoyer_mail(email, nom_complet)
        error_popup = "❌ Ce nom figure sur une liste AML. Crédit refusé."
        data = {
            'cin': cin,
            'nom': nom,
            'prenom': prenom,
            'date': date
        }
        return render_template('formulaire.html', data=data, error_popup=error_popup)

    # ✅ Si tout est bon, redirige vers demande_credit
    return redirect(url_for('demande_credit'))



# 🧠 Vérification faciale
@app.route('/verify_face', methods=['POST'])
def verify_face():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)

    try:
        live_image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return jsonify({'message': f'❌ Erreur lors du traitement de l’image capturée : {str(e)}'}), 400

    live_filename = f"live_{uuid.uuid4().hex}.jpg"
    live_path = os.path.join(UPLOAD_FOLDER, live_filename)
    live_image.save(live_path)

    cin_path = session.get('cin_path')
    if not cin_path or not os.path.exists(cin_path):
        return jsonify({'message': "❌ Image CIN introuvable. Veuillez d'abord l'uploader."}), 400

    # Vérifie que les deux images sont lisibles
    if cv2.imread(cin_path) is None:
        return jsonify({'message': "❌ L’image CIN est illisible ou corrompue."}), 400
    if cv2.imread(live_path) is None:
        return jsonify({'message': "❌ L’image live est illisible ou corrompue."}), 400

    try:
        result = DeepFace.verify(
            img1_path=cin_path,
            img2_path=live_path,
            model_name='VGG-Face',
            detector_backend='opencv'
        )
        distance = result.get("distance", None)
        threshold = result.get("threshold", None)

        if result["verified"]:
            message = "✅ Identity confirmed"
        elif distance is not None and threshold is not None:
            message = f"❌ Not the same person"
        else:
            message = "❌ Face not recognized"

        return jsonify({'message': message})
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("❌ Trace complète DeepFace :", traceback_str)
        return jsonify({'message': f'❌ Erreur DeepFace : {str(e)}'}), 500

# 🔓 Déconnexion
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cin_path', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
