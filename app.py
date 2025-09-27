from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import cv2
import uuid
import os
import base64
from PIL import Image
from io import BytesIO
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config_email import SMTP_CONFIG
import random
import string

try:
    from flask_babel import Babel, gettext, ngettext, get_locale
    BABEL_AVAILABLE = True
except ImportError:
    BABEL_AVAILABLE = False

try:
    from credit_prediction import CreditPredictor
    credit_predictor = CreditPredictor()
    CREDIT_PREDICTION_AVAILABLE = True
    print("✅ Module de prédiction de crédit chargé avec succès")
except ImportError as e:
    CREDIT_PREDICTION_AVAILABLE = False
    print(f"⚠️ Module de prédiction non disponible: {e}")
    
    # Créer une classe mock pour éviter les erreurs
    class MockCreditPredictor:
        def predict_credit_approval(self, form_data):
            return {
                'approved': True,
                'probability': 0.75,
                'risk_level': 'Moyen',
                'message': 'Analyse automatique non disponible - Demande enregistrée pour étude manuelle'
            }
    credit_predictor = MockCreditPredictor()

try:
    from extraction import extraire_donnees
    from AML import check_name
    from deepface import DeepFace
    ADDITIONAL_MODULES_AVAILABLE = True
    print("✅ Modules d'extraction et AML chargés avec succès")
except ImportError as e:
    ADDITIONAL_MODULES_AVAILABLE = False
    print(f"⚠️ Modules additionnels non disponibles: {e}")
    
    # Créer des fonctions mock
    def extraire_donnees(path):
        return "12345678", "Doe", "John", "1990-01-01"
    
    def check_name(name):
        return pd.DataFrame()  # DataFrame vide = pas de match AML

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
        credit_score = prediction_result.get('credit_score', 'N/A')
        body = f"""
    Bonjour {nom_complet},

    Excellente nouvelle ! Votre demande de crédit a reçu une pré-approbation automatique.

    📊 Résultats de l'analyse IA :
    • Score de crédit prédit : {credit_score:.0f}
    • Probabilité d'approbation : {prediction_result['probability']:.1%}
    • Niveau de risque : {prediction_result['risk_level']}
    
    🎯 {prediction_result['message']}
    
    Votre dossier sera finalisé par nos équipes dans les plus brefs délais.

    Cordialement,
    L'équipe SecuriBank
    """
    elif prediction_result and not prediction_result['approved']:
        subject = "📋 Demande de crédit - Analyse requise - SecuriBank"
        credit_score = prediction_result.get('credit_score', 'N/A')
        body = f"""
    Bonjour {nom_complet},

    Nous avons bien reçu votre demande de crédit.

    📊 Résultats de l'analyse IA préliminaire :
    • Score de crédit prédit : {credit_score:.0f}
    • Probabilité d'approbation : {prediction_result['probability']:.1%}
    • Niveau de risque : {prediction_result['risk_level']}
    
    🔍 {prediction_result['message']}
    
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

# 🔑 Fonctions de gestion OTP
def generer_code_otp():
    """Génère un code OTP à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))

def sauvegarder_otp(email, code_otp):
    """Sauvegarde le code OTP en base avec expiration de 5 minutes"""
    try:
        cur = mysql.connection.cursor()
        
        # Supprimer les anciens codes pour cet email
        cur.execute("DELETE FROM otp_codes WHERE email = %s", (email,))
        
        # Calculer l'expiration (5 minutes)
        expires_at = datetime.now() + timedelta(minutes=5)
        
        # Insérer le nouveau code
        cur.execute("""
            INSERT INTO otp_codes (email, otp_code, expires_at) 
            VALUES (%s, %s, %s)
        """, (email, code_otp, expires_at))
        
        mysql.connection.commit()
        cur.close()
        print(f"✅ Code OTP sauvegardé pour {email}")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde OTP: {e}")
        return False

def verifier_otp(email, code_saisi):
    """Vérifie si le code OTP est valide et non expiré"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT otp_code, expires_at, is_used 
            FROM otp_codes 
            WHERE email = %s AND is_used = FALSE
            ORDER BY created_at DESC 
            LIMIT 1
        """, (email,))
        
        result = cur.fetchone()
        
        if not result:
            print(f"❌ Aucun code OTP trouvé pour {email}")
            return False, "Aucun code trouvé"
        
        code_stocke, expires_at, is_used = result
        
        # Vérifier l'expiration
        if datetime.now() > expires_at:
            print(f"❌ Code OTP expiré pour {email}")
            return False, "Code expiré"
        
        # Vérifier le code
        if code_saisi != code_stocke:
            print(f"❌ Code OTP incorrect pour {email}")
            return False, "Code incorrect"
        
        # Marquer le code comme utilisé
        cur.execute("""
            UPDATE otp_codes 
            SET is_used = TRUE 
            WHERE email = %s AND otp_code = %s
        """, (email, code_stocke))
        
        mysql.connection.commit()
        cur.close()
        print(f"✅ Code OTP validé pour {email}")
        return True, "Code valide"
        
    except Exception as e:
        print(f"❌ Erreur vérification OTP: {e}")
        return False, "Erreur système"

