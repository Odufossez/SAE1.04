#! /usr/bin/python
import sqlite3
from tempfile import template
from flask import Flask, request , render_template, redirect, url_for, abort, flash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'

from flask import session , g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host='localhost', #mettre "serveurmysql"
            user="root", #"odufosse"
            password="mdproot", #"mdp"
            database="oscar_data", #"BDD_odufosse_tp"
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_accueil():
    return render_template('layout.html')

#----------- RECOLTE ----------------------------------

@app.route('/recolte/show' , methods=['GET'])
def show_recolte():
    mycursor = get_db().cursor()

    sql = ''' SELECT Recolte.Id_Recolte , Adherent.NomPrenom as Nom, Parcelle.Nom_Parcelle as Parcelle , 
    Recolte.Date_Recolte , Libelle_FruitLegume as Plante, Recolte.Quantite as Quantite FROM Recolte
    LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
    RIGHT JOIN Fruits_Legumes_et_aromate on Recolte.Id_plante = Fruits_Legumes_et_aromate.Id_FruitLegume
    RIGHT JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
    JOIN Parcelle on Recolte.Id_Parcelle = Parcelle.Id_Parcelle
    WHERE Actions.Id_Actions = 2; '''

    mycursor.execute(sql)
    recoltes = mycursor.fetchall()

    return render_template('recolte/show_recolte.html' , recoltes = recoltes)

@app.route('/recolte/add' , methods=['GET'])
def add_recolte():
    mycursor = get_db().cursor()

    # Liste des adhérents
    sql = '''  SELECT Adherent.Id_Adherent , Adherent.NomPrenom FROM Adherent; '''
    mycursor.execute(sql)
    Adherents = mycursor.fetchall()

    # Liste des parcelles qui ont des plantes actuellement
    sql = '''  SELECT Parcelle.Id_Parcelle, Parcelle.Nom_Parcelle FROM Parcelle WHERE Plante_id IS NOT NULL; '''
    mycursor.execute(sql)
    Parcelles = mycursor.fetchall()

    return render_template('recolte/add_recolte.html' , Adherent = Adherents , Parcelle = Parcelles)

@app.route('/recolte/add' , methods=['POST'])
def valid_add_recolte():
    mycursor = get_db().cursor()

    idAdherent = request.form.get('Id_Adherent', '')
    Id_Parcelle = request.form.get('Id_Parcelle', '')
    Date = request.form.get('Date_Recolte', '')
    Quantite = request.form.get('Quantite', '')
    Recolte_complete = request.form.get('Recolte_complete', '') #indicateur de si la parcelle est vide ou non

    # Récupération de la plante sur la parcelle sélectionnée
    tuple_plante = (Id_Parcelle)
    sql = ''' SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s '''
    id_plante = mycursor.execute(sql, tuple_plante)

    # si la récolte vide la parcelle alors on met à jour la table parcelle
    if (Recolte_complete == "oui_recolte_complete"):

        mycursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        mycursor.execute("ALTER TABLE Parcelle DISABLE KEYS;",)

        tuple_update = (Id_Parcelle)
        sql = '''  UPDATE Parcelle SET Plante_id = NULL WHERE Id_Parcelle = %s; '''
        mycursor.execute(sql, tuple_update)
        get_db().commit()
        mycursor.execute("ALTER TABLE Parcelle ENABLE KEYS;",)
        mycursor.execute("SET FOREIGN_KEY_CHECKS=1;",)

    #Conversion en string
    id_plante = str(id_plante)

    #Insertion dans la table récolte
    tuple_insert = (idAdherent , Id_Parcelle , id_plante , Date , Quantite)
    sql = ''' INSERT INTO Recolte (Id_Adherent, Id_Parcelle, Id_plante , Date_Recolte , Id_Actions , Quantite) VALUES 
    (%s , %s , %s , %s , 2 , %s);'''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    message = (u'Récolte ajoutée : Adhérent : ' + idAdherent + ' --Parcelle : ' + Id_Parcelle +
               ' --Plante : ' + id_plante + ' --Date : ' + Date + ' --Quantite : ' + Quantite)
    print(message)
    flash(message, 'alert-success')
    return redirect(url_for('show_recolte'))

