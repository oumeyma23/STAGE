-- ===============================================
-- Script SQL pour ajouter le système de rôles
-- Base de données: stagee
-- ===============================================

USE stagee;

-- 1. Ajouter la colonne 'role' à la table signup
ALTER TABLE `signup` 
ADD COLUMN `role` VARCHAR(20) NOT NULL DEFAULT 'client' AFTER `verifiedpass`;

-- 2. Mettre à jour tous les utilisateurs existants en tant que 'client'
UPDATE `signup` 
SET `role` = 'client' 
WHERE `role` IS NULL OR `role` = '';

-- 3. (OPTIONNEL) Promouvoir un utilisateur existant en admin
-- Décommentez la ligne ci-dessous et remplacez l'email par celui de votre compte
-- UPDATE `signup` SET `role` = 'admin' WHERE `email` = 'votre.email@exemple.com';

-- 4. (OPTIONNEL) Créer un compte admin de test
-- Décommentez les lignes ci-dessous pour créer un compte admin
-- Le mot de passe sera "Admin@123" (à changer après la première connexion)
/*
INSERT INTO `signup` (`name`, `email`, `password`, `verifiedpass`, `role`) 
VALUES (
    'Administrateur',
    'admin@stagee.com',
    'scrypt:32768:8:1$CZHIXqEvFgMCCWbP$3016789378867608fdd055beb2b075b747d5bafb297f280df5e4e3de8eba97497c8eda67572676e1ebbdfdf0bc9c44ec3a92b6b4ab3b037d2c030f321c6fc430',
    '',
    'admin'
);
*/

-- 5. Vérifier les modifications
SELECT id, name, email, role FROM `signup`;

-- ===============================================
-- Instructions d'utilisation:
-- ===============================================
-- 1. Exécutez ce script dans phpMyAdmin ou votre client MySQL
-- 2. Pour créer un admin, décommentez l'option 3 ou 4 ci-dessus
-- 3. Les nouveaux utilisateurs qui s'inscrivent auront automatiquement le rôle 'client'
-- 4. Les admins peuvent changer les rôles via l'interface web
-- ===============================================
