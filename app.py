from flask import *
from flask import session
from flask import Flask, Markup, render_template
import sqlite3
import hashlib
from flask_session import Session
from os import *

app = Flask(__name__, static_folder='static')
SESSION_TYPE = "filesystem"
PERMANENT_SESSION_LIFETIME = 1800

app.config.update(SECRET_KEY=urandom(24))

app.config.from_object(__name__)
Session(app)

if __name__ == "__main__":
    with app.test_request_context("/"):
        session["key"] = "value"


DATABASE = 'project.db'


from blueprints.borderBP import borderBP
app.register_blueprint(borderBP)

def get_db():

    db = getattr(g, DATABASE, None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, DATABASE, None)
    if db is not None:
        db.close()

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/bar')
def bar():
    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=bar_labels, values=bar_values)

@app.route('/line')
def line():
    line_labels=labels
    line_values=values
    return render_template('line_chart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=line_labels, values=line_values)

@app.route('/pie')
def pie():
    pie_labels = labels
    pie_values = values
    return render_template('pie_chart.html', title='Bitcoin Monthly Price in USD', max=17000, set=zip(values, labels, colors))




@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST' and request.form.get('username') and request.form.get('password'):
        r = get_db().cursor()
        nom = request.form.get('username')
        mdp = bytes(request.form.get('password'), 'utf-8')
        mass = hashlib.sha256(mdp).hexdigest()
        r.execute("SELECT mdp FROM utilisateurs WHERE nom=?", (nom,))
        tuple = r.fetchall()
        if tuple==[]:
            print("pas d'utilisateur correspondant")
        elif nom=='milo' and tuple[0][0]==mass:
            return render_template("milo.html")
        elif tuple[0][0] == mass:
            r2 = get_db().cursor()
            r2.execute("SELECT id FROM utilisateurs WHERE nom=?",(nom,))
            tuple = r2.fetchall()[0][0]
            session["id_utilisateur"] = tuple
            return render_template("sandbox.html", id=tuple)
        else:
            return render_template('login.html',message="Incorrect")
    return render_template('login.html', message="")

@app.route('/sandbox', methods=['GET', 'POST'])
def sandbox():
    bar_labels=["Cosimo","Thomas","Kieran","Arthur"]
    bar_values=([get_db().cursor().execute("SELECT COUNT(*) FROM taches WHERE id={}".format(i)).fetchall()[0][0] for i in range(0,4)])
    bar_values_complete=([get_db().cursor().execute("SELECT COUNT(*) FROM taches WHERE id={} AND BOOL_DONE=1".format(i)).fetchall()[0][0] for i in range(0,4)])
    nom=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id={}".format(session["id_utilisateur"])).fetchall()
    liste_taches=get_db().cursor().execute("SELECT * FROM taches WHERE id={}".format(session["id_utilisateur"])).fetchall()
    liste_utilisateurs=get_db().cursor().execute("SELECT nom FROM utilisateurs".format(session["id_utilisateur"])).fetchall()
    if request.method == 'POST' and request.form.get('nom_tache') and request.form.get('menu_choix_utilisateur_tache'):
        max_id=get_db().cursor().execute("SELECT MAX(id_tache) FROM taches").fetchall()
        if max_id[0][0]==None:
            new_id=0
        else:
            new_id=max_id[0][0]+1
        conn = get_db()
        if request.form.get('menu_choix_utilisateur_tache')=="Cosimo":
            conn.cursor().execute('INSERT INTO taches VALUES(?,?,?,?,3)', (0,request.form.get('nom_tache'),0,new_id))
        elif request.form.get('menu_choix_utilisateur_tache')=="Thomas":
            conn.cursor().execute('INSERT INTO taches VALUES(?,?,?,?,3)', (0,request.form.get('nom_tache'),1,new_id))
        elif request.form.get('menu_choix_utilisateur_tache')=="Olivia":
            conn.cursor().execute('INSERT INTO taches VALUES(?,?,?,?,3)', (0,request.form.get('nom_tache'),2,new_id))
        conn.commit()
        conn.close()
        liste_taches=get_db().cursor().execute("SELECT * FROM taches WHERE id={}".format(session["id_utilisateur"])).fetchall()
        return(render_template("sandbox.html", nom=nom[0][0], taches=liste_taches, id=session["id_utilisateur"], utilisateurs=liste_utilisateurs, max=max(bar_values), labels=bar_labels, values=bar_values, values_complete=bar_values_complete))
    elif request.method == 'POST' and request.form.get("check_submit"):
        for element in request.form.keys():
            if element[:4]=="supp":
                conn = get_db()
                conn.cursor().execute('DELETE FROM taches WHERE id_tache=(?)', (element[4:],))
                conn.commit()
                conn.close()

        nb=get_db().cursor().execute("SELECT MAX(id_tache) FROM taches").fetchall()
        for i in range(nb[0][0]):
            if str("done_"+str(i)) in request.form.getlist('task_check'):
                conn = get_db()
                conn.cursor().execute('UPDATE taches SET BOOL_DONE=1 WHERE id_tache=(?)', (i,))
                conn.commit()
                conn.close()
            else:
                conn = get_db()
                conn.cursor().execute('UPDATE taches SET BOOL_DONE=0 WHERE id_tache=(?)', (i,))
                conn.commit()
                conn.close()

        liste_taches=get_db().cursor().execute("SELECT * FROM taches WHERE id={}".format(session["id_utilisateur"])).fetchall()
        return(render_template("sandbox.html", nom=nom[0][0], taches=liste_taches, id=session["id_utilisateur"], utilisateurs=liste_utilisateurs, max=max(bar_values), labels=bar_labels, values=bar_values, values_complete=bar_values_complete))
    return(render_template("sandbox.html", nom=nom[0][0], taches=liste_taches, id=session["id_utilisateur"], utilisateurs=liste_utilisateurs, max=max(bar_values), labels=bar_labels, values=bar_values, values_complete=bar_values_complete))


@app.route('/overview', methods=['GET', 'POST'])
def overview():
    nom=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id={}".format(session["id_utilisateur"])).fetchall()
    total_am=get_db().cursor().execute("SELECT COUNT(*) FROM taches").fetchall()[0][0]
    not_done_am=get_db().cursor().execute("SELECT COUNT(*) FROM taches WHERE BOOL_DONE=0").fetchall()[0][0]
    done_am=get_db().cursor().execute("SELECT COUNT(*) FROM taches WHERE BOOL_DONE=1").fetchall()[0][0]
    liste_taches=get_db().cursor().execute("SELECT * FROM taches").fetchall()
    lst=[]
    lstemp=get_db().cursor().execute("SELECT id FROM taches").fetchall()
    for e in lstemp:
        tmp=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id=(?)",(e[0],)).fetchall()
        if tmp==[]:
            lst.append("")
        else:
            lst.append(tmp[0][0])
    nb=len(liste_taches)
    return(render_template("overview.html", nom=nom[0][0], taches=liste_taches, id=session["id_utilisateur"], utilisateurs=lst, n=nb, nb_total = total_am, nb_not_done=not_done_am, nb_done = done_am))

@app.route('/gantt', methods=['GET', 'POST'])
def gantt():
    nom=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id={}".format(session["id_utilisateur"])).fetchall()
    liste_taches=get_db().cursor().execute("SELECT * FROM taches").fetchall()
    lst=[]
    lstemp=get_db().cursor().execute("SELECT id FROM taches").fetchall()
    for e in lstemp:
        tmp=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id=(?)",(e[0],)).fetchall()
        lst.append(tmp[0][0])
    nb=len(liste_taches)
    return(render_template("gantt.html", nom=nom[0][0], taches=liste_taches, id=session["id_utilisateur"], utilisateurs=lst, n=nb))

"""@app.route("/vuetache/<int:tache_id>", methods=['GET', 'POST'])
def rendu_tache(tache_id):
    if request.method=='POST':
        if request.form.get("nom_tache"):
            conn=get_db()
            conn.cursor().execute('UPDATE taches SET nom=(?) WHERE id_tache=(?)', (request.form.get("nom_tache"), tache_id,))
            conn.commit()
            conn.close()
        if request.form.get("choix_prio"):
            conn=get_db()
            conn.cursor().execute('UPDATE taches SET priorite=(?) WHERE id_tache=(?)', (request.form.get("choix_prio")[5:][0], tache_id,))
            conn.commit()
            conn.close()
        if request.form.get('menu_choix_utilisateur_tache'):
            conn = get_db()
            if request.form.get('menu_choix_utilisateur_tache')=="Cosimo":
                conn.cursor().execute('UPDATE taches SET id=0 WHERE id_tache=(?)', (tache_id,))
            elif request.form.get('menu_choix_utilisateur_tache')=="Thomas":
                conn.cursor().execute('UPDATE taches SET id=1 WHERE id_tache=(?)', (tache_id,))
            elif request.form.get('menu_choix_utilisateur_tache')=="Kieran":
                conn.cursor().execute('UPDATE taches SET id=2 WHERE id_tache=(?)', (tache_id,))
            elif request.form.get('menu_choix_utilisateur_tache')=="Arthur":
                conn.cursor().execute('UPDATE taches SET id=3 WHERE id_tache=(?)', (tache_id,))
            conn.commit()
            conn.close()
    lst_taches=get_db().cursor().execute("SELECT * FROM taches WHERE id_tache=(?)",(tache_id,)).fetchall()
    lst_actions=get_db().cursor().execute("SELECT * FROM actions WHERE id_tache=(?)",(tache_id,)).fetchall()
    if lst_taches==[]:
        user=1
    else:
        user=lst_taches[0][2]
    utilisateur=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id=(?)",(user,)).fetchall()
    if utilisateur==[]:
        utilisateur=""
    else:
        utilisateur=utilisateur[0][0]
    liste_utilisateurs=get_db().cursor().execute("SELECT nom FROM utilisateurs").fetchall()
    nb=len(get_db().cursor().execute("SELECT * FROM actions WHERE id_tache=(?)", (tache_id,)).fetchall())
    liste_actions=get_db().cursor().execute("SELECT * FROM actions WHERE id_tache=(?)", (tache_id,)).fetchall()
    if lst_actions==[]:
        lst_actions=[0 for i in range(7)]
    messages_liste=get_db().cursor().execute("SELECT * FROM messages WHERE tache_id=(?)",(tache_id,)).fetchall()
    if messages_liste==None:
        messages_liste=[]
    n=len(messages_liste)
    sender_liste=[]
    for i in range(n):
        sender_liste.append(get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id=(?)",(messages_liste[i][3],)).fetchall()[0][0])
    return render_template("vue_tache.html", infos_taches=lst_taches, infos_actions=lst_actions, nom_utilisateur=utilisateur, utilisateurs=liste_utilisateurs, n=nb, actions=liste_actions, id=tache_id, messages=messages_liste, len_messages=int(n), individus=sender_liste)"""

@app.route('/reunions')
def reunions():
    liste_taches=get_db().cursor().execute("SELECT * FROM taches").fetchall()
    tout=get_db().cursor().execute("SELECT * FROM reunions;").fetchall()
    id=tout[0][3]
    nom=get_db().cursor().execute("SELECT nom FROM utilisateurs WHERE id=(?)",(id,)).fetchall()[0][0]
    return render_template("reunions.html",taches=liste_taches, utilisateurs=[], infos=tout, secretaire = nom)

@app.route('/reunions/editeur/<int:id_reunion>')
def editeur(id_reunion):
    return render_template("editeur_reunion.html")

@app.route('/creer_tache')
def creer_tache():
    nb=get_db().cursor().execute("SELECT MAX(id_tache) FROM taches").fetchall()[0][0]
    if nb==None:
        nb=0
    else:
        nb+=1
    conn = get_db()
    conn.cursor().execute('INSERT INTO taches VALUES(0, "Nouvelle tâche", Null, (?), 0, Null, Null)',(nb,))
    conn.commit()
    conn.close()
    return redirect('/overview')

@app.route('/changer_statut_tache/<int:tache_id>', methods=['GET','POST'])
def valider_tache(tache_id):
    conn=get_db()
    new_bool_done=1-get_db().cursor().execute("SELECT BOOL_DONE FROM taches WHERE id_tache=(?)",(tache_id,)).fetchall()[0][0]
    conn.cursor().execute('UPDATE taches SET BOOL_DONE=(?) WHERE id_tache=(?)',(new_bool_done,tache_id,))
    conn.commit()
    conn.close()
    return redirect('/vuetache/'+str(tache_id))

@app.route('/supprimer_tache/<int:tache_id>', methods=['GET','POST'])
def supprimer_tache(tache_id):
    conn=get_db()
    conn.cursor().execute('DELETE FROM taches WHERE id_tache=(?)',(tache_id,))
    conn.commit()
    conn.close()
    return redirect('/overview')

@app.route('/envoyer_message/<int:tache_id>', methods=['GET', 'POST'])
def envoyer(tache_id):
    if request.method=='POST':
        max_id=get_db().cursor().execute("SELECT MAX(id) FROM messages WHERE tache_id=(?)",(tache_id,)).fetchall()[0][0]
        max_global_id=get_db().cursor().execute("SELECT MAX(global_id) FROM messages WHERE tache_id=(?)",(tache_id,)).fetchall()[0][0]
        if max_id == None:
            max_id = 0
        if max_global_id == None:
            max_global_id = 0
        conn=get_db()
        conn.cursor().execute('INSERT INTO messages VALUES(?,?,?,?,?)',(int(max_id)+1, tache_id, int(max_global_id)+1, session["id_utilisateur"], request.form.get("message")))
        conn.commit()
        conn.close()
    return redirect('/vuetache/'+str(tache_id))

@app.route('/vuetache/creer_action/<int:tache_id>', methods=['GET','POST'])
def creer_action(tache_id):
    max_id=get_db().cursor().execute("SELECT MAX(id) FROM Actions").fetchall()[0][0]
    conn=get_db()
    conn.cursor().execute('INSERT INTO actions VALUES((?), Null, 2, "Nouvelle action", Null, Null, 0, (?))',(max_id + 1, tache_id,))
    conn.commit()
    conn.close()
    return redirect('/vuetache/'+str(tache_id))