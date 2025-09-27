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

# 🔄 Vérification d'inversion de mots (prénom/nom)
def check_word_inversion(input_name, target_name):
    """Vérifie si les noms sont des inversions l'un de l'autre"""
    input_words = input_name.split()
    target_words = target_name.split()
    
    # Cas 1: Mots identiques dans un ordre différent
    if len(input_words) == len(target_words) and set(input_words) == set(target_words):
        return True
    
    # Cas 2: Deux mots - vérification croisée avec seuils ajustés
    if len(input_words) == 2 and len(target_words) == 2:
        # Ordre normal: input[0] vs target[0] et input[1] vs target[1]
        normal_sim = (jellyfish.jaro_winkler_similarity(input_words[0], target_words[0]) + 
                     jellyfish.jaro_winkler_similarity(input_words[1], target_words[1])) / 2
        
        # Ordre inversé: input[0] vs target[1] et input[1] vs target[0]
        inverse_sim = (jellyfish.jaro_winkler_similarity(input_words[0], target_words[1]) + 
                      jellyfish.jaro_winkler_similarity(input_words[1], target_words[0])) / 2
        
        # Seuil plus permissif pour les inversions (0.75 au lieu de 0.85)
        max_similarity = max(normal_sim, inverse_sim)
        
        if max_similarity > 0.75:
            print(f"🔄 Inversion détectée: similarité normale={normal_sim:.3f}, inversée={inverse_sim:.3f}")
            return True
    
    # Cas 3: Vérification avec des mots partiellement similaires
    if len(input_words) >= 2 and len(target_words) >= 2:
        for i_word in input_words:
            for t_word in target_words:
                if jellyfish.jaro_winkler_similarity(i_word, t_word) > 0.85:
                    # Si on trouve un mot très similaire, vérifier les autres
                    remaining_input = [w for w in input_words if w != i_word]
                    remaining_target = [w for w in target_words if w != t_word]
                    
                    if remaining_input and remaining_target:
                        for ri_word in remaining_input:
                            for rt_word in remaining_target:
                                if jellyfish.jaro_winkler_similarity(ri_word, rt_word) > 0.75:
                                    print(f"🔄 Correspondance partielle: '{i_word}' ≈ '{t_word}' et '{ri_word}' ≈ '{rt_word}'")
                                    return True
    
    return False

# 🔍 Comparaison avec les algorithmes de similarité
def is_similar(input_name, target_name):
    input_proc = preprocess(input_name)
    target_proc = preprocess(target_name)

    jaro = jellyfish.jaro_winkler_similarity(input_proc, target_proc)
    levenshtein = jellyfish.levenshtein_distance(input_proc, target_proc)
    soundex_match = jellyfish.soundex(input_proc) == jellyfish.soundex(target_proc)
    
    # Vérification d'inversion de mots
    word_inversion = check_word_inversion(input_proc, target_proc)

    print(f"🧪 Comparaison : '{input_proc}' vs '{target_proc}' | Jaro: {jaro:.3f} | Levenshtein: {levenshtein} | Soundex: {soundex_match} | Inversion: {word_inversion}")

    # Critères ajustés pour une détection plus réaliste
    name_length = min(len(input_proc), len(target_proc))
    
    if name_length < 8:
        # Seuils plus permissifs pour les noms courts
        is_match = jaro > 0.65 or levenshtein < 4 or soundex_match or word_inversion
    else:
        # Seuils standards pour les noms longs
        is_match = jaro > 0.75 or levenshtein < 5 or soundex_match or word_inversion
    
    if is_match:
        print(f"✅ MATCH trouvé: Jaro={jaro:.3f} | Levenshtein={levenshtein} | Soundex={soundex_match} | Inversion={word_inversion}")
    
    return is_match

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
        # Afficher toutes les colonnes disponibles
        print("Colonnes disponibles:", result.columns.tolist())
        # Afficher seulement les colonnes qui existent
        available_cols = ['Full Name']
        for col in ['Risk Category', 'Source', 'Risk Type', 'Notes']:
            if col in result.columns:
                available_cols.append(col)
        print(result[available_cols])
    else:
        print("\n✅ Aucun match trouvé.")
