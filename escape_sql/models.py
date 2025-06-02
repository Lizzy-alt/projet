import sqlite3
import uuid
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path):
        # Obtenir le chemin absolu du répertoire contenant ce fichier
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Construire le chemin absolu pour la base de données
        self.db_path = os.path.join(self.base_dir, db_path)
        logger.info(f"Initialisation de DatabaseManager avec db_path: {self.db_path}")
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Crée la base de données et initialise le schéma si nécessaire"""
        try:
            if not os.path.exists(self.db_path):
                logger.info(f"Base de données non trouvée à {self.db_path}, création en cours...")
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                self._init_db()
            else:
                logger.info("Base de données existante trouvée")
                # Vérifie si la table hint existe et contient des données
                conn = self.connect()
                try:
                    result = conn.execute("SELECT COUNT(*) FROM hint").fetchone()
                    logger.info(f"Nombre d'indices dans la base : {result[0]}")
                except sqlite3.OperationalError:
                    logger.warning("La table 'hint' n'existe pas, réinitialisation de la base...")
                    self._init_db()
                finally:
                    conn.close()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification/création de la base : {str(e)}")
            raise

    def _init_db(self):
        """Initialise la base de données avec le schéma"""
        try:
            schema_path = os.path.join(self.base_dir, 'schema.sql')
            logger.info(f"Chargement du schéma depuis : {schema_path}")
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            conn = self.connect()
            try:
                conn.executescript(schema)
                conn.commit()
                logger.info("Schéma de base de données initialisé avec succès")

                # Charge les données initiales
                data_path = os.path.join(self.base_dir, 'initial_data.sql')
                if os.path.exists(data_path):
                    logger.info(f"Chargement des données initiales depuis : {data_path}")
                    with open(data_path, 'r', encoding='utf-8') as f:
                        conn.executescript(f.read())
                    conn.commit()
                    logger.info("Données initiales chargées avec succès")
                else:
                    logger.warning(f"Fichier de données initiales non trouvé : {data_path}")
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base : {str(e)}")
            raise

    def connect(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Erreur de connexion à la base : {str(e)}")
            raise

    def execute(self, sql, params=None):
        try:
            conn = self.connect()
            try:
                cur = conn.cursor()
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                rows = cur.fetchall()
                conn.commit()
                return [dict(row) for row in rows]
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Erreur d'exécution SQL : {str(e)}\nRequête : {sql}\nParamètres : {params}")
            raise

    def execute_script(self, sql_script):
        try:
            conn = self.connect()
            try:
                conn.executescript(sql_script)
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Erreur d'exécution du script SQL : {str(e)}")
            raise

# Instanciation globale pour usage direct
db = DatabaseManager('db/murder_mystery.db')

class MurderMystery:
    def __init__(self):
        self.current_level = 1
        self.total_levels = self._get_total_levels()

    def _get_total_levels(self):
        result = db.execute('SELECT MAX(level) as max_level FROM hint')
        return result[0]['max_level'] if result else 0

    def get_current_hint(self):
        result = db.execute('SELECT * FROM hint WHERE level = ?', (self.current_level,))
        return result[0] if result else None

    def check_solution(self, user_query, expected_result):
        """Vérifie si la requête de l'utilisateur donne le résultat attendu"""
        try:
            user_result = db.execute(user_query)
            return self._compare_results(user_result, expected_result)
        except Exception as e:
            return False, str(e)

    def _compare_results(self, result1, result2):
        """Compare deux résultats de requêtes"""
        # Simplifie les résultats pour la comparaison
        def simplify_result(result):
            return [{k: str(v).lower() for k, v in row.items()} for row in result]
        
        try:
            simple1 = simplify_result(result1)
            simple2 = simplify_result(result2)
            return simple1 == simple2, None
        except Exception as e:
            return False, str(e)

class GameSession:
    sessions = {}

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.mystery = MurderMystery()
        self.current_level = 1
        self.completed_levels = set()

    def start(self):
        GameSession.sessions[self.session_id] = self

    @classmethod
    def load(cls, session_id):
        return cls.sessions.get(session_id)

    def get_current_hint(self):
        return self.mystery.get_current_hint()

    def check_level(self, user_query):
        hint = self.get_current_hint()
        if not hint:
            return False, "Niveau non trouvé"
        
        success, error = self.mystery.check_solution(user_query, db.execute(hint['query_example']))
        if success:
            self.completed_levels.add(self.current_level)
            if self.current_level < self.mystery.total_levels:
                self.current_level += 1
        return success, error if error else hint['explanation']

    def is_game_completed(self):
        """Vérifie si le jeu est terminé"""
        if self.mystery.total_levels == 0:
            return False
        return self.current_level > self.mystery.total_levels