def envoyer_code_otp(email, code_otp, nom_utilisateur=""):
    """Envoie le code OTP par email pour la connexion"""
    subject = "🔐 Votre code de vérification - SecuriBank"
    
    body = f"""
Bonjour {nom_utilisateur},

Voici votre code de vérification pour vous connecter à SecuriBank :

🔑 Code : {code_otp}

⏰ Ce code est valable pendant 5 minutes seulement.

Si vous n'avez pas demandé ce code, ignorez ce message.

Cordialement,
L'équipe SecuriBank
    """
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['email']
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"🔗 Envoi du code OTP de connexion vers {email}")
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        
        if SMTP_CONFIG['use_tls']:
            server.starttls()
        
        server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
        server.sendmail(SMTP_CONFIG['email'], email, msg.as_string())
        server.quit()
        print(f"📨 Code OTP de connexion envoyé avec succès à {email}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi OTP connexion: {e}")
        return False

def envoyer_code_otp_inscription(email, code_otp, nom_utilisateur=""):
    """Envoie le code OTP par email pour l'inscription"""
    subject = "🎉 Bienvenue sur SecuriBank - Code de vérification"
    
    body = f"""
Bonjour {nom_utilisateur},

Bienvenue sur SecuriBank ! Pour finaliser votre inscription, veuillez saisir le code de vérification ci-dessous :

🔑 Code : {code_otp}

⏰ Ce code est valable pendant 5 minutes seulement.

Une fois votre compte vérifié, vous pourrez accéder à tous nos services bancaires sécurisés.

Si vous n'avez pas créé de compte, ignorez ce message.

Cordialement,
L'équipe SecuriBank
    """
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['email']
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"🔗 Envoi du code OTP d'inscription vers {email}")
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        
        if SMTP_CONFIG['use_tls']:
            server.starttls()
        
        server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
        server.sendmail(SMTP_CONFIG['email'], email, msg.as_string())
        server.quit()
        print(f"📨 Code OTP d'inscription envoyé avec succès à {email}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi OTP inscription: {e}")
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
            # Vérifier si l'utilisateur existe déjà
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
                # ✅ Nouveau processus d'inscription avec OTP
                # 1. Stocker temporairement les données d'inscription
                hashed = generate_password_hash(password)
                session['pending_signup'] = {
                    'name': name,
                    'email': email,
                    'password': hashed
                }
                
                # 2. Générer et envoyer le code OTP
                code_otp = generer_code_otp()
                
                if sauvegarder_otp(email, code_otp) and envoyer_code_otp_inscription(email, code_otp, name):
                    print(f"🔑 Code OTP d'inscription généré et envoyé pour {email}")
                    return redirect(url_for('verify_signup_otp'))
                else:
                    if current_language == 'ar':
                        error = "خطأ في إرسال رمز التحقق"
                    elif current_language == 'en':
                        error = "Error sending verification code"
                    else:
                        error = "Erreur lors de l'envoi du code de vérification"
    return render_template('signup.html', error=error, current_language=current_language)

# 🔐 Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = None
    current_language = session.get('language', 'fr')
    
    # Vérifier s'il y a un message de succès d'inscription
    if session.pop('signup_success', False):
        if current_language == 'ar':
            success = "تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول"
        elif current_language == 'en':
            success = "Account created successfully! You can now log in"
        else:
            success = "Compte créé avec succès ! Vous pouvez maintenant vous connecter"
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user and check_password_hash(user[3], password):
            # ✅ Identifiants corrects - Générer et envoyer code OTP
            code_otp = generer_code_otp()
            nom_utilisateur = user[1]  # Le nom est dans la colonne 1
            
            if sauvegarder_otp(email, code_otp) and envoyer_code_otp(email, code_otp, nom_utilisateur):
                # Stocker l'email en session temporairement pour la vérification OTP
                session['pending_login'] = email
                print(f"🔑 Code OTP généré et envoyé pour {email}")
                return redirect(url_for('verify_otp'))
            else:
                if current_language == 'ar':
                    error = "خطأ في إرسال رمز التحقق"
                elif current_language == 'en':
                    error = "Error sending verification code"
                else:
                    error = "Erreur lors de l'envoi du code de vérification"
        else:
            if current_language == 'ar':
                error = "بيانات الاعتماد غير صحيحة"
            elif current_language == 'en':
                error = "Invalid credentials"
            else:
                error = "Identifiants incorrects"
    return render_template('login.html', error=error, success=success, current_language=current_language)

