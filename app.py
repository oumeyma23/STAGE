from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import SMTP_CONFIG


app = Flask(__name__)
app.secret_key = 'secret_key'

# 🔗 Connexion à MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stagee'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

def envoyer_mail_inscription_refusee(destinataire, nom_complet):
    """Envoie un email d'avertissement lors de l'inscription pour liste rouge"""
    subject = "Avertissement d'inscription - SecuriBank"
    body = f"""
    Bonjour {nom_complet},

    Nous vous informons que votre tentative d'inscription sur notre plateforme SecuriBank a été détectée.

    Votre nom figure sur une liste de surveillance AML (Anti-Money Laundering).

    Pour des raisons de sécurité et de conformité réglementaire, votre inscription ne peut pas être validée.

    Si vous pensez qu'il s'agit d'une erreur, veuillez contacter notre service client.

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
        
        print(f"📤 Envoi email d'inscription vers {destinataire}")
        server.sendmail(SMTP_CONFIG['email'], destinataire, msg.as_string())
        server.quit()
        print("📨 Email d'avertissement d'inscription envoyé avec succès.")
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
        print(f"❌ Erreur d'envoi de mail d'inscription: {type(e).__name__}: {e}")
        return False

# 📝 Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        verifiedpass = request.form['confirm']

        if password != verifiedpass:
            error = "Les mots de passe ne correspondent pas"
        else:
            # 🔍 Vérification AML lors de l'inscription
            print(f"🧪 Vérification AML pour l'inscription de : {name}")
            result = check_name(name)
            
            if not result.empty:
                # Le nom figure sur la liste rouge
                print(f"🚨 Nom '{name}' trouvé sur liste rouge lors de l'inscription")
                envoyer_mail_inscription_refusee(email, name)
                error = "Votre inscription ne peut pas être validée pour des raisons de sécurité. Un email d'information vous a été envoyé."
                return render_template('signup.html', error=error)
            
            # Si le nom n'est pas sur la liste rouge, continuer l'inscription normale
            hashed = generate_password_hash(password)
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM signup WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                error = "Utilisateur déjà existant"
            else:
                cur.execute("INSERT INTO signup (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed))
                mysql.connection.commit()
                print(f"✅ Inscription réussie pour : {name}")
                return redirect(url_for('login'))
    return render_template('signup.html', error=error)

# 🔐 Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE email = %s", (email,))
        user = cur.fetchone()
        if user and check_password_hash(user[3], password):
            session['user'] = email
            return redirect(url_for('formulaire'))
        else:
            error = "Identifiants incorrects"
    return render_template('login.html', error=error)

# 🏠 Page d'accueil
@app.route('/accueil')
def accueil():
    return render_template('accueil.html')

@app.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    if 'user' not in session:
        return redirect(url_for('login'))

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
                    return render_template('formulaire.html', data=data, error_popup=error_popup)
                print(f"🧪 Résultat AML pour '{nom_complet}' : {result}")


            except ValueError:
                error_popup = "❌ This is not a Tunisian ID card. Please upload a valid document."

    return render_template('formulaire.html', data=data, error_popup=error_popup)

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

    # ✅ Si tout est bon, redirige vers accueil ou affiche un message de succès
    return redirect(url_for('accueil'))



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
