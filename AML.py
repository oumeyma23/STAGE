import pandas as pd
import jellyfish

# 🔤 Fonction de translittération arabe vers alphabet latin
def arabic_to_latin(arabic_name):
    mapping = {
        'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
        'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's',
        'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y',
        'ء': '', 'ى': 'a', 'ة': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'aa'
    }
    return ''.join([mapping.get(c, c) for c in arabic_name])

# 🔧 Normalisation et translittération si nécessaire
def preprocess(name):
    name = str(name).strip().lower()
    if any('\u0600' <= c <= '\u06FF' for c in name):  # détecte les caractères arabes
        name = arabic_to_latin(name)
    return name

# 🔍 Comparaison avec les algorithmes de similarité
def is_similar(input_name, target_name):
    input_proc = preprocess(input_name)
    target_proc = preprocess(target_name)

    jaro = jellyfish.jaro_winkler_similarity(input_proc, target_proc)
    levenshtein = jellyfish.levenshtein_distance(input_proc, target_proc)
    soundex_match = jellyfish.soundex(input_proc) == jellyfish.soundex(target_proc)

    print(f"🧪 Comparaison : '{input_proc}' vs '{target_proc}' | Jaro: {jaro:.3f} | Levenshtein: {levenshtein} | Soundex: {soundex_match}")

    return jaro > 0.88 or levenshtein < 4 or soundex_match

# 📂 Chargement de la base AML et vérification du nom
def check_name(input_name):
    df = pd.read_excel(r"C:\Users\MSI\Downloads\AML-augmented.xlsx")

    # 🔍 Vérification du nom de colonne
    if "Full Name" not in df.columns:
        print("❌ La colonne 'Full Name' est introuvable. Colonnes disponibles :")
        print(df.columns.tolist())
        return pd.DataFrame()

    matches = []
    for _, row in df.iterrows():
        full_name = str(row.get("Full Name", "")).strip()
        if full_name:  # éviter les lignes vides
            if is_similar(input_name, full_name):
                matches.append(row)
    return pd.DataFrame(matches)

# 🧪 Interface utilisateur
if __name__ == "__main__":
    input_name = input("✍️ Entrez le nom à vérifier : ").strip()
    print(f"📝 Nom saisi : '{input_name}'")

    result = check_name(input_name)

    if not result.empty:
        print("\n🚨 Ce nom correspond à une personne sur liste rouge !")
        print(result[['Full Name', 'Risk Category', 'Source', 'Risk Type', 'Notes']])
    else:
        print("\n✅ Aucun match trouvé.")
