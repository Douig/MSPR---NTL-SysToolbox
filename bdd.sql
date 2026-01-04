-- Création de la base de données
CREATE DATABASE IF NOT EXISTS demo_db;
USE demo_db;

-- =========================
-- TABLE CLIENTS
-- =========================
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO clients (nom, prenom, email) VALUES
('Dupont', 'Paul', 'paul.dupont@gmail.com'),
('Martin', 'Sarah', 'sarah.martin@gmail.com'),
('Durand', 'Lucas', 'lucas.durand@gmail.com');

-- =========================
-- TABLE PRODUITS
-- =========================
CREATE TABLE produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    prix DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO produits (nom, description, prix, stock) VALUES
('Clavier', 'Clavier mécanique', 79.99, 50),
('Souris', 'Souris gaming', 49.99, 80),
('Ecran', 'Ecran 24 pouces', 199.99, 20);

-- =========================
-- TABLE COMMANDES
-- =========================
CREATE TABLE commandes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

INSERT INTO commandes (client_id, total) VALUES
(1, 129.98),
(2, 199.99),
(3, 79.99);

-- =========================
-- TABLE LOGS
-- =========================
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255),
    date_action DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO logs (action) VALUES
('Création client'),
('Ajout produit'),
('Commande validée');
