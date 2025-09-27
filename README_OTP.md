# 🔐 Système de Vérification OTP - SecuriBank

## 📋 Vue d'ensemble

Le système OTP (One-Time Password) ajoute une couche de sécurité supplémentaire au processus de connexion de SecuriBank. Après avoir saisi leurs identifiants corrects, les utilisateurs reçoivent un code à 6 chiffres par email qu'ils doivent saisir pour finaliser leur connexion.

## 🚀 Installation et Configuration

### 1. Créer la table OTP dans la base de données

```bash
python init_otp_db.py
```

Ou exécutez manuellement le SQL :
```sql
CREATE TABLE IF NOT EXISTS otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at)
);
```

### 2. Configuration Email

Assurez-vous que le fichier `config_email.py` est correctement configuré avec vos paramètres SMTP.

### 3. Tester le système

```bash
python test_otp_system.py
```

## 🔄 Processus de Connexion avec OTP

### Étape 1 : Connexion Initiale
- L'utilisateur saisit son email et mot de passe sur `/login`
- Le système vérifie les identifiants

### Étape 2 : Génération et Envoi du Code
- Si les identifiants sont corrects :
  - Un code OTP à 6 chiffres est généré
  - Le code est sauvegardé en base avec expiration (5 minutes)
  - Un email est envoyé à l'utilisateur
  - Redirection vers `/verify_otp`

### Étape 3 : Vérification du Code
- L'utilisateur saisit le code reçu par email
- Le système vérifie :
  - ✅ Code correct et non expiré → Connexion réussie
  - ❌ Code incorrect/expiré → Erreur affichée

### Étape 4 : Options Supplémentaires
- **Renvoyer un code** : Nouveau code généré et envoyé
- **Retour à la connexion** : Annule le processus OTP

## 📧 Format de l'Email OTP

```
Objet: 🔐 Votre code de vérification - SecuriBank

Bonjour [Nom],

Voici votre code de vérification pour vous connecter à SecuriBank :

🔑 Code : 123456

⏰ Ce code est valable pendant 5 minutes seulement.

Si vous n'avez pas demandé ce code, ignorez ce message.

Cordialement,
L'équipe SecuriBank
```

## 🛡️ Sécurité

### Mesures de Protection
- **Expiration** : Codes valables 5 minutes seulement
- **Usage unique** : Chaque code ne peut être utilisé qu'une fois
- **Nettoyage automatique** : Suppression des anciens codes
- **Validation stricte** : 6 chiffres exactement
- **Protection session** : Email stocké temporairement en session

### Gestion des Erreurs
- Code expiré → Message d'erreur + option de renvoi
- Code incorrect → Message d'erreur
- Code déjà utilisé → Rejeté automatiquement
- Session invalide → Redirection vers login

## 🌐 Support Multilingue

Le système OTP supporte 3 langues :
- **Français** (par défaut)
- **English** 
- **العربية** (Arabe avec support RTL)

## 📱 Interface Utilisateur

### Page de Vérification (`/verify_otp`)
- **Design moderne** : Card avec backdrop-filter et ombres
- **Champ OTP stylisé** : Input centré avec espacement des caractères
- **Timer en temps réel** : Compte à rebours de 5 minutes
- **Auto-focus** : Curseur automatiquement dans le champ
- **Auto-submit** : Soumission automatique à 6 chiffres
- **Bouton de renvoi** : Désactivé pendant 30 secondes
- **Notice de sécurité** : Rappel de ne pas partager le code

### Fonctionnalités UX
- Validation en temps réel (chiffres seulement)
- Formatage automatique de l'input
- Messages d'erreur contextuels
- Design responsive mobile/desktop
- Cohérence avec le thème SecuriBank

## 🔧 API et Routes

### Nouvelles Routes
- `GET/POST /verify_otp` : Page de vérification du code
- `POST /resend_otp` : Renvoyer un nouveau code

### Fonctions Principales
- `generer_code_otp()` : Génère un code à 6 chiffres
- `sauvegarder_otp(email, code)` : Sauvegarde en base avec expiration
- `verifier_otp(email, code)` : Valide le code et le marque comme utilisé
- `envoyer_code_otp(email, code, nom)` : Envoie l'email avec le code

## 🧪 Tests et Débogage

### Script de Test
```bash
python test_otp_system.py
```

Tests inclus :
- Génération de codes OTP
- Workflow complet (génération → vérification → usage unique)
- Gestion des codes incorrects
- Test d'envoi d'email (optionnel)

### Logs de Débogage
Le système affiche des logs détaillés :
```
🔑 Code OTP généré et envoyé pour user@example.com
✅ Code OTP sauvegardé pour user@example.com
📨 Code OTP envoyé avec succès à user@example.com
✅ Code OTP validé pour user@example.com
```

## 🚨 Maintenance

### Nettoyage Automatique
Les codes expirés et utilisés sont automatiquement supprimés lors de nouvelles générations.

### Nettoyage Manuel
```sql
DELETE FROM otp_codes WHERE expires_at < NOW() OR is_used = TRUE;
```

### Monitoring
Surveillez les métriques :
- Taux de réussite des envois d'emails
- Temps de validation des codes
- Codes expirés vs utilisés

## 📊 Statistiques

Le système permet de tracker :
- Nombre de codes générés
- Taux de validation réussie
- Codes expirés
- Tentatives de réutilisation

---

## 🎯 Avantages du Système OTP

✅ **Sécurité renforcée** : Protection contre les accès non autorisés
✅ **Expérience utilisateur fluide** : Interface moderne et intuitive  
✅ **Multilingue** : Support FR/EN/AR
✅ **Responsive** : Fonctionne sur tous les appareils
✅ **Maintenance facile** : Logs détaillés et nettoyage automatique
✅ **Intégration transparente** : S'intègre parfaitement avec l'existant

Le système OTP de SecuriBank offre une sécurité bancaire de niveau professionnel tout en conservant une expérience utilisateur exceptionnelle ! 🏦🔒