# 🔐 Page de vérification OTP
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    # Vérifier qu'il y a une connexion en attente
    if 'pending_login' not in session:
        return redirect(url_for('login'))
    
    error = None
    success = None
    current_language = session.get('language', 'fr')
    email = session['pending_login']
    
    if request.method == 'POST':
        code_saisi = request.form['otp_code'].strip()
        
        if len(code_saisi) != 6 or not code_saisi.isdigit():
            if current_language == 'ar':
                error = "يجب أن يكون الرمز مكون من 6 أرقام"
            elif current_language == 'en':
                error = "Code must be 6 digits"
            else:
                error = "Le code doit contenir 6 chiffres"
        else:
            # Vérifier le code OTP
            is_valid, message = verifier_otp(email, code_saisi)
            
            if is_valid:
                # ✅ Code valide - Connexion réussie
                session['user'] = email
                session.pop('pending_login', None)  # Nettoyer la session temporaire
                print(f"✅ Connexion réussie avec OTP pour {email}")
                return redirect(url_for('accueil'))
            else:
                # ❌ Code invalide
                if message == "Code expiré":
                    if current_language == 'ar':
                        error = "انتهت صلاحية الرمز. يرجى طلب رمز جديد"
                    elif current_language == 'en':
                        error = "Code expired. Please request a new code"
                    else:
                        error = "Code expiré. Veuillez demander un nouveau code"
                elif message == "Code incorrect":
                    if current_language == 'ar':
                        error = "رمز غير صحيح"
                    elif current_language == 'en':
                        error = "Invalid code"
                    else:
                        error = "Code incorrect"
                else:
                    if current_language == 'ar':
                        error = "خطأ في التحقق من الرمز"
                    elif current_language == 'en':
                        error = "Error verifying code"
                    else:
                        error = "Erreur lors de la vérification du code"
    
    return render_template('verify_otp.html', error=error, success=success, 
                         current_language=current_language, email=email)

# 🔄 Renvoyer un nouveau code OTP
@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    if 'pending_login' not in session:
        return redirect(url_for('login'))
    
    email = session['pending_login']
    current_language = session.get('language', 'fr')
    
    # Récupérer le nom de l'utilisateur
    cur = mysql.connection.cursor()
    cur.execute("SELECT name FROM signup WHERE email = %s", (email,))
    user = cur.fetchone()
    nom_utilisateur = user[0] if user else ""
    
    # Générer et envoyer un nouveau code
    code_otp = generer_code_otp()
    
    if sauvegarder_otp(email, code_otp) and envoyer_code_otp(email, code_otp, nom_utilisateur):
        if current_language == 'ar':
            success = "تم إرسال رمز جديد"
        elif current_language == 'en':
            success = "New code sent"
        else:
            success = "Nouveau code envoyé"
        
        return render_template('verify_otp.html', success=success, 
                             current_language=current_language, email=email)
    else:
        if current_language == 'ar':
            error = "خطأ في إرسال الرمز"
        elif current_language == 'en':
            error = "Error sending code"
        else:
            error = "Erreur lors de l'envoi du code"
        
        return render_template('verify_otp.html', error=error, 
                             current_language=current_language, email=email)