@app.route('/recolte/edit' , methods=['GET'])
def edit_recolte():
    mycursor = get_db().cursor()

    Id_Recolte = request.args.get('Id_Recolte', '')

    #Récupération de la ligne dans la DB
    sql = ''' SELECT Adherent.NomPrenom, Adherent.Id_Adherent, Recolte.Id_Parcelle,
        Recolte.Date_Recolte , Parcelle.Nom_Parcelle, Recolte.Id_plante,
        Fruits_Legumes_et_aromate.Libelle_FruitLegume, Recolte.Quantite , Recolte.Id_Recolte
        FROM Recolte
        LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
        RIGHT JOIN Fruits_Legumes_et_aromate on Recolte.Id_plante = Fruits_Legumes_et_aromate.Id_FruitLegume
        JOIN Parcelle on Recolte.Id_Parcelle = Parcelle.Id_Parcelle
        WHERE Recolte.Id_Recolte = %s ;'''

    mycursor.execute(sql , (Id_Recolte,))
    Recolte = mycursor.fetchone()

    # RECUPERATION DES LISTES DÉROULANTES
    sql = '''  SELECT Id_Adherent , Adherent.NomPrenom FROM Adherent; '''
    mycursor.execute(sql)
    adherents = mycursor.fetchall()

    sql = '''  SELECT Parcelle.Id_Parcelle , Parcelle.Nom_Parcelle FROM Parcelle WHERE Plante_id IS NOT NULL; '''
    mycursor.execute(sql)
    parcelles = mycursor.fetchall()

    sql = '''  SELECT Id_FruitLegume , Libelle_FruitLegume FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql)
    fruits_legumes_et_aromate = mycursor.fetchall()

    return render_template('recolte/edit_recolte.html' , Recolte = Recolte , Adherents = adherents ,
                           Parcelles = parcelles , Fruits_Legumes_et_aromate = fruits_legumes_et_aromate)

@app.route('/recolte/edit' , methods=['POST'])
def valid_edit_recolte():
    mycursor = get_db().cursor()

    # Attributs qui ne sont pas modifiables
    Id_Recolte = request.form.get('Id_Recolte', '')
    if not Id_Recolte:
        flash("Id_Recolte manquant", "alert-danger")
        return redirect(url_for('show_recolte'))

    # Attributs modifiables
    Id_FruitLegume = request.form.get('Id_FruitLegume', '')
    idAdherent = request.form.get('Id_Adherent', '')
    Id_Parcelle = request.form.get('Id_Parcelle', '')
    Date = request.form.get('Date_Recolte', '')
    Quantite = request.form.get('Quantite', '')
    Recolte_complete = request.form.get('Recolte_complete', '')

    # Récupération de l'ancienne valeur de Id_Parcelle
    Id_Parcelle_DB=mycursor.execute("SELECT Id_Parcelle FROM Recolte WHERE Id_Recolte = %s;", (Id_Recolte,))

    # Vérifier si Id_Parcelle a changé
    if Id_Parcelle_DB != Id_Parcelle:
        Id_FruitLegume=mycursor.execute("SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s;", (Id_Parcelle,))

    # Mettre à jour la parcelle selon si la récolte est complète ou non
    if Recolte_complete == 'oui_recolte_complete':
        mycursor.execute("UPDATE Parcelle SET Plante_id = NULL WHERE Id_Parcelle = %s;", (Id_Parcelle,))
    else:
        mycursor.execute("UPDATE Parcelle SET Plante_id = %s WHERE Id_Parcelle = %s;", (Id_FruitLegume, Id_Parcelle))

    get_db().commit()  # Validation des modifications sur la parcelle

    # Mettre à jour la récolte
    tuple_update = (idAdherent, Id_Parcelle, Date, Quantite, Id_FruitLegume, Id_Recolte)
    sql = '''UPDATE Recolte
        SET Id_Adherent = %s, Id_Parcelle = %s, Date_Recolte = %s, Quantite = %s, Id_plante = %s
        WHERE Id_Recolte = %s;'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()  # Validation des modifications sur la récolte

    # Message de confirmation
    message = (f"Récolte modifiée : {Id_Recolte} - Adhérent : {idAdherent} - Parcelle : {Id_Parcelle} "
               f"- Plante : {Id_FruitLegume} - Date : {Date} - Quantité : {Quantite}")
    print(message)
    flash(message, 'alert-success')

    return redirect(url_for('show_recolte'))


