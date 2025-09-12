import easyocr
import re
import arabic_reshaper
from bidi.algorithm import get_display

# Initialisation du lecteur OCR
reader = easyocr.Reader(['ar', 'en'])

# Mois arabes pour formater la date
mois_arabe = {
    "جانفي": "01", "فيفري": "02", "مارس": "03", "أفريل": "04",
    "ماي": "05", "جوان": "06", "جويلية": "07", "جويية": "07", "أوت": "08",
    "سبتمبر": "09", "أكتوبر": "10", "نوفمبر": "11", "ديسمبر": "12"
}

# Correction de l'affichage du texte arabe
def fix_arabic(text):
    if not text or text == "Non trouvé":
        return "Non trouvé"
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

# Formatage de la date en JJ/MM/AAAA
def formater_date(date_text):
    match = re.search(r"(\d{1,2})\s+([\u0600-\u06FF]+)\s+(19|20)\d{2}", date_text)
    if match:
        jour = match.group(1).zfill(2)
        mois = mois_arabe.get(match.group(2), "??")
        annee = match.group(3)
        return f"{jour}/{mois}/{annee}"
    return date_text

# Fonction principale d'extraction
def extraire_donnees(image_path):
    # Lecture OCR
    results = reader.readtext(image_path, detail=0, paragraph=True)
    full_text = " ".join(results)

    # 🔍 Affichage pour débogage
    print("🔍 OCR lines:")
    for line in results:
        print("•", line)

    # Vérification par numéro CIN
    cin_match = re.search(r"\b\d{8}\b", full_text)
    if not cin_match:
        raise ValueError("❌ CIN number not found. Please upload a valid ID card.")

    # Vérification par mots-clés partiels
    keywords = ["بطاقة", "هوية", "الجمهورية", "IDENTITE", "IDENTITY"]
    found_keywords = [kw for kw in keywords if kw in full_text]
    if not found_keywords:
        print("⚠️ Aucun mot-clé officiel détecté, mais CIN présent.")

    # Extraction des données
    nom_match = re.search(r"(?:اللقب|اللفب)\s*[:：]?\s*([\w\u0600-\u06FF]+)", full_text)
    prenom_match = re.search(r"(?:الاسم|الاسـم)\s*[:：]?\s*([\w\u0600-\u06FF]+)", full_text)
    date_match = re.search(r"\d{1,2}\s+[\u0600-\u06FF]+\s+(19|20)\d{2}", full_text)
    year_match = re.search(r"(19|20)\d{2}", full_text)

    cin = cin_match.group()
    nom = fix_arabic(nom_match.group(1)) if nom_match else "Non trouvé"
    prenom = fix_arabic(prenom_match.group(1)) if prenom_match else "Non trouvé"

    if date_match:
        date_naissance = formater_date(date_match.group())
    elif year_match:
        date_naissance = f"Year only: {year_match.group()}"
    else:
        date_naissance = "Not found"

    return cin, nom, prenom, date_naissance
