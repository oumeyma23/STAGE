# 🚀 Guide d'Installation - Système OTP SecuriBank

## 📋 Prérequis

Avant d'installer le système OTP, assurez-vous d'avoir :

✅ **MySQL/MariaDB** démarré  
✅ **Base de données** `stagee` créée  
✅ **Configuration email** dans `config_email.py`  
✅ **Flask-MySQLdb** installé  

## 🔧 Installation Étape par Étape

### Étape 1 : Créer la Table OTP

**Option A : Via le script Python**
```bash
python init_otp_db.py
```

**Option B : Via MySQL directement**
```sql
USE stagee;

CREATE TABLE IF NOT EXISTS otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Étape 2 : Vérifier la Configuration Email

Assurez-vous que `config_email.py` contient :
```python
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',  # Ou votre serveur SMTP
    'port': 587,
    'email': 'votre-email@gmail.com',
    'password': 'votre-mot-de-passe-app',
    'use_tls': True
}
```

### Étape 3 : Tester le Système

```bash
python test_otp_system.py
```

### Étape 4 : Démarrer l'Application

```bash
python app.py
```

## 🧪 Tests de Fonctionnement

### Test 1 : Connexion avec OTP

1. Allez sur `http://localhost:5000/login`
2. Saisissez vos identifiants corrects
3. Vous devriez être redirigé vers `/verify_otp`
4. Vérifiez votre email pour le code à 6 chiffres
5. Saisissez le code et validez

### Test 2 : Gestion des Erreurs

**Code expiré :**
- Attendez 5 minutes après réception
- Tentez de saisir le code → Erreur "Code expiré"

**Code incorrect :**
- Saisissez `999999` → Erreur "Code incorrect"

**Renvoi de code :**
- Cliquez sur "Renvoyer le code"
- Nouveau code reçu par email

## 🔍 Vérification de l'Installation

### Vérifier la Table OTP
```sql
DESCRIBE otp_codes;
SELECT COUNT(*) FROM otp_codes;
```

### Vérifier les Logs
L'application affiche des logs détaillés :
```
🔑 Code OTP généré et envoyé pour user@example.com
✅ Code OTP sauvegardé pour user@example.com
📨 Code OTP envoyé avec succès à user@example.com
```

## 🚨 Résolution des Problèmes

### Erreur : "Table doesn't exist"
```bash
python init_otp_db.py
```

### Erreur : "SMTP Authentication failed"
- Vérifiez `config_email.py`
- Activez l'authentification à 2 facteurs sur Gmail
- Générez un mot de passe d'application

### Erreur : "No module named 'MySQLdb'"
```bash
pip install Flask-MySQLdb
```

### Page OTP ne s'affiche pas
- Vérifiez que `templates/verify_otp.html` existe
- Redémarrez l'application Flask

## 📊 Monitoring et Maintenance

### Nettoyage Automatique
Le système nettoie automatiquement les codes expirés.

### Nettoyage Manuel (optionnel)
```sql
DELETE FROM otp_codes WHERE expires_at < NOW() OR is_used = TRUE;
```

### Statistiques
```sql
-- Codes générés aujourd'hui
SELECT COUNT(*) FROM otp_codes WHERE DATE(created_at) = CURDATE();

-- Codes expirés
SELECT COUNT(*) FROM otp_codes WHERE expires_at < NOW() AND is_used = FALSE;

-- Taux de réussite
SELECT 
    COUNT(*) as total,
    SUM(is_used) as utilises,
    ROUND(SUM(is_used) / COUNT(*) * 100, 2) as taux_reussite
FROM otp_codes WHERE DATE(created_at) = CURDATE();
```

## 🎯 Points de Contrôle

Après installation, vérifiez :

✅ **Table créée** : `otp_codes` existe dans la base  
✅ **Email configuré** : Réception des codes de test  
✅ **Interface OTP** : Page `/verify_otp` accessible  
✅ **Workflow complet** : Login → OTP → Accueil  
✅ **Multilingue** : FR/EN/AR fonctionnent  
✅ **Responsive** : Mobile et desktop OK  

## 🔐 Sécurité Post-Installation

### Recommandations
- Utilisez HTTPS en production
- Configurez un serveur SMTP dédié
- Surveillez les tentatives de brute force
- Limitez les tentatives par IP
- Activez les logs d'audit

### Variables d'Environnement (Production)
```bash
export MYSQL_PASSWORD="mot-de-passe-securise"
export SMTP_PASSWORD="mot-de-passe-email-app"
export FLASK_SECRET_KEY="cle-secrete-longue-et-complexe"
```

---

## ✅ Installation Terminée !

Votre système OTP SecuriBank est maintenant opérationnel ! 

🎉 **Félicitations** - Vous avez ajouté une couche de sécurité bancaire professionnelle à votre application !

Pour toute question ou problème, consultez les logs de l'application ou le fichier `README_OTP.md` pour plus de détails techniques.
