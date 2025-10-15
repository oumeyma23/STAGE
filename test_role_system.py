"""
Script de test pour vérifier l'implémentation du système de rôles
"""
import mysql.connector
from mysql.connector import Error

def test_role_system():
    """Teste l'implémentation du système de rôles"""
    print("🔍 Vérification du système de rôles...")
    print("=" * 60)
    
    try:
        # Connexion à la base de données
        connection = mysql.connector.connect(
            host='localhost',
            database='stagee',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("✅ Connexion à la base de données réussie\n")
            
            # 1. Vérifier si la colonne 'role' existe
            print("1️⃣  Vérification de la colonne 'role'...")
            cursor.execute("SHOW COLUMNS FROM signup LIKE 'role'")
            role_column = cursor.fetchone()
            
            if role_column:
                print("   ✅ La colonne 'role' existe")
                print(f"   📋 Type: {role_column[1]}")
                print(f"   📋 Défaut: {role_column[4]}\n")
            else:
                print("   ❌ La colonne 'role' n'existe pas!")
                print("   💡 Exécutez le fichier add_role_column.sql\n")
                return False
            
            # 2. Vérifier les utilisateurs existants
            print("2️⃣  Vérification des utilisateurs...")
            cursor.execute("SELECT id, name, email, role FROM signup")
            users = cursor.fetchall()
            
            if users:
                print(f"   📊 {len(users)} utilisateur(s) trouvé(s):\n")
                
                clients = 0
                admins = 0
                
                for user in users:
                    user_id, name, email, role = user
                    role_icon = "👤" if role == 'client' else "🛡️"
                    print(f"   {role_icon} ID: {user_id} | {name} | {email} | Rôle: {role}")
                    
                    if role == 'client':
                        clients += 1
                    elif role == 'admin':
                        admins += 1
                
                print(f"\n   📈 Statistiques:")
                print(f"      👥 Total: {len(users)}")
                print(f"      👤 Clients: {clients}")
                print(f"      🛡️  Admins: {admins}\n")
                
                if admins == 0:
                    print("   ⚠️  Aucun administrateur trouvé!")
                    print("   💡 Pour créer un admin, exécutez:")
                    print("      UPDATE signup SET role = 'admin' WHERE email = 'votre@email.com';\n")
                else:
                    print(f"   ✅ {admins} administrateur(s) configuré(s)\n")
            else:
                print("   ℹ️  Aucun utilisateur trouvé\n")
            
            # 3. Vérifier la valeur par défaut
            print("3️⃣  Test de la valeur par défaut...")
            cursor.execute("SHOW CREATE TABLE signup")
            create_table = cursor.fetchone()[1]
            
            if "DEFAULT 'client'" in create_table:
                print("   ✅ La valeur par défaut 'client' est bien configurée\n")
            else:
                print("   ⚠️  La valeur par défaut pourrait ne pas être configurée correctement\n")
            
            # 4. Recommandations
            print("4️⃣  Recommandations:")
            print("   📝 Fichiers créés/modifiés:")
            print("      • app.py (modifié)")
            print("      • templates/admin_dashboard.html (nouveau)")
            print("      • templates/admin_users.html (nouveau)")
            print("      • add_role_column.sql (nouveau)")
            print("      • ROLE_SYSTEM_README.md (nouveau)")
            print("\n   🚀 Pour tester l'application:")
            print("      1. Assurez-vous d'avoir au moins un admin")
            print("      2. Lancez l'application: python app.py")
            print("      3. Connectez-vous avec un compte admin")
            print("      4. Vous serez redirigé vers /admin/dashboard\n")
            
            print("=" * 60)
            print("✅ Vérification terminée avec succès!")
            return True
            
    except Error as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Connexion à la base de données fermée")

if __name__ == "__main__":
    test_role_system()