@app.route('/recolte/delete' , methods=['GET'])
def delete_recolte():
    mycursor = get_db().cursor()

    id_delete = request.args.get('Id_Recolte', '')
    tuple_delete = (id_delete,)
    sql = '''DELETE FROM Recolte WHERE Id_Recolte = %s;'''

    mycursor.execute(sql , tuple_delete)
    get_db().commit()

    flash(u'Une récolte a été supprimée : ' + id_delete , 'alerte-warning')
    return redirect('/recolte/show')

@app.route('/recolte/filtre' , methods=['GET'])
def filtre_recolte():
    mycursor = get_db().cursor()

    sql = ''' SELECT Recolte.Id_Recolte , Adherent.NomPrenom as Nom, Parcelle.Nom_Parcelle as Parcelle , 
        Recolte.Date_Recolte , Libelle_FruitLegume as Plante, Recolte.Quantite as Quantite FROM Recolte
        LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
        RIGHT JOIN Fruits_Legumes_et_aromate on Recolte.Id_plante = Fruits_Legumes_et_aromate.Id_FruitLegume
        RIGHT JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
        JOIN Parcelle on Recolte.Id_Parcelle = Parcelle.Id_Parcelle
        WHERE Actions.Id_Actions = 2; '''
    mycursor.execute(sql)
    Recoltes = mycursor.fetchall()

    #CALCUL POIDS TOTAL
    sql = ''' SELECT sum(Recolte.Quantite) AS poids_recolte FROM Recolte'''
    mycursor.execute(sql)
    poids_recolte = mycursor.fetchone()

    #CALCUL POIDS DE PASTÈQUE
    sql = ''' SELECT sum(Recolte.Quantite) AS poids_pdt FROM Recolte WHERE Id_plante = 1;'''
    mycursor.execute(sql)
    poids_pdt = mycursor.fetchone()


    return render_template('recolte/filtre_recolte.html' , Recoltes = Recoltes ,
                           poids_recolte = poids_recolte , poids_pdt = poids_pdt)


#----------Parcelle----------------------------------------------

@app.route('/parcelle/show' , methods=['GET'])
def show_parcelle():
    mycursor = get_db().cursor()

    sql = ''' SELECT Parcelle.Id_Parcelle , Nom_Parcelle , Fruits_Legumes_et_aromate.Libelle_FruitLegume as Plante, 
    Surface
    FROM Parcelle
    JOIN Fruits_Legumes_et_aromate on Parcelle.Plante_id = Fruits_Legumes_et_aromate.Id_FruitLegume;'''

    mycursor.execute(sql)
    parcelles = mycursor.fetchall()

    # RÉCUPÉRATION DES PARCELLES INNOCUPÉES
    sql = ''' SELECT Id_Parcelle ,  Nom_Parcelle , Surface FROM Parcelle WHERE Plante_id IS NULL OR Plante_id = ' '; '''
    mycursor.execute(sql)
    parcelles_vide = mycursor.fetchall()

    return render_template('parcelle/show_parcelle.html' , parcelles = parcelles ,
                           parcelles_vide = parcelles_vide)

