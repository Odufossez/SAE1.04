USE oscar_data;
-- SUPPRESSION DES TABLES
drop table if exists Recolte;
drop table if exists Entretient;
drop table if exists Attendre;
drop table if exists Pousse;
drop table if exists Traitement;
drop table if exists Mois;
drop table if exists Compost;
drop table if exists Défaut;
drop table if exists Actions;
drop table if exists Parcelle;
drop table if exists Fruits_Legumes_et_aromate;
drop table if exists Adherent;

-- CREATION DES TABLES
CREATE TABLE Adherent(
   Id_Adherent INT AUTO_INCREMENT NOT NULL,
   NomPrenom VARCHAR(50),
   Adresse VARCHAR(50),
   Telephone VARCHAR(10),
   PRIMARY KEY(Id_Adherent)
);

CREATE TABLE Fruits_Legumes_et_aromate(
    Id_FruitLegume INT AUTO_INCREMENT NOT NULL,
    Libelle_FruitLegume VARCHAR(20),

    PRIMARY KEY(Id_FruitLegume)
);

CREATE TABLE Parcelle(
    Id_Parcelle INT AUTO_INCREMENT NOT NULL,
    Nom_Parcelle VARCHAR(4),
    Surface NUMERIC(4,2),
    Plante_id INT,

    PRIMARY KEY(Id_Parcelle),
    FOREIGN KEY(plante_id) REFERENCES Fruits_Legumes_et_aromate(Id_FruitLegume)
);

CREATE TABLE Actions(
    Id_Actions INT AUTO_INCREMENT NOT NULL,
    Libelle_action VARCHAR(20),

    PRIMARY KEY(Id_Actions)
);

CREATE TABLE Défaut(
    Id_Defaut INT AUTO_INCREMENT NOT NULL,
    Libelle_Defaut VARCHAR(20),
    Id_Actions INT UNIQUE,

    PRIMARY KEY(Id_Defaut),
    FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions)
);

CREATE TABLE Compost(
    Id_Compost INT AUTO_INCREMENT NOT NULL ,
    Taille NUMERIC(4,2),
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
    Libelle_traitement VARCHAR(20),
    Id_Actions INT,

    PRIMARY KEY(Id_traitement),
    FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions)
);

CREATE TABLE Pousse(
    Id_FruitLégume INT AUTO_INCREMENT NOT NULL,
    Id_mois_a_planter INT,

    PRIMARY KEY(Id_FruitLégume, Id_mois_a_planter),
    FOREIGN KEY(Id_FruitLégume) REFERENCES Fruits_Legumes_et_aromate(Id_FruitLegume),
    FOREIGN KEY(Id_mois_a_planter) REFERENCES Mois(Id_Mois)
);

CREATE TABLE Attendre(
    Id_traitement INT ,
    Id_traitement_1 INT,
    temps_attente VARCHAR(20),

    PRIMARY KEY(Id_traitement, Id_traitement_1),
    FOREIGN KEY(Id_traitement) REFERENCES Traitement(Id_traitement),
    FOREIGN KEY(Id_traitement_1) REFERENCES Traitement(Id_traitement)
);

CREATE TABLE Entretient(
    Id_Entretient INT NOT NULL AUTO_INCREMENT ,
    Id_Adherent INT,
    Date_Entretient DATE,
    Id_Actions INT,
    Id_Compost INT,
    Quantite DECIMAL(4,2),

    PRIMARY KEY(Id_Entretient),
    FOREIGN KEY(Id_Adherent) REFERENCES Adherent(Id_Adherent),
    FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions),
    FOREIGN KEY(Id_Compost) REFERENCES Compost(Id_Compost)
);

CREATE TABLE Recolte(
    Id_Recolte INT NOT NULL AUTO_INCREMENT ,
    Id_Adherent INT,
    Id_Parcelle INT,
    Id_plante INT ,
    Date_Recolte DATE,
    Id_Actions INT,
    Quantite DECIMAL(4,2),

    PRIMARY KEY(Id_Recolte),
    FOREIGN KEY(Id_Adherent) REFERENCES Adherent(Id_Adherent),
    FOREIGN KEY(Id_Parcelle) REFERENCES Parcelle(Id_Parcelle),
    FOREIGN KEY(Id_Actions) REFERENCES Actions(Id_Actions),
    FOREIGN KEY(Id_plante) REFERENCES Fruits_Legumes_et_aromate(Id_FruitLegume)
);

