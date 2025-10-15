-- ========================================
-- COMMANDE SQL PRINCIPALE
-- À exécuter dans phpMyAdmin
-- Base de données: stagee
-- ========================================

-- 1. AJOUTER LA COLONNE ROLE
ALTER TABLE `signup` ADD COLUMN `role` VARCHAR(20) NOT NULL DEFAULT 'client' AFTER `verifiedpass`;

-- 2. CRÉER UN ADMIN (CHANGEZ L'EMAIL !)
UPDATE `signup` SET `role` = 'admin' WHERE `email` = 'oumeyma.sokkeh@esprit.tn';

-- 3. VÉRIFIER
SELECT id, name, email, role FROM `signup`;

-- ========================================
-- C'EST TOUT ! 🎉
-- ========================================
