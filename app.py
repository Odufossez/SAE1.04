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

@app.route('/recolte/show' , methods=['GET'])
def show_recolte():
    mycursor = g.db.cursor()
    sql = '''  SELECT Adherent.Nom as Nom , Adherent.Prenom as Prénom , Recolte.Id_Parcelle as Parcelle , 
        Recolte.JJ_MM_AAAA as Date ,
        Libelle_FruitLegume as Plante, Recolte.Quantite as Quantité
        FROM Recolte
        LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
        RIGHT JOIN Fruits_Legumes_et_aromate on Id_Parcelle = Fruits_Legumes_et_aromate.Id_FruitLegume
        LEFT JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
        WHERE Actions.Id_Actions = 2; '''

    mycursor.execute(sql)
    recoltes = mycursor.fetchall()

    return render_template('recolte/show_recolte.html' , recolte = recoltes)

@app.route('/recolte/add' , methods=['GET'])
def add_recolte():
    mycursor = g.db.cursor()

    sql = '''  SELECT Adherent.Nom FROM Adherent; '''
    mycursor.execute(sql)
    Adherents = mycursor.fetchall()

    sql = '''  SELECT Parcelle.Id_Parcelle FROM Parcelle WHERE Plante_id = 0 OR Plante_id IS NULL; '''
    mycursor.execute(sql)
    Parcelles = mycursor.fetchall()

    sql = '''  SELECT Fruits_Legumes_et_aromate.Libelle_FruitLegume FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql)
    Fruits_Legumes_et_aromate = mycursor.fetchall()

    return render_template('recolte/add_recolte.html' , Adherent = Adherents , Parcelle = Parcelles , Fruits_Legumes_et_aromate = Fruits_Legumes_et_aromate)

@app.route('/recolte/add' , methods=['POST'])
def valid_add_recolte():
    mycursor = g.db.cursor()

    idAdherent = request.form.get('Id_Adherent', '')
    Id_Parcelle = request.form.get('Id_Parcelle', '')
    Date = request.form.get('JJ_MM_AAAA', '')
    Id_FruitLegume = request.form.get('Id_FruitLegume', '')
    Quantite = request.form.get('Quantite', '')

    tuple_insert = (Id_FruitLegume , Id_Parcelle)
    sql = '''  INSERT INTO Parcelle (Plante_id) VALUE (%s) WHERE Id_Parcelle = %s;'''
    mycursor.execute(sql, tuple_insert)

    tuple_insert = (idAdherent , Id_Parcelle , Date , Quantite)
    sql = ''' INSERT INTO Recolte (Id_Adherent , Id_Parcelle , Date , Id_Action , Quantite) VALUES (%s, %s, %s, 2 ,%s);'''
    mycursor.execute(sql, tuple_insert)

    message = (u'Récolte ajoutée : Adhérent : ' + idAdherent + ' --Parcelle : ' + Id_Parcelle +
               ' --Plante : ' + Id_FruitLegume + ' --Date : ' + Date + ' --Quantite : ' + Quantite)
    print(message)
    flash(message, 'alert-success')
    return redirect(url_for('show_recolte'))

@app.route('/recolte/edit' , methods=['GET'])
def edit_recolte():
    mycursor = g.db.cursor()

    idRecolte = request.args.get('Id_Recolte', '')
    sql = ''' SELECT Adherent.Nom as Nom , Adherent.Prenom as Prénom , Recolte.Id_Parcelle as Parcelle , 
        Recolte.JJ_MM_AAAA as Date ,
        Libelle_FruitLegume as Plante, Recolte.Quantite as Quantité
        FROM Recolte
        LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
        RIGHT JOIN Fruits_Legumes_et_aromate on Id_Parcelle = Fruits_Legumes_et_aromate.Id_FruitLegume
        LEFT JOIN Actions on Recolte.Id_Actions = Actions.Id_Actions
        WHERE Actions.Id_Actions = 2 AND Recolte.Id_Recolte = %s ; '''
    mycursor.execute(sql , (idRecolte,))