-- AJOUT DES DONNÉES DANS LES TABLES
INSERT INTO Adherent (NomPrenom, Adresse, Telephone) VALUES
('DUSSOL Luca','3 Rue du Cadre', '0612345561'),
('HETRU Owen','12 Avenue du Peuple','0698765432'),
('DUFOSSEZ Oscar','6 Impasse de la Loutre','0630893144'),
('MARTIN Julie', '23 Rue des Lilas', '0682379156'),
('DUPONT Hugo', '14 Avenue des Champs', '0654893021'),
('LECLERC Camille', '5 Boulevard des Érables', '0778945602'),
('GIRARD Louis', '17 Impasse des Fleurs', '0612345678'),
('BERTRAND Chloé', '8 Allée des Peupliers', '0698751234'),
('LAMBERT Lucas', '10 Rue de la Liberté', '0645128793'),
('ROUSSEAU Emma', '3 Chemin des Sources', '0712348956'),
('FONTAINE Nathan', '12 Place de la République', '0678953412'),
('MOREAU Sarah', '19 Rue du Soleil', '0632789456'),
('BLANC Thomas', '25 Avenue de la Paix', '0623456789');

INSERT INTO Fruits_Legumes_et_aromate (Libelle_FruitLegume) VALUES
('Pastèque'),
('Persil'),
('Piment d espelette'),
('Tomate'),
('Pomme de terre'),
('Courgette'),
('Potiron'),
('Potimaron'),
('Courge'),
('Betterave'),
('Poivron'),
('Epinard'),
('Salade d\'hiver'),
('Haricots verts');

INSERT INTO Parcelle (Parcelle.Nom_Parcelle, Parcelle.Surface, Parcelle.Plante_id) VALUES
('A1', 2.5 , 5),
('A2' , 3 , 6),
('A3' , 2 , 7),
('A4' , 4 , NULL),
('B1' , 1 , 2),
('B2' , 2 , 3),
('B3' , 3 , NULL),
('B4' , 3.4 , NULL),
('C1' , 5 , NULL),
('C2' , 3 , NULL),
('C3' , 3.6 , NULL),
('C4' , 2.1 , NULL),
('D1' , 7 , NULL),
('D2' , 3.9 , NULL),
('D3' , 4.5 , NULL),
('D4' , 3 , NULL);

INSERT INTO Actions (Libelle_action) VALUES
('Planter'),
('Récolter'),
('Vider'),
('Ajouter'),
('Signale'),
('Nettoyer'),
('Applique'),
('Pot cassé'),
('Tuteur cassé'),
('Maladie'),
('Infestation');

INSERT INTO Compost (Taille, Localisation) VALUES
(12,'B4'),
(10,'D4'),
(15, 'A2'),
(6, 'D1');

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

INSERT INTO Défaut(Libelle_Defaut , Id_Actions) VALUES
('Pot cassé' , 7),
('Tuteur cassé' , 8),
('Maladie' , 9),
('Infestation', 10);

INSERT INTO Traitement(Libelle_traitement, Id_Actions) VALUES
('Engrais' , 7),
('Désherbant' , 7),
('Arrosage' , 7),
('Rempotage' , 7),
('Pose de tuteurs', 7),
('Anti-fongique',7),
('Anti-vermine',7);

INSERT INTO Pousse (Id_FruitLégume, Id_mois_a_planter) VALUES
(1 , 3),
(2,5),
(3, 4),
(4 , 4),
(5,5),
(6, 5),
(7,4),
(8,4),
(9,3),
(10, 3),
(11,2),
(12,12),
(13,8),
(14,4);

INSERT INTO Attendre (Id_traitement, Id_traitement_1, temps_attente) VALUES
(1 , 1 , 'Un mois'),
(2 , 1 , '24 heures'),
(7,6,'Minimum une semaine'),
(3,3,'Pas 2x/J'),
(4,3, '48 heures'),
(2,3,'24h');

