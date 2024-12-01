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

    #Récupération de la ligne dans la DB
    sql = ''' SELECT Adherent.NomPrenom, Adherent.Id_Adherent, Recolte.Id_Parcelle,
        Recolte.Date_Recolte , Parcelle.Nom_Parcelle, Recolte.Id_plante,
        Fruits_Legumes_et_aromate.Libelle_FruitLegume, Recolte.Quantite
        FROM Recolte
        LEFT JOIN Adherent on Recolte.Id_Adherent = Adherent.Id_Adherent
        RIGHT JOIN Fruits_Legumes_et_aromate on Recolte.Id_plante = Fruits_Legumes_et_aromate.Id_FruitLegume
        JOIN Parcelle on Recolte.Id_Parcelle = Parcelle.Id_Parcelle
        WHERE Recolte.Id_Recolte = %s ;'''

    mycursor.execute(sql , (idRecolte,))
    recolte = mycursor.fetchone()

    # RECUPERATION DES LISTES DÉROULANTES
    sql = '''  SELECT Id_Adherent , Adherent.NomPrenom FROM Adherent; '''
    mycursor.execute(sql)
    adherents = mycursor.fetchall()

    sql = '''  SELECT Parcelle.Id_Parcelle , Parcelle.Nom_Parcelle FROM Parcelle; '''
    mycursor.execute(sql)
    parcelles = mycursor.fetchall()

    sql = '''  SELECT Id_FruitLegume , Libelle_FruitLegume FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql)
    fruits_legumes_et_aromate = mycursor.fetchall()

    return render_template('recolte/edit_recolte.html' , Recolte = recolte , Adherents = adherents ,
                           Parcelles = parcelles , Fruits_Legumes_et_aromate = fruits_legumes_et_aromate)

@app.route('/recolte/edit' , methods=['POST'])
def valid_edit_recolte():
    mycursor = get_db().cursor()

    Id_Recolte = request.args.get('Id_Recolte', '')

    idAdherent_form = request.form.get('Id_Adherent', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if idAdherent_form == ' ':
        idAdherent =  mycursor.execute("SELECT Id_Adherent FROM Recolte WHERE Id_Recolte = %s" , Id_Recolte)
    else:
        idAdherent = idAdherent_form

    Id_Parcelle_form = request.form.get('Id_Parcelle', '')
    #Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Id_Parcelle_form == ' ':
        Id_Parcelle = mycursor.execute("SELECT Id_Parcelle FROM Recolte WHERE Id_Recolte = %s" , Id_Recolte)
    else:
        Id_Parcelle = Id_Parcelle_form

    Date_form = request.form.get('Date_Recolte', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Date_form == ' ':
        Date = mycursor.execute("SELECT Date_Recolte FROM Recolte WHERE Id_Recolte = %s" , Id_Recolte)
    else:
        Date = Date_form

    Id_FruitLegume_form = request.form.get('Id_FruitLegume', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Id_FruitLegume_form == ' ':
        Id_FruitLegume = mycursor.execute("SELECT Id_plante FROM Recolte WHERE Id_Recolte = %s" , Id_Recolte)
    else:
        Id_FruitLegume = Id_FruitLegume_form

    Quantite_form = request.form.get('Quantite', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Quantite_form == ' ':
        Quantite = mycursor.execute("SELECT Quantite FROM Recolte WHERE Id_Recolte = %s" , Id_Recolte)
    else:
        Quantite = Quantite_form

    tuple_update = (idAdherent, Id_Parcelle, Date, Quantite, Id_FruitLegume, Id_Recolte)
    sql = ''' UPDATE Recolte SET Id_Adherent = %s , Id_Parcelle = %s , Date_Recolte = %s , Quantite = %s , 
        Id_plante = %s
        WHERE Id_Recolte = %s; '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()

    Recolte_complete = request.form.get('Recolte_complete', '')  # indicateur de si la parcelle est vide ou non
    #Vide la parcelle si besoin else ajuste la valeur des plantes dessus au cas où
    if (Recolte_complete == 'oui_recolte_complete'):
        mycursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        mycursor.execute("ALTER TABLE Parcelle DISABLE KEYS;", )

        tuple_update = (Id_Parcelle)
        sql = '''  UPDATE Parcelle SET Plante_id = NULL WHERE Id_Parcelle = %s; '''
        mycursor.execute(sql, tuple_update)
        get_db().commit()
        mycursor.execute("ALTER TABLE Parcelle ENABLE KEYS;", )
        mycursor.execute("SET FOREIGN_KEY_CHECKS=1;", )
    else:
        mycursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        mycursor.execute("ALTER TABLE Parcelle DISABLE KEYS;", )

        tuple_update = (Id_FruitLegume , Id_Parcelle)
        sql = '''  UPDATE Parcelle SET Plante_id = %s WHERE Id_Parcelle = %s; '''
        mycursor.execute(sql, tuple_update)
        get_db().commit()
        mycursor.execute("ALTER TABLE Parcelle ENABLE KEYS;", )
        mycursor.execute("SET FOREIGN_KEY_CHECKS=1;", )


    message = (u'Récolte modifiée :' + Id_Recolte + 'Adhérent : ' + idAdherent + ' --Parcelle : ' + Id_Parcelle +
               ' --Plante : ' + Id_FruitLegume + ' --Date : ' + Date + ' --Quantite : ' + Quantite)
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

    idParcelle = request.args.get('Id_Parcelle', '')
    plante_vide = mycursor.execute("SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s", idParcelle)
    plante_vide = str(plante_vide)

    #si la plante est vide, la récupération de la ligne n'est pas la même pour éviter des champs vides
    if plante_vide == '':
        #Récupération de la ligne dans la DB
        sql = ''' SELECT Parcelle.Id_Parcelle, Parcelle.Nom_Parcelle, Parcelle.Surface FROM Parcelle
        WHERE Parcelle.Id_Parcelle = %s ;'''
    else:
        # Récupération de la ligne dans la DB
        sql = ''' SELECT Parcelle.Id_Parcelle, Parcelle.Nom_Parcelle, Parcelle.Surface,
                Parcelle.Plante_id , Fruits_Legumes_et_aromate.Libelle_FruitLegume , Fruits_Legumes_et_aromate.Id_FruitLegume
                FROM Parcelle
                RIGHT JOIN Fruits_Legumes_et_aromate on Parcelle.Plante_id = Fruits_Legumes_et_aromate.Id_FruitLegume
                WHERE Parcelle.Id_Parcelle = %s ;'''

    mycursor.execute(sql , (idParcelle,))
    Parcelle = mycursor.fetchone()

    # RECUPERATION DE LA LISTE DÉROULANTE DES PLANTES
    sql = '''  SELECT * FROM Fruits_Legumes_et_aromate; '''
    mycursor.execute(sql,)
    Plantes = mycursor.fetchall()

    return render_template('parcelle/edit_parcelle.html' , Parcelle = Parcelle , Plantes = Plantes)


