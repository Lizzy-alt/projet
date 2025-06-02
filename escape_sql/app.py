from flask import Flask, render_template, request, session, redirect, url_for, abort, jsonify
from models import db, GameSession
import os
import secrets
import logging
import traceback

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
def game():
    try:
        return render_template('game.html')
    except Exception as e:
        logger.error(f"Erreur dans /game: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html', 
                            error=f"Une erreur est survenue lors du chargement de l'interface: {str(e)}")

@app.route('/submit', methods=['POST'])
def submit():
    try:
        user_sql = request.form.get('sql', '').strip()
        if not user_sql:
            return jsonify({'error': "La requête SQL ne peut pas être vide"})
        
        # Exécution directe de la requête
        try:
            results = db.execute(user_sql)
            return jsonify({'results': results})
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
def check_suspect():
    try:
        suspect = request.form.get('suspect', '').strip()
        if not suspect:
            return jsonify({
                'correct': False,
                'message': "Veuillez entrer le nom d'un suspect."
            })

        # Dans cet exemple, Marie Dubois est la coupable
        if suspect.lower() == "marie dubois":
            return jsonify({
                'correct': True,
                'message': "Bravo ! Vous avez trouvé le coupable. Marie Dubois a en effet empoisonné Jean Martin en utilisant ses connaissances en pharmacie."
            })
        else:
            return jsonify({
                'correct': False,
                'message': "Ce n'est pas la bonne personne. Continuez votre enquête..."
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
