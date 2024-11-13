-- SUPPRESSION DES TABLES
drop table if exists Fait;
drop table if exists Pousse_dans;
drop table if exists Entretient;
drop table if exists Attendre;
drop table if exists Pousse;
drop table if exists Traitement;
drop table if exists Mois;
drop table if exists Compost;
drop table if exists Défaut;
drop table if exists Actions;
drop table if exists Dates;
drop table if exists Fruits_Légumes_et_aromate;
drop table if exists Parcelle;
drop table if exists Adhérent;

-- CREATION DES TABLES
CREATE TABLE Adhérent(
   Id_Adhérent INT AUTO_INCREMENT NOT NULL,
   Nom VARCHAR(50),
   Prénom VARCHAR(50),
   Adresse VARCHAR(50),
   Téléphone VARCHAR(10),
   PRIMARY KEY(Id_Adhérent)
);

CREATE TABLE Parcelle(
   Id_Parcelle INT AUTO_INCREMENT NOT NULL,
   Longueur DECIMAL(4,2),
   Largeur DECIMAL(4,2),
   PRIMARY KEY(Id_Parcelle)
);

CREATE TABLE Fruits_Légumes_et_aromate(
   Id_FruitLégume INT AUTO_INCREMENT NOT NULL,
   Libellé VARCHAR(20),
   PRIMARY KEY(Id_FruitLégume)
);

CREATE TABLE Dates(
   JJ_MM_AAAA DATE,
   PRIMARY KEY(JJ_MM_AAAA)
);

CREATE TABLE Actions(
   Id_Actions INT AUTO_INCREMENT NOT NULL,
   Libellé VARCHAR(20),
   PRIMARY KEY(Id_Actions)
);

CREATE TABLE Défaut(
   Id_Défaut INT AUTO_INCREMENT NOT NULL,
   Libellé VARCHAR(20),
   Id_Actions INT NOT NULL,
   PRIMARY KEY(Id_Défaut),
   FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions)
);

CREATE TABLE Compost(
   Id_Compost INT AUTO_INCREMENT NOT NULL ,
   Taille VARCHAR(20),
   Localisation VARCHAR(20),
   PRIMARY KEY(Id_Compost)
);

CREATE TABLE Mois(
   Id_Mois INT AUTO_INCREMENT NOT NULL ,
   Libellé VARCHAR(20),
   PRIMARY KEY(Id_Mois)
);

CREATE TABLE Traitement(
   Id_traitement INT AUTO_INCREMENT NOT NULL ,
   Libellé VARCHAR(20),
   Id_Actions INT NOT NULL,
   PRIMARY KEY(Id_traitement),
   UNIQUE(Id_Actions),
   FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions)
);

CREATE TABLE Pousse(
   Id_FruitLégume INT AUTO_INCREMENT NOT NULL,
   Id_Mois INT,
   PRIMARY KEY(Id_FruitLégume, Id_Mois),
   FOREIGN KEY(Id_FruitLégume) REFERENCES Fruits_Légumes_et_aromate(Id_FruitLégume),
   FOREIGN KEY(Id_Mois) REFERENCES Mois(Id_Mois)
);

CREATE TABLE Attendre(
   Id_traitement INT ,
   Id_traitement_1 INT,
   PRIMARY KEY(Id_traitement, Id_traitement_1),
   FOREIGN KEY(Id_traitement) REFERENCES Traitement(Id_traitement),
   FOREIGN KEY(Id_traitement_1) REFERENCES Traitement(Id_traitement)
);

CREATE TABLE Entretient(
   Id_Adhérent INT,
   JJ_MM_AAAA DATE,
   Id_Actions INT,
   Id_Compost INT,
   Quantité DECIMAL(4,2),
   PRIMARY KEY(Id_Adhérent, JJ_MM_AAAA, Id_Actions, Id_Compost),
   FOREIGN KEY(Id_Adhérent) REFERENCES Adhérent(Id_Adhérent),
   FOREIGN KEY(JJ_MM_AAAA) REFERENCES Dates(JJ_MM_AAAA),
   FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions),
   FOREIGN KEY(Id_Compost) REFERENCES Compost(Id_Compost)
);

CREATE TABLE Pousse_dans(
   Id_Parcelle INT,
   Id_FruitLégume INT,
   PRIMARY KEY(Id_Parcelle, Id_FruitLégume),
   FOREIGN KEY(Id_Parcelle) REFERENCES Parcelle(Id_Parcelle),
   FOREIGN KEY(Id_FruitLégume) REFERENCES Fruits_Légumes_et_aromate(Id_FruitLégume)
);

CREATE TABLE Fait(
   Id_Adhérent INT,
   Id_Parcelle INT,
   JJ_MM_AAAA DATE,
   Id_Actions INT,
   Quantité DECIMAL(4,2),
   PRIMARY KEY(Id_Adhérent, Id_Parcelle, JJ_MM_AAAA, Id_Actions),
   FOREIGN KEY(Id_Adhérent) REFERENCES Adhérent(Id_Adhérent),
   FOREIGN KEY(Id_Parcelle) REFERENCES Parcelle(Id_Parcelle),
   FOREIGN KEY(JJ_MM_AAAA) REFERENCES Dates(JJ_MM_AAAA),
   FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions)
);

-- AJOUT DES DONNÉES DANS LES TABLES
INSERT INTO Adhérent (Nom, Prénom, Adresse, Téléphone) VALUES
('DUSSOL','Luca','Quelque part sur rien', '0612345561'),
('HETRU','Owen','La-bas','0698765432'),
('DUFOSSEZ','Oscar','Près de là','0630893144');

INSERT INTO Parcelle (Longueur, Largeur) VALUES
(2.5,1),
(3,2),
(1.5,2);

INSERT INTO Fruits_Légumes_et_aromate (Libellé) VALUES
('Pastèque'),
('Persil'),
('Piment d espelette'),
('Tomate'),
('Pomme de terre');

INSERT INTO Actions (Libellé) VALUES
('Planter'),
('Récolter'),
('Vider'),
('Ajouter'),
('Signale'),
('Nettoyer');

INSERT INTO Compost (Taille, Localisation) VALUES
('12','B4'),
('10','D4');

INSERT INTO Mois (Libellé) VALUES
('Janvier'),
('Février'),
('Mars'),
('Avril'),
('Mai'),
('Juin'),
('Juillet'),
('Aout'),
('Septembre'),
('Octobre'),
('Novembre'),
('Décembre');


-- AJOUT DES DONNÉES DANS LES ASSOCIATIONS

INSERT INTO Défaut (Libellé, Id_Actions)
SELECT Défaut.Libellé , Actions.Id_Actions
FROM Actions
WHERE (Actions.Libellé LIKE 'Signale');

-- REQUETES
SELECT * FROM Mois;