@app.route('/parcelle/edit' , methods=['POST'])
def valid_edit_parcelle():
    mycursor = get_db().cursor()

    Id_Parcelle = request.args.get('Id_Parcelle', '') #ne change jamais

    Nom_Parcelle_form = request.form.get('Nom_Parcelle', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Nom_Parcelle_form == ' ':
        Nom_Parcelle = mycursor.execute("SELECT Nom_Parcelle FROM Parcelle WHERE Id_Parcelle = %s;", Id_Parcelle)
    else:
        Nom_Parcelle = Nom_Parcelle_form

    Surface_form = request.form.get('Surface', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Surface_form == ' ':
        Surface = mycursor.execute("SELECT Surface FROM Parcelle WHERE Surface = %s;",Id_Parcelle)
    else:
        Surface = Surface_form

    Id_FruitLegume_form = request.form.get('Id_FruitLegume', '')
    # Si la valeur du champ n'a pas changé, récupérer celle précédente
    if Id_FruitLegume_form == ' ':
        Id_FruitLegume = mycursor.execute("SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s;", Id_Parcelle)
        Id_FruitLegume = str(Id_FruitLegume)
    elif Id_FruitLegume_form == 'vide':
        Id_FruitLegume = 'NULL'
    else:
        Id_FruitLegume = Id_FruitLegume_form

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
    plante_vide = mycursor.execute("SELECT Plante_id FROM Parcelle WHERE Id_Parcelle = %s;", Id_Parcelle)
    plante_vide = str(plante_vide)#conversion pour comparaison
    if (plante_vide == 'NULL'):
        flash(u'Une parcelle ne peut pas être supprimée: ' + Id_Parcelle , 'alerte-warning')
    else :
        id_delete = request.args.get('Id_Parcelle', '')
        tuple_delete = (id_delete,)
        sql = '''DELETE FROM Parcelle WHERE Id_Parcelle = %s;'''
        mycursor.execute(sql, tuple_delete)
        get_db().commit()
        flash(u'Une parcelle a été supprimée : ' + id_delete, 'alerte-warning')
        
    return redirect('/parcelle/show')


