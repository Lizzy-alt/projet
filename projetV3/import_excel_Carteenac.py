import pandas as pd
import sqlite3
from pathlib import Path

def import_excel_to_db(excel_file, table_name='Carte_Enac', database_name='game.db'):
    try:
        # Lire le fichier Excel
        print(f"Lecture du fichier Excel: {excel_file}")
        df = pd.read_excel(excel_file)
        
        # Afficher les colonnes trouvées
        print("\nColonnes trouvées dans le fichier Excel:")
        print(df.columns.tolist())
        
        # Convertir les types de données
        df['id_Enac'] = df['id_Enac'].astype(str)
        df['Nom'] = df['Nom'].astype(str)
        df['Prénom'] = df['Prénom'].astype(str)
        df['Couleur_de_cheveux'] = df['Couleur_de_cheveux'].astype(str)
        df['Genre'] = df['Genre'].astype(str)
        
        # Connexion à la base de données SQLite du jeu
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id_Enac TEXT PRIMARY KEY,
                Nom TEXT,
                Prénom TEXT,
                Couleur_de_cheveux TEXT,
                Genre TEXT
            )
        ''')
        
        # Supprimer les données existantes de la table
        cursor.execute(f'DELETE FROM {table_name}')
        print("\nAncienne table vidée.")
        
        # Insérer les nouvelles données
        for index, row in df.iterrows():
            cursor.execute(
                f'INSERT INTO {table_name} (id_Enac, Nom, Prénom, Couleur_de_cheveux, Genre) VALUES (?, ?, ?, ?, ?)',
                (str(row['id_Enac']), str(row['Nom']), str(row['Prénom']), 
                 str(row['Couleur_de_cheveux']), str(row['Genre']))
            )
        
        # Valider les changements
        conn.commit()
        print(f"\n✅ {len(df)} lignes importées avec succès dans la table {table_name} de {database_name}!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'importation: {str(e)}")
        print("\nDonnées de la première ligne pour debug:")
        if 'df' in locals():
            print(df.iloc[0].to_dict())
        
    finally:
        # Fermer la connexion
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Chemin du fichier Excel dans le dossier templates
    excel_path = Path("templates/carteenac.xlsx")
    
    if excel_path.is_file():
        import_excel_to_db(excel_path)
    else:
        print("❌ Fichier non trouvé dans le dossier templates.") 