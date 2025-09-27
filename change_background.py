#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour changer facilement l'image de background de SecuriBank
"""

import os
import shutil
from pathlib import Path

def list_available_images():
    """Liste les images disponibles dans le dossier images"""
    images_dir = Path("static/images")
    if not images_dir.exists():
        print("❌ Dossier images non trouvé")
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
    images = []
    
    for file in images_dir.iterdir():
        if file.suffix.lower() in image_extensions:
            images.append(file.name)
    
    return images

def show_current_background():
    """Affiche la configuration actuelle du background"""
    css_file = Path("static/css/styles.css")
    if not css_file.exists():
        print("❌ Fichier CSS non trouvé")
        return
    
    print("🎨 Configuration actuelle du background:")
    print("=" * 50)
    
    with open(css_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if 'background: url(' in line and '../images/' in line:
            print(f"Ligne {i+1}: {line.strip()}")

def change_background_image(new_image_name):
    """Change l'image de background dans le CSS"""
    css_file = Path("static/css/styles.css")
    if not css_file.exists():
        print("❌ Fichier CSS non trouvé")
        return False
    
    # Lire le fichier CSS
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer l'ancienne image
    old_pattern = "url('../images/bank-facade.jpg')"
    new_pattern = f"url('../images/{new_image_name}')"
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        
        # Sauvegarder
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Image de background changée vers: {new_image_name}")
        return True
    else:
        print("❌ Pattern d'image non trouvé dans le CSS")
        return False

def suggest_images():
    """Suggère des images de background appropriées"""
    suggestions = [
        {
            "name": "bank-modern.jpg",
            "description": "Façade de banque moderne avec verre et acier",
            "url": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=2000"
        },
        {
            "name": "bank-classic.jpg", 
            "description": "Architecture bancaire classique avec colonnes",
            "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=2000"
        },
        {
            "name": "bank-security.jpg",
            "description": "Coffre-fort et sécurité bancaire",
            "url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=2000"
        },
        {
            "name": "fintech-abstract.jpg",
            "description": "Design fintech moderne et abstrait",
            "url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=2000"
        }
    ]
    
    print("💡 Suggestions d'images de background:")
    print("=" * 50)
    
    for i, img in enumerate(suggestions, 1):
        print(f"{i}. {img['name']}")
        print(f"   📝 {img['description']}")
        print(f"   🔗 {img['url']}")
        print()

def copy_image_to_project(source_path, new_name=None):
    """Copie une image vers le dossier du projet"""
    source = Path(source_path)
    if not source.exists():
        print(f"❌ Fichier source non trouvé: {source_path}")
        return False
    
    images_dir = Path("static/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    
    if new_name:
        destination = images_dir / new_name
    else:
        destination = images_dir / source.name
    
    try:
        shutil.copy2(source, destination)
        print(f"✅ Image copiée: {destination.name}")
        return destination.name
    except Exception as e:
        print(f"❌ Erreur lors de la copie: {e}")
        return False

def main():
    print("🎨 SecuriBank - Changement d'Image de Background")
    print("=" * 60)
    
    while True:
        print("\n🔧 Options disponibles:")
        print("1. 📋 Voir la configuration actuelle")
        print("2. 📁 Lister les images disponibles")
        print("3. 🖼️  Changer l'image de background")
        print("4. 📥 Copier une nouvelle image")
        print("5. 💡 Voir les suggestions d'images")
        print("6. 🚪 Quitter")
        
        choice = input("\n👉 Votre choix (1-6): ").strip()
        
        if choice == "1":
            show_current_background()
            
        elif choice == "2":
            images = list_available_images()
            if images:
                print("📁 Images disponibles:")
                for img in images:
                    print(f"   - {img}")
            else:
                print("📁 Aucune image trouvée dans static/images/")
                
        elif choice == "3":
            images = list_available_images()
            if not images:
                print("❌ Aucune image disponible. Ajoutez d'abord une image (option 4)")
                continue
                
            print("📁 Images disponibles:")
            for i, img in enumerate(images, 1):
                print(f"   {i}. {img}")
            
            try:
                img_choice = int(input("👉 Numéro de l'image à utiliser: ")) - 1
                if 0 <= img_choice < len(images):
                    change_background_image(images[img_choice])
                else:
                    print("❌ Numéro invalide")
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")
                
        elif choice == "4":
            source_path = input("👉 Chemin vers votre image: ").strip().strip('"')
            new_name = input("👉 Nouveau nom (optionnel, Entrée pour garder le nom): ").strip()
            
            if not new_name:
                new_name = None
                
            result = copy_image_to_project(source_path, new_name)
            if result:
                use_now = input("👉 Utiliser cette image maintenant? (o/n): ").strip().lower()
                if use_now in ['o', 'oui', 'y', 'yes']:
                    change_background_image(result)
                    
        elif choice == "5":
            suggest_images()
            
        elif choice == "6":
            print("👋 Au revoir!")
            break
            
        else:
            print("❌ Choix invalide")

if __name__ == "__main__":
    main()