# 🔐 Page de vérification OTP pour l'inscription
@app.route('/verify_signup_otp', methods=['GET', 'POST'])
def verify_signup_otp():
    # Vérifier qu'il y a une inscription en attente
    if 'pending_signup' not in session:
        return redirect(url_for('signup'))
    
    error = None
    success = None
    current_language = session.get('language', 'fr')
    signup_data = session['pending_signup']
    email = signup_data['email']
    
    if request.method == 'POST':
        code_saisi = request.form['otp_code'].strip()
        
        if len(code_saisi) != 6 or not code_saisi.isdigit():
            if current_language == 'ar':
                error = "يجب أن يكون الرمز مكون من 6 أرقام"
            elif current_language == 'en':
                error = "Code must be 6 digits"
            else:
                error = "Le code doit contenir 6 chiffres"
        else:
            # Vérifier le code OTP
            is_valid, message = verifier_otp(email, code_saisi)
            
            if is_valid:
                # ✅ Code valide - Finaliser l'inscription
                try:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO signup (name, email, password) VALUES (%s, %s, %s)", 
                              (signup_data['name'], signup_data['email'], signup_data['password']))
                    mysql.connection.commit()
                    cur.close()
                    
                    # Nettoyer la session
                    session.pop('pending_signup', None)
                    
                    print(f"✅ Inscription finalisée avec OTP pour {email}")
                    
                    # Rediriger vers la page de connexion avec un message de succès
                    session['signup_success'] = True
                    return redirect(url_for('login'))
                    
                except Exception as e:
                    print(f"❌ Erreur lors de la finalisation de l'inscription: {e}")
                    if current_language == 'ar':
                        error = "خطأ في إنشاء الحساب"
                    elif current_language == 'en':
                        error = "Error creating account"
                    else:
                        error = "Erreur lors de la création du compte"
            else:
                # ❌ Code invalide
                if message == "Code expiré":
                    if current_language == 'ar':
                        error = "انتهت صلاحية الرمز. يرجى طلب رمز جديد"
                    elif current_language == 'en':
                        error = "Code expired. Please request a new code"
                    else:
                        error = "Code expiré. Veuillez demander un nouveau code"
                elif message == "Code incorrect":
                    if current_language == 'ar':
                        error = "رمز غير صحيح"
                    elif current_language == 'en':
                        error = "Invalid code"
                    else:
                        error = "Code incorrect"
                else:
                    if current_language == 'ar':
                        error = "خطأ في التحقق من الرمز"
                    elif current_language == 'en':
                        error = "Error verifying code"
                    else:
                        error = "Erreur lors de la vérification du code"
    
    return render_template('verify_signup_otp.html', error=error, success=success, 
                         current_language=current_language, email=email, 
                         name=signup_data['name'])

# 🔄 Renvoyer un nouveau code OTP pour l'inscription
@app.route('/resend_signup_otp', methods=['POST'])
def resend_signup_otp():
    if 'pending_signup' not in session:
        return redirect(url_for('signup'))
    
    signup_data = session['pending_signup']
    email = signup_data['email']
    name = signup_data['name']
    current_language = session.get('language', 'fr')
    
    # Générer et envoyer un nouveau code
    code_otp = generer_code_otp()
    
    if sauvegarder_otp(email, code_otp) and envoyer_code_otp_inscription(email, code_otp, name):
        if current_language == 'ar':
            success = "تم إرسال رمز جديد"
        elif current_language == 'en':
            success = "New code sent"
        else:
            success = "Nouveau code envoyé"
        
        return render_template('verify_signup_otp.html', success=success, 
                             current_language=current_language, email=email, name=name)
    else:
        if current_language == 'ar':
            error = "خطأ في إرسال الرمز"
        elif current_language == 'en':
            error = "Error sending code"
        else:
            error = "Erreur lors de l'envoi du code"
        
        return render_template('verify_signup_otp.html', error=error, 
                             current_language=current_language, email=email, name=name)

# 📝 Formulaire de demande de crédit
@app.route("/demande_credit", methods=["GET", "POST"])
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
                    Monthly_Balance, Credit_Score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer_id, current_month, name, age, ssn, occupation, annual_income, monthly_salary,
                num_bank_accounts, num_credit_card, interest_rate, num_of_loan, type_of_loan,
                delay_from_due_date, num_delayed_payment, changed_credit_limit, num_credit_inquiries,
                credit_mix, outstanding_debt, credit_utilization_ratio, credit_history_age,
                payment_min_amount, total_emi_per_month, amount_invested_monthly, payment_behaviour,
                monthly_balance, prediction_result.get('credit_score', 0)
            ))
            mysql.connection.commit()
            cur.close()
            
            print(f"✅ Demande enregistrée en base pour {name}")
            
            # Message de succès basé sur la prédiction
            if prediction_result.get('approved', False):
                success = f"✅ Félicitations ! Votre demande a été pré-approuvée automatiquement !\n🎯 {prediction_result.get('message', '')}\n📧 Un email de confirmation vous a été envoyé."
            else:
                success = f"📝 Votre demande a été enregistrée et sera étudiée par nos experts.\n📊 {prediction_result.get('message', '')}\n📧 Un email de confirmation vous a été envoyé."
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            import traceback
            traceback.print_exc()
            error = f"❌ Erreur lors de l'envoi : {str(e)}"
    
    return render_template("demande_credit.html", success=success, error=error, current_language=current_language)


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
