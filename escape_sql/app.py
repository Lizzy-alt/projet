from flask import Flask, render_template, request, session, redirect, url_for, abort, jsonify, flash
from models import db, GameSession
import os
import secrets
import logging
import traceback
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import time

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Génération d'une clé secrète aléatoire
app.secret_key = secrets.token_hex(32)

# Obtenir le chemin absolu du répertoire de l'application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Variable pour suivre si la base de données a été initialisée
_db_initialized = False

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            _db_initialized = True
            logger.info("Base de données initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
            logger.error(traceback.format_exc())
            return render_template('error.html', 
                                error="Erreur d'initialisation de la base de données. Détails: " + str(e))

def init_db():
    """Initialise la base de données si elle n'existe pas"""
    try:
        # Force la réinitialisation de la base de données
        db_path = os.path.join(BASE_DIR, 'db', 'murder_mystery.db')
        if os.path.exists(db_path):
            logger.info(f"Suppression de l'ancienne base de données: {db_path}")
            os.remove(db_path)
        
        logger.info("Création d'une nouvelle base de données...")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialise le schéma
        schema_path = os.path.join(BASE_DIR, 'schema.sql')
        logger.info(f"Chargement du schéma depuis: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_content = f.read()
            logger.debug(f"Contenu du schéma:\n{schema_content}")
            db.execute_script(schema_content)
        
        # Charge les données initiales
        data_path = os.path.join(BASE_DIR, 'initial_data.sql')
        if os.path.exists(data_path):
            logger.info(f"Chargement des données initiales depuis: {data_path}")
            with open(data_path, 'r', encoding='utf-8') as f:
                data_content = f.read()
                logger.debug(f"Contenu des données initiales:\n{data_content}")
                db.execute_script(data_content)
        
        # Vérifie que les données ont été chargées
        result = db.execute("SELECT COUNT(*) as count FROM hint")
        hint_count = result[0]['count'] if result else 0
        logger.info(f"Nombre d'indices dans la base : {hint_count}")
        
        if hint_count == 0:
            raise Exception("Aucun indice n'a été chargé dans la base de données")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
@login_required
def game():
    try:
        # Initialiser le temps de début si ce n'est pas déjà fait
        if not session.get('game_start_time'):
            session['game_start_time'] = str(time.time())
            session['query_count'] = 0
        return render_template('game.html')
    except Exception as e:
        logger.error(f"Erreur dans /game: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html', 
                            error=f"Une erreur est survenue lors du chargement de l'interface: {str(e)}")

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not all([email, username, password]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400

        # Vérifier si l'email ou le username existe déjà
        existing_user = db.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            [email, username]
        )
        if existing_user:
            return jsonify({'error': 'Email ou nom d\'utilisateur déjà utilisé'}), 400

        # Créer le nouvel utilisateur
        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            [email, username, password_hash]
        )

        return jsonify({'message': 'Compte créé avec succès'}), 201

    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {str(e)}")
        return jsonify({'error': 'Erreur lors de l\'inscription'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        login = data.get('login')  # Peut être email ou username
        password = data.get('password')

        if not all([login, password]):
            return jsonify({'error': 'Informations de connexion incomplètes'}), 400

        # Rechercher l'utilisateur par email ou username
        user = db.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            [login, login]
        )

        if not user or not check_password_hash(user[0]['password_hash'], password):
            return jsonify({'error': 'Identifiants invalides'}), 401

        # Créer la session
        session['user_id'] = user[0]['id']
        session['username'] = user[0]['username']
        session['game_start_time'] = None
        session['query_count'] = 0

        return jsonify({
            'message': 'Connexion réussie',
            'username': user[0]['username'],
            'redirect': url_for('index')
        })

    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {str(e)}")
        return jsonify({'error': 'Erreur lors de la connexion'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/data')
@login_required
def get_user_data():
    try:
        user = db.execute(
            "SELECT username, req_count, resolve_time FROM users WHERE id = ?",
            [session['user_id']]
        )[0]
        
        # Calculer le temps écoulé
        start_time = session.get('game_start_time')
        current_time = 0
        if start_time:
            current_time = int(time.time() - float(start_time))
        
        return jsonify({
            'username': user['username'],
            'req_count': user['req_count'],
            'resolve_time': user['resolve_time'],
            'current_count': session.get('query_count', 0),
            'current_time': current_time
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données utilisateur: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération des données'}), 500

@app.route('/user/record', methods=['POST'])
@login_required
def record_game_stats():
    try:
        # Ne mettre à jour que si c'est le premier essai réussi
        user = db.execute(
            "SELECT req_count, resolve_time FROM users WHERE id = ?",
            [session['user_id']]
        )[0]

        if user['resolve_time'] is None:  # Premier essai réussi
            db.execute(
                "UPDATE users SET req_count = ?, resolve_time = ? WHERE id = ?",
                [session['query_count'], 
                 int(time.time() - float(session['game_start_time'])),
                 session['user_id']]
            )
            return jsonify({'message': 'Statistiques enregistrées'})
        return jsonify({'message': 'Statistiques déjà enregistrées'})

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des statistiques: {str(e)}")
        return jsonify({'error': 'Erreur lors de l\'enregistrement des statistiques'}), 500

@app.route('/leaderboard')
def get_leaderboard():
    try:
        leaderboard = db.execute("""
            SELECT username, req_count, resolve_time 
            FROM users 
            WHERE resolve_time IS NOT NULL 
            ORDER BY req_count ASC, resolve_time ASC
        """)
        return jsonify(leaderboard)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du leaderboard: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération du leaderboard'}), 500

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    try:
        # Initialiser le temps de début si ce n'est pas déjà fait
        if not session.get('game_start_time'):
            session['game_start_time'] = str(time.time())
            session['query_count'] = 0

        user_sql = request.form.get('sql', '').strip()
        if not user_sql:
            return jsonify({'error': "La requête SQL ne peut pas être vide"})
        
        # Incrémenter le compteur de requêtes
        session['query_count'] = session.get('query_count', 0) + 1
        
        # Exécution de la requête
        try:
            results = db.execute(user_sql)
            current_time = int(time.time() - float(session.get('game_start_time', str(time.time()))))
            return jsonify({
                'results': results,
                'query_count': session['query_count'],
                'elapsed_time': current_time
            })
        except Exception as e:
            return jsonify({'error': str(e)})
            
    except Exception as e:
        logger.error(f"Erreur dans /submit: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': "Une erreur est survenue lors de l'exécution de votre requête"})

@app.route('/schema')
def schema():
    """Retourne la structure des tables disponibles"""
    try:
        tables = {}
        for table in db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT IN ('sqlite_sequence', 'hint')
        """):
            table_name = table['name']
            columns = db.execute(f"PRAGMA table_info({table_name})")
            tables[table_name] = [
                {'name': col['name'], 'type': col['type']}
                for col in columns
            ]
        return jsonify(tables)
    except Exception as e:
        logger.error(f"Erreur dans /schema: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/check-suspect', methods=['POST'])
@login_required
def check_suspect():
    try:
        suspect = request.form.get('suspect', '').strip()
        if not suspect:
            return jsonify({
                'correct': False,
                'message': "Veuillez entrer le nom d'un suspect."
            })

        # Marie Dubois est la coupable
        if suspect.lower() == "marie dubois":
            # Vérifier si c'est la première résolution
            user = db.execute(
                "SELECT resolve_time FROM users WHERE id = ?",
                [session['user_id']]
            )[0]

            if user['resolve_time'] is None:
                # S'assurer que le temps de début existe
                start_time = session.get('game_start_time')
                if not start_time:
                    start_time = str(time.time() - 1)  # Par défaut, 1 seconde si pas de temps de début
                
                # Enregistrer les statistiques du premier essai
                current_time = int(time.time() - float(start_time))
                db.execute(
                    "UPDATE users SET req_count = ?, resolve_time = ? WHERE id = ?",
                    [session.get('query_count', 0), current_time, session['user_id']]
                )

                # Réinitialiser le timer pour les prochaines parties
                session['game_start_time'] = None
                session['query_count'] = 0

            return jsonify({
                'correct': True,
                'message': "Bravo ! Vous avez trouvé le coupable. Marie Dubois a en effet empoisonné Jean Martin. Les preuves montrent qu'elle l'a rencontré au restaurant, l'a suivi au parc et a utilisé ses connaissances en pharmacie pour l'empoisonner."
            })
        else:
            return jsonify({
                'correct': False,
                'message': "Ce n'est pas la bonne personne... Continuez votre enquête."
            })

    except Exception as e:
        logger.error(f"Erreur dans /check-suspect: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'correct': False,
            'message': "Une erreur est survenue lors de la vérification du suspect."
        })

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Une erreur interne est survenue"), 500

if __name__ == '__main__':
    app.run(debug=False)  # debug=False en production
