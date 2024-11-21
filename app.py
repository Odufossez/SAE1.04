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
    sql = '''  '''