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
            host='localhost', #mettre "serveurmsyql"
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

    #Récupération de la plante sur la parcelle sélectionnée
    tuple_plante = (Id_Parcelle)
    sql = ''' SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s '''
    id_plante = mycursor.execute(sql, tuple_plante)

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

    idRecolte = request.args.get('Id_Recolte', '')
    sql = ''' SELECT Adherent.NomPrenom as Nom , Recolte.Id_Parcelle as Parcelle , 
        Recolte.Date_Recolte as Date ,
        Libelle_FruitLegume as Plante, Recolte.Quantite as Quantité
        FROM Recolte
        LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
        RIGHT JOIN Fruits_Legumes_et_aromate on Id_Parcelle = Fruits_Legumes_et_aromate.Id_FruitLegume
        LEFT JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
        WHERE Actions.Id_Actions = 2 AND Recolte.Id_Recolte = %s ; '''

    mycursor.execute(sql , (idRecolte,))
    Recolte = mycursor.fetchone()

    sql = '''  SELECT Adherent.NomPrenom FROM Adherent; '''
    mycursor.execute(sql)
    Adherents = mycursor.fetchall()

    sql = '''  SELECT Parcelle.Id_Parcelle FROM Parcelle WHERE Plante_id IS NOT NULL; '''
    mycursor.execute(sql)
    Parcelles = mycursor.fetchall()

    sql = '''  SELECT Fruits_Legumes_et_aromate.Libelle_FruitLegume FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql)
    Fruits_Legumes_et_aromate = mycursor.fetchall()

    return render_template('recolte/edit_recolte.html' , Recolte = Recolte , Adherents = Adherents ,
                           Parcelles = Parcelles , Fruits_Legumes_et_aromate = Fruits_Legumes_et_aromate)

@app.route('/recolte/edit' , methods=['POST'])
def valid_edit_recolte():
    mycursor = get_db().cursor()

    idAdherent = request.form.get('Id_Adherent', '')
    Id_Parcelle = request.form.get('Id_Parcelle', '')
    Date = request.form.get('JJ_MM_AAAA', '')
    Id_FruitLegume = request.form.get('Id_FruitLegume', '')
    Quantite = request.form.get('Quantite', '')

    tuple_insert = (Id_FruitLegume, Id_Parcelle)
    sql = '''  INSERT INTO Parcelle (Plante_id) VALUE (%s) WHERE Id_Parcelle = %s;'''
    mycursor.execute(sql, tuple_insert)

    tuple_insert = (idAdherent, Id_Parcelle, Date, Quantite)
    sql = ''' INSERT INTO Recolte (Id_Adherent , Id_Parcelle , Date , Id_Action , Quantite) VALUES (%s, %s, %s, 2 ,%s);'''
    mycursor.execute(sql, tuple_insert)

    message = (u'Récolte modifiée : Adhérent : ' + idAdherent + ' --Parcelle : ' + Id_Parcelle +
               ' --Plante : ' + Id_FruitLegume + ' --Date : ' + Date + ' --Quantite : ' + Quantite)
    print(message)
    flash(message, 'alert-success')
    return redirect(url_for('show_recolte'))

@app.route('/recolte/delete' , methods=['GET'])
def delete_recolte():
    mycursor = get_db().cursor()

    id_delete = request.args.get('Id_Recolte', '')
    tuple_delete = (id_delete,)
    sql = ''' DELETE FROM Recolte WHERE Id_Recolte = %s;'''

    mycursor.execute(sql , tuple_delete)
    get_db().commit()

    flash(u'Une récolte a été supprimée : ' + id_delete , 'alerte-warning')
    return redirect('/recolte/show')

#--------------------------------------------------------