INSERT INTO Entretient (Id_Adherent, Date_Entretient, Id_Actions, Id_Compost, Quantite)VALUES
(1 , '2024_05_09' , 4 , 1 , 2.5),
(2 , '2024_05_18' , 6 , 2 , 0);

INSERT INTO Recolte (Id_Adherent, Id_Parcelle, Id_plante , Date_Recolte, Id_Actions, Quantite) VALUES
(3 , 2 , 1 ,'2024_05_07' , 8 , 0),
(2 , 3 , 3 , '2024_05_10' , 1 , 0),
(1 , 2 ,  4 , '2024_06_28' , 2 , 3),
(2 , 1 , 5 , '2024_03_20' , 2 , 1.3),
(3 , 2 , 1 , '2024_01_28' , 2 , 3);



-- REQUETES ----------------
-- REQUETE 1 : VOIR LES ACTIONS SUR LA PARCELLE 2
SELECT Adherent.NomPrenom , Actions.Libelle_action
FROM Adherent
JOIN Recolte on Adherent.Id_Adherent = Recolte.Id_Adherent
LEFT JOIN Actions on  Actions.Id_Actions = Recolte.Id_Actions
WHERE Recolte.Id_Parcelle = 2;

-- REQUETE 2 : VOIR LES PLANTES QUI ONT POUSSÉ SUR LA PARCELLE 2
select Fruits_Legumes_et_aromate.Libelle_FruitLegume
from Fruits_Legumes_et_aromate
right join Parcelle on Fruits_Legumes_et_aromate.Id_FruitLegume = Parcelle.Id_Parcelle
WHERE Parcelle.Id_Parcelle=2  -- "permet de choisir la parcelle"
group by Fruits_Legumes_et_aromate.Libelle_FruitLegume;

-- REQUETE 3 : VOIR LES TRAITEMENTS ET L'ACTION ASSOCIÉE
SELECT  Traitement.Libelle_traitement, Actions.Libelle_action
FROM Traitement
right JOIN Actions ON Traitement.Id_Actions = Actions.Id_Actions

-- REQUETE 4 : MODIFIER UNE PLANTE
where Actions.Libelle_action = 'Applique'
ORDER BY Traitement.Libelle_traitement, Actions.Libelle_action;
SELECT * FROM Fruits_Legumes_et_aromate;

UPDATE Fruits_Legumes_et_aromate
SET Libelle_FruitLegume = 'Pomme'
WHERE Libelle_FruitLegume LIKE 'Tomate';

SELECT * FROM Fruits_Legumes_et_aromate;

-- REQUETE 5 : SIGNALEMENT D'UN DÉFAUT & AFFICHAGE
INSERT INTO Recolte (Id_Adherent, Id_Parcelle, Date_Recolte, Id_Actions, Quantite) VALUE (3, 1 ,
                        '2024_07_20' , 7 , 0);

SELECT Parcelle.Id_Parcelle , Défaut.Libelle_Defaut , Recolte.Date_Recolte
FROM Parcelle
JOIN Recolte on Parcelle.Id_Parcelle = Recolte.Id_Parcelle
JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
JOIN Défaut on Actions.Id_Actions = Défaut.Id_Actions;


-- AFFICHAGE DES RECOLTES AVEC NOM ADHERENT, ID PARCELLE , NOM ACTION , DATE RECOLTE , QTITÉ RAMASSÉE
SELECT Adherent.NomPrenom as Nom, Recolte.Id_Parcelle as Parcelle , Recolte.Date_Recolte as Date ,
       Libelle_FruitLegume as Plante, Recolte.Quantite as Quantité
FROM Recolte
LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
RIGHT JOIN Fruits_Legumes_et_aromate on Recolte.Id_plante = Fruits_Legumes_et_aromate.Id_FruitLegume
RIGHT JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
WHERE Actions.Id_Actions = 2;

-- RECUPERATION DES DONNÉES POUR LES LD DU ADD
SELECT Adherent.NomPrenom FROM Adherent;
SELECT Parcelle.Id_Parcelle FROM Parcelle WHERE Plante_id IS NOT NULL;
SELECT Fruits_Legumes_et_aromate.Libelle_FruitLegume FROM Fruits_Legumes_et_aromate;