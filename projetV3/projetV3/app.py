from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import pandas as pd
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'  # Nécessaire pour les sessions

#initialisation de la base de données des utilisateurs dans la base de données ma_base.db
def init_user_db():
    conn = sqlite3.connect("ma_base.db")
    cur = conn.cursor()
    
    # Création de la table utilisateurs si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mail TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            notes TEXT DEFAULT ''
        )
    """)
    
    # Ajouter la colonne notes si elle n'existe pas déjà (pour les bases existantes)
    try:
        cur.execute("ALTER TABLE utilisateurs ADD COLUMN notes TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        # La colonne existe déjà, c'est normal
        pass
    
    conn.commit()
    conn.close()
''' # à décacher si reset de la base de données de jeu avec commande dans terminal: attrib -r game.db

#initialisation de la base de données du jeu dans la base de données game.db pour différentier les données du jeu des données des utilisateurs
def init_game_db():
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    
    # Création de la table Carte_Enac
    cur.execute("DROP TABLE IF EXISTS Carte_Enac")
    cur.execute("""
        CREATE TABLE Carte_Enac (
            id_Enac TEXT PRIMARY KEY,
            Nom TEXT NOT NULL,
            Prénom TEXT NOT NULL,
            Couleur_de_cheveux TEXT,
            Genre TEXT
        )
    """)

    # Création de la table Boite_mail
    cur.execute("DROP TABLE IF EXISTS Boite_mail")
    cur.execute("""
        CREATE TABLE Boite_mail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            message TEXT
        )
    """)

    # Création de la table PPL
    cur.execute("DROP TABLE IF EXISTS PPL")
    cur.execute("""
        CREATE TABLE PPL (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nom TEXT,
            Prenom TEXT,
            Date_obtention TEXT
        )
    """)

    # Création de la table Personnel_Enac
    cur.execute("DROP TABLE IF EXISTS Personnel_Enac")
    cur.execute("""
        CREATE TABLE Personnel_Enac (
            id_Enac TEXT INTEGER SECONDARY KEY,
            matiere TEXT,
            Enseignement_aux_APPR TEXT
        )
    """)

    # Création de la table Eleve
    cur.execute("DROP TABLE IF EXISTS Eleve")
    cur.execute("""
        CREATE TABLE Eleve (
            id_Enac TEXT PRIMARY KEY,
            Promotion TEXT
        )
    """)

    # Création de la table Goelia
    cur.execute("DROP TABLE IF EXISTS Goelia")
    cur.execute("""
        CREATE TABLE Goelia (
            id_Enac TEXT PRIMARY KEY,
            Etage TEXT,
            Numero_de_chambre TEXT,
            Surface TEXT,
            Nombre_d_habitants TEXT
        )
    """)

    # Création de la table Temoignages
    cur.execute("DROP TABLE IF EXISTS Temoignages")
    cur.execute("""
        CREATE TABLE Temoignages (
            id_Enac TEXT INTEGER SECONDARY KEY,
            temoignage TEXT
        )
    """)

    # Création de la table Whatsapp
    cur.execute("DROP TABLE IF EXISTS Whatsapp")
    cur.execute("""
        CREATE TABLE Whatsapp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo_organisateur TEXT,
            Nom_evenement TEXT,
            date TEXT,
            Lieu TEXT,
            Ville TEXT
        )
    """)

    # Création de la table Messages
    cur.execute("DROP TABLE IF EXISTS Messages")
    cur.execute("""
        CREATE TABLE Messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nom_evenement TEXT,
            pseudo TEXT,
            message TEXT,
            date TEXT
        )
    """)

    # Importer les données depuis le fichier Excel pour Carte_Enac
    try:
        excel_path = Path("templates/carteenac.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['id_Enac'] = df['id_Enac'].astype(str)
            df['Nom'] = df['Nom'].astype(str)
            df['Prénom'] = df['Prénom'].astype(str)
            df['Couleur_de_cheveux'] = df['Couleur_de_cheveux'].astype(str)
            df['Genre'] = df['Genre'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Carte_Enac (id_Enac, Nom, Prénom, Couleur_de_cheveux, Genre) VALUES (?, ?, ?, ?, ?)',
                    (str(row['id_Enac']), str(row['Nom']), str(row['Prénom']), 
                     str(row['Couleur_de_cheveux']), str(row['Genre']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Carte_Enac de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Carte_Enac: {str(e)}")
        cur.executemany("INSERT INTO Carte_Enac (id_Enac, Nom, Prénom, Couleur_de_cheveux, Genre) VALUES (?, ?, ?, ?, ?)", donnees)

    # Importer les données depuis le fichier Excel pour Boite_mail
    try:
        excel_path = Path("templates/Boite_mail.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['Date'] = df['Date'].astype(str)
            df['Message'] = df['Message'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Boite_mail (date, message) VALUES (?, ?)',
                    (str(row['Date']), str(row['Message']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Boite_mail de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Boite_mail: {str(e)}")

    # Importer les données depuis le fichier Excel pour PPL
    try:
        excel_path = Path("templates/PPL.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['Nom'] = df['Nom'].astype(str)
            df['Prenom '] = df['Prenom '].astype(str)  # Espace après Prenom, pas d'accent
            df['date_obtention'] = df['date_obtention'].astype(str)  # Tout en minuscules avec underscore
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO PPL (Nom, Prenom, Date_obtention) VALUES (?, ?, ?)',
                    (str(row['Nom']), str(row['Prenom ']), str(row['date_obtention']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table PPL de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de PPL: {str(e)}")

    # Importer les données depuis le fichier Excel pour Personnel_Enac
    try:
        excel_path = Path("templates/Personnel_Enac.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['id_Enac'] = df['id_Enac'].astype(str)
            df['matiere'] = df['matiere'].astype(str)
            df['Enseignement_aux_APPR'] = df['Enseignement_aux_APPR'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Personnel_Enac (id_Enac, matiere, Enseignement_aux_APPR) VALUES (?, ?, ?)',
                    (str(row['id_Enac']), str(row['matiere']), str(row['Enseignement_aux_APPR']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Personnel_Enac de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Personnel_Enac: {str(e)}")

    # Importer les données depuis le fichier Excel pour Eleve
    try:
        excel_path = Path("templates/Eleve.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['id_Enac'] = df['id_Enac'].astype(str)
            df['Promotion'] = df['Promotion'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Eleve (id_Enac, Promotion) VALUES (?, ?)',
                    (str(row['id_Enac']), str(row['Promotion']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Eleve de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Eleve: {str(e)}")

    # Importer les données depuis le fichier Excel pour Goelia
    try:
        excel_path = Path("templates/Goelia.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['id_Enac'] = df['id_Enac'].astype(str)
            df['Etage'] = df['Etage'].astype(str)
            df['Numero_de_chambre'] = df['Numero_de_chambre'].astype(str)
            df['Surface'] = df['Surface'].astype(str)
            df['Nombre_d_habitants'] = df['Nombre_d_habitants'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Goelia (id_Enac, Etage, Numero_de_chambre, Surface, Nombre_d_habitants) VALUES (?, ?, ?, ?, ?)',
                    (str(row['id_Enac']), str(row['Etage']), str(row['Numero_de_chambre']), 
                     str(row['Surface']), str(row['Nombre_d_habitants']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Goelia de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Goelia: {str(e)}")

    # Importer les données depuis le fichier Excel pour Temoignages
    try:
        excel_path = Path("templates/Témoignage.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['id_Enac'] = df['id_Enac'].astype(str)
            df['temoignage'] = df['temoignage'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Temoignages (id_Enac, temoignage) VALUES (?, ?)',
                    (str(row['id_Enac']), str(row['temoignage']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Temoignages de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Temoignages: {str(e)}")

    # Importer les données depuis le fichier Excel pour Whatsapp
    try:
        excel_path = Path("templates/Whatsapp.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['pseudo_organisateur'] = df['pseudo_organisateur'].astype(str)
            df['Nom_evenement'] = df['Nom_evenement'].astype(str)
            df['date'] = df['date'].astype(str)
            df['Lieu'] = df['Lieu'].astype(str)
            df['Ville'] = df['Ville'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Whatsapp (pseudo_organisateur, Nom_evenement, date, Lieu, Ville) VALUES (?, ?, ?, ?, ?)',
                    (str(row['pseudo_organisateur']), str(row['Nom_evenement']), str(row['date']), 
                     str(row['Lieu']), str(row['Ville']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Whatsapp de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Whatsapp: {str(e)}")

    # Importer les données depuis le fichier Excel pour Messages
    try:
        excel_path = Path("templates/Messages.xlsx")
        if excel_path.is_file():
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            
            # Convertir les types de données
            df['Nom_evenement'] = df['Nom_evenement'].astype(str)
            df['pseudo'] = df['pseudo'].astype(str)
            df['message'] = df['message'].astype(str)
            df['date'] = df['date'].astype(str)
            
            # Insérer les données
            for index, row in df.iterrows():
                cur.execute(
                    'INSERT INTO Messages (Nom_evenement, pseudo, message, date) VALUES (?, ?, ?, ?)',
                    (str(row['Nom_evenement']), str(row['pseudo']), str(row['message']), str(row['date']))
                )
            print(f"✅ {len(df)} lignes importées avec succès dans la table Messages de game.db!")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation de Messages: {str(e)}")
    
    conn.commit()
    conn.close()
''' # à retirer si reset de la base de données du jeu

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["GET", "POST"])
def query():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    requete = ""
    erreur = ""
    lignes = []
    colonnes = []
    notes = ""

    # Charger les notes de l'utilisateur depuis la base de données
    conn_user = sqlite3.connect("ma_base.db")
    cur_user = conn_user.cursor()
    cur_user.execute("SELECT notes FROM utilisateurs WHERE mail = ?", (session['mail'],))
    user_data = cur_user.fetchone()
    if user_data:
        notes = user_data[0] or ""
    conn_user.close()

    if request.method == "POST" and "sql" in request.form:
        # Nettoyer les résultats précédents du coupable quand on fait une nouvelle requête SQL
        session.pop('culprit_result', None)
        
        # Récupérer les notes du formulaire et les sauvegarder
        notes = request.form.get("notes", "")
        
        # Sauvegarder les notes dans la base de données
        conn_user = sqlite3.connect("ma_base.db")
        cur_user = conn_user.cursor()
        cur_user.execute("UPDATE utilisateurs SET notes = ? WHERE mail = ?", (notes, session['mail']))
        conn_user.commit()
        conn_user.close()
        
        requete = request.form["sql"]
        try:
            conn = sqlite3.connect("game.db")  # Utilisation de la base de données du jeu
            cur = conn.cursor()
            cur.execute(requete)

            if requete.strip().lower().startswith("select"):
                lignes = cur.fetchall()
                colonnes = [desc[0] for desc in cur.description]
            else:
                conn.commit()
                resultat = "Veuillez saisir une requête."

            conn.close()
        except sqlite3.Error as erreur_sql:
            erreur = f"Erreur SQL : {erreur_sql}"
        
    return render_template("query.html", requete=requete, colonnes=colonnes, lignes=lignes, erreur=erreur, notes=notes)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        mail = request.form['mail']
        password = request.form['password']
        
        conn = sqlite3.connect("ma_base.db")  # Base de données des utilisateurs
        cur = conn.cursor()
        cur.execute("SELECT * FROM utilisateurs WHERE mail = ? AND password = ?", (mail, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            session['username'] = user[2]  # Stocke le username dans la session
            session['mail'] = user[1]      # Stocke l'email dans la session
            return redirect(url_for('query'))
        else:
            error = "Email ou mot de passe incorrect"
    
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        mail = request.form['mail']
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect("ma_base.db")  # Base de données des utilisateurs
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO utilisateurs (mail, username, password) VALUES (?, ?, ?)", 
                       (mail, username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Cet email est déjà utilisé"
            conn.close()
    
    return render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/settings")
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("settings.html")

@app.route("/update_account", methods=["POST"])
def update_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    mail = request.form['mail']
    username = request.form['username']
    new_password = request.form['new_password']
    current_password = request.form['current_password']
    
    conn = sqlite3.connect("ma_base.db")  # Base de données des utilisateurs
    cur = conn.cursor()
    
    # Vérifier le mot de passe actuel
    cur.execute("SELECT * FROM utilisateurs WHERE mail = ? AND password = ?", 
                (session['mail'], current_password))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return render_template("settings.html", error="Mot de passe actuel incorrect")
    
    try:
        if new_password:
            # Si un nouveau mot de passe est fourni, le mettre à jour aussi
            cur.execute("""
                UPDATE utilisateurs 
                SET mail = ?, username = ?, password = ?
                WHERE mail = ?
            """, (mail, username, new_password, session['mail']))
        else:
            # Sinon, mettre à jour uniquement mail et username
            cur.execute("""
                UPDATE utilisateurs 
                SET mail = ?, username = ?
                WHERE mail = ?
            """, (mail, username, session['mail']))
        
        conn.commit()
        
        # Mettre à jour la session
        session['mail'] = mail
        session['username'] = username
        
        conn.close()
        return render_template("settings.html", success="Modifications enregistrées avec succès")
    
    except sqlite3.IntegrityError:
        conn.close()
        return render_template("settings.html", error="Cet email est déjà utilisé")

@app.route("/delete_account", methods=["POST"])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    password = request.form['password']
    
    conn = sqlite3.connect("ma_base.db")  # Base de données des utilisateurs
    cur = conn.cursor()
    
    # Vérifier le mot de passe
    cur.execute("SELECT * FROM utilisateurs WHERE mail = ? AND password = ?", 
                (session['mail'], password))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return render_template("settings.html", error="Mot de passe incorrect")
    
    # Supprimer le compte
    cur.execute("DELETE FROM utilisateurs WHERE mail = ?", (session['mail'],))
    conn.commit()
    conn.close()
    
    # Déconnecter l'utilisateur
    session.clear()
    return redirect(url_for('index'))

@app.route("/check_culprit", methods=["POST"])
def check_culprit():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    culprit_name = request.form['culprit_name'].strip().lower()
    
    # Liste des noms possibles pour le vrai coupable (à adapter selon votre jeu)
    # Vous devrez remplacer "nom_du_vrai_coupable" par le vrai nom du coupable de votre enquête
    correct_answers = ["Magalie Berdah", "magalie berdah", "MAGALIE BERDAH", "Magalie berdah", "magalie berdah", "Magalie Berdah", "magalie berdah", "MAGALIE BERDAH", "magalie Berdah"]  # À personnaliser
    
    if culprit_name in correct_answers:
        session['culprit_result'] = 'success'
    else:
        session['culprit_result'] = 'error'
    
    return redirect(url_for('query'))

if __name__ == "__main__":
    init_user_db()  # Initialiser la base de données des utilisateurs
    #init_game_db()  # Initialiser la base de données du jeu, à décacher si reset de la base de données du jeu
    app.run(debug=True)
