# Configuration SMTP pour l'envoi d'emails
# ⚠️ IMPORTANT: Ne partagez jamais ce fichier avec vos vraies credentials !

# Configuration Zoho Mail
SMTP_CONFIG = {
    'server': 'smtp.zoho.com',
    'port': 587,
    'email': 'hakkaii92@gmail.com',
    'password': 'zSV2nbLdyXtu',
    'use_tls': True
}



# Configuration Outlook/Hotmail (alternative)
# SMTP_CONFIG = {
#     'server': 'smtp-mail.outlook.com',
#     'port': 587,
#     'email': 'votre_email@outlook.com',
#     'password': 'votre_mot_de_passe',
#     'use_tls': True
# }

# Configuration Yahoo (alternative)
# SMTP_CONFIG = {
#     'server': 'smtp.mail.yahoo.com',
#     'port': 587,
#     'email': 'votre_email@yahoo.com',
#     'password': 'votre_mot_de_passe_app',
#     'use_tls': True
# }

# Configuration personnalisée (pour autres fournisseurs)
# SMTP_CONFIG = {
#     'server': 'votre_serveur_smtp.com',
#     'port': 587,  # ou 465 pour SSL
#     'email': 'votre_email@domaine.com',
#     'password': 'votre_mot_de_passe',
#     'use_tls': True  # ou False si vous utilisez SSL sur port 465
# }