@app.route('/parcelle/add' , methods=['GET'])
def add_parcelle():
    mycursor = get_db().cursor()

    # Liste des plantes
    sql = '''  SELECT * FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql)
    Plantes = mycursor.fetchall()

    return render_template('parcelle/add_parcelle.html' , Plantes = Plantes)

@app.route('/parcelle/add' , methods=['POST'])
def valid_add_parcelle():
    mycursor = get_db().cursor()

    Nom_Parcelle = request.form.get('Nom_Parcelle', '')
    Surface = request.form.get('Surface', '')
    Plante_id = request.form.get('Plante_id', '')

    if (Plante_id != ''):
        Plante_id = int(Plante_id) #Pour le sql
        # Insertion dans la table parcelle
        tuple_insert = (Nom_Parcelle, Surface, Plante_id)
        sql = ''' INSERT INTO Parcelle (Nom_Parcelle, Surface , Plante_id) VALUES (%s , %s , %s);'''
        mycursor.execute(sql, tuple_insert)
        get_db().commit()
        Plante_id = str(Plante_id) #Pour le message
    else:
        # Insertion dans la table parcelle
        tuple_insert = (Nom_Parcelle, Surface)
        sql = ''' INSERT INTO Parcelle (Nom_Parcelle, Surface) VALUES (%s , %s);'''
        mycursor.execute(sql, tuple_insert)
        get_db().commit()

    message = (u' Nouvelle Parcelle : Nom parcelle : ' + Nom_Parcelle + ' --Surface : ' + Surface +
               ' --Plante_id : ' + Plante_id)
    print(message)
    flash(message, 'alert-success')
    return redirect(url_for('show_parcelle'))

@app.route('/parcelle/edit' , methods=['GET'])
def edit_parcelle():
    mycursor = get_db().cursor()

    Id_Parcelle = request.args.get('Id_Parcelle', '')

    # RÉCUPÉRATION DE LA VALEUR DE LA PLANTE
    mycursor.execute("SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s;", (Id_Parcelle,))
    plante_vide = mycursor.fetchone()
    plante_vide = str(plante_vide)
    plante_vide = plante_vide.find("None")

    if plante_vide != -1:
        sql = '''SELECT Id_Parcelle , Nom_Parcelle , Surface FROM Parcelle WHERE Id_Parcelle = %s'''
    else:
        sql = ''' SELECT * FROM Parcelle
        JOIN Fruits_Legumes_et_aromate on Parcelle.Plante_id = Fruits_Legumes_et_aromate.Id_FruitLegume
        WHERE Id_Parcelle = %s'''

    mycursor.execute(sql , (Id_Parcelle,))
    Parcelle = mycursor.fetchone()

    # RECUPERATION DE LA LISTE DÉROULANTE DES PLANTES
    sql = '''  SELECT * FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql,)
    Plantes = mycursor.fetchall()

    return render_template('parcelle/edit_parcelle.html' , Parcelle = Parcelle , Plantes = Plantes)


@app.route('/parcelle/edit' , methods=['POST'])
def valid_edit_parcelle():
    mycursor = get_db().cursor()

    Id_Parcelle = request.form.get('Id_Parcelle', '') #ne change jamais
    if not Id_Parcelle:
        flash("Id_Parcelle manquant", "alert-danger")
        return redirect(url_for('show_parcelle'))

    Nom_Parcelle= request.form.get('Nom_Parcelle', '')
    Surface = request.form.get('Surface', '')
    Id_FruitLegume= request.form.get('Id_FruitLegume', '')

    # Si la valeur du champ est "vide" mettre NULL
    if Id_FruitLegume == 'vide':
        Id_FruitLegume = 'NULL'

    #mise à jour de la table PARCELLE
    tuple_update = (Nom_Parcelle,Surface,Id_FruitLegume,Id_Parcelle)
    sql = ''' UPDATE Parcelle SET Nom_Parcelle = %s , Surface = %s , Plante_id = %s WHERE Id_Parcelle = %s;'''
    mycursor.execute(sql,tuple_update)
    get_db().commit()

    message = (u'Parcelle modifiée id : ' + Id_Parcelle +
               ' --Nom : ' + Nom_Parcelle + ' --surface : ' + Surface + ' --id_plante : ' + Id_FruitLegume)
    print(message)
    flash(message, 'alert-success')
    return redirect(url_for('show_parcelle'))


@app.route('/parcelle/delete' , methods=['GET'])
def delete_parcelle():
    mycursor = get_db().cursor()
    
    Id_Parcelle = request.args.get('Id_Parcelle', '')

    # RÉCUPÉRATION DE LA VALEUR DE LA PLANTE
    mycursor.execute("SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s;", (Id_Parcelle,))
    plante_vide = mycursor.fetchone()
    plante_vide = str(plante_vide)
    plante_vide = plante_vide.find("None")

    if plante_vide == -1: #si la plante est vide
        flash(u'Une parcelle ne peut pas être supprimée, des plantes sont actuellement plantées dessus: '
              + Id_Parcelle, 'alerte-warning')
    else:
        id_delete = request.args.get('Id_Parcelle', '')
        tuple_delete = (id_delete,)
        sql = '''DELETE FROM Parcelle WHERE Id_Parcelle = %s;'''
        mycursor.execute(sql, tuple_delete)
        get_db().commit()
        flash(u'Une parcelle a été supprimée : ' + id_delete, 'alerte-warning')

    return redirect('/parcelle/show')


