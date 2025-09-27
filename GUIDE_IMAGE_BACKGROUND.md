# 🎨 Guide Complet - Image de Background SecuriBank

## 📐 TAILLES RECOMMANDÉES

### 🏆 **TAILLE PARFAITE**
```
Largeur : 1920px
Hauteur : 1080px
Ratio : 16:9
Format : JPG
Poids : 500KB - 1MB
```

### 📱 **COMPATIBILITÉ MULTI-ÉCRANS**
- **Mobile :** 1366x768px (minimum)
- **Desktop :** 1920x1080px (recommandé)
- **4K :** 2560x1440px (optimal)
- **Ultra :** 3840x2160px (maximum)

## 🔧 **COMMENT CHANGER L'IMAGE**

### **Méthode 1 : Rapide**
1. Copiez votre image dans : `static/images/`
2. Renommez-la : `bank-facade.jpg`
3. ✅ **C'est tout !** L'image sera automatiquement utilisée

### **Méthode 2 : Personnalisée**
1. Copiez votre image avec n'importe quel nom
2. Lancez : `python change_background.py`
3. Suivez les instructions du script

### **Méthode 3 : Manuelle**
Modifiez dans `static/css/styles.css` ligne 35 :
```css
background: url('../images/VOTRE_IMAGE.jpg') center center / cover no-repeat fixed,
```

## 🎯 **CONFIGURATION CSS ACTUELLE**

Votre CSS est déjà parfaitement configuré :
```css
background-size: cover;      /* Couvre toute la page */
background-position: center; /* Centré */
background-repeat: no-repeat;/* Pas de répétition */
background-attachment: fixed;/* Fixe au scroll */
```

## 📊 **OPTIMISATION DE L'IMAGE**

### **Formats Recommandés**
- **JPG :** Photos, paysages (plus petit)
- **PNG :** Logos, transparence (plus lourd)
- **WebP :** Moderne, très optimisé

### **Compression**
- **Qualité :** 80-90% (bon compromis)
- **Poids :** 500KB - 1MB maximum
- **Outils :** TinyPNG, Photoshop, GIMP

## 🎨 **CONSEILS DESIGN**

### **Composition**
- ✅ Éléments importants au **centre**
- ✅ Éviter les détails sur les **bords**
- ✅ **Contraste** suffisant pour le texte
- ✅ **Couleurs** harmonieuses avec l'orange SecuriBank

### **Style Bancaire**
- 🏛️ Architecture classique (colonnes)
- 🔒 Éléments de sécurité (coffres)
- 💼 Ambiance professionnelle
- 🏢 Façades de banque modernes

## 🚀 **TESTS RAPIDES**

### **Test 1 : Taille d'Écran**
Ouvrez : `test_image_sizes.html` dans votre navigateur

### **Test 2 : Application Live**
1. Lancez : `python app.py`
2. Ouvrez : http://127.0.0.1:5000
3. Testez sur différentes tailles d'écran

### **Test 3 : Script Automatique**
```bash
python change_background.py
```

## 📝 **CHECKLIST FINALE**

- [ ] Image en **1920x1080px** minimum
- [ ] Format **JPG** optimisé
- [ ] Poids **< 1MB**
- [ ] Placée dans **static/images/**
- [ ] Nommée **bank-facade.jpg** (ou CSS modifié)
- [ ] Testée sur mobile et desktop
- [ ] Contraste OK avec les formulaires

## 🎯 **RÉSULTAT ATTENDU**

Avec ces paramètres, votre image :
- ✅ Couvre **100% de la page**
- ✅ S'adapte à **tous les écrans**
- ✅ Reste **fixe** au scroll
- ✅ Se **centre** automatiquement
- ✅ **Ne se répète pas**
- ✅ **Charge rapidement**

## 🆘 **DÉPANNAGE**

### **Image pas visible ?**
1. Vérifiez le chemin : `static/images/bank-facade.jpg`
2. Vérifiez les permissions du fichier
3. Rechargez la page (Ctrl+F5)

### **Image déformée ?**
1. Utilisez un ratio 16:9
2. Vérifiez la résolution minimum (1920x1080)

### **Image trop lourde ?**
1. Compressez avec TinyPNG
2. Réduisez la qualité à 80%
3. Convertissez en WebP

---

**🎉 Avec ce guide, votre image de background sera parfaite sur SecuriBank !**
