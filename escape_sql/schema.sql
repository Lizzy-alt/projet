-- Schéma de la base de données pour le SQL Murder Mystery

-- Table des rapports de scène de crime
CREATE TABLE IF NOT EXISTS crime_scene_report (
    id INTEGER PRIMARY KEY,
    date TEXT,
    type TEXT,
    description TEXT,
    location TEXT
);

-- Table des personnes
CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    address TEXT,
    occupation TEXT,
    phone_number TEXT
);

-- Table des témoignages
CREATE TABLE IF NOT EXISTS interview (
    id INTEGER PRIMARY KEY,
    person_id INTEGER,
    date TEXT,
    transcript TEXT,
    FOREIGN KEY (person_id) REFERENCES person(id)
);

-- Table des preuves physiques
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY,
    type TEXT,
    description TEXT,
    location_found TEXT,
    date_found TEXT
);

-- Table des relations entre personnes
CREATE TABLE IF NOT EXISTS relationship (
    id INTEGER PRIMARY KEY,
    person1_id INTEGER,
    person2_id INTEGER,
    relationship_type TEXT,
    FOREIGN KEY (person1_id) REFERENCES person(id),
    FOREIGN KEY (person2_id) REFERENCES person(id)
);

-- Table des mouvements suspects
CREATE TABLE IF NOT EXISTS movement (
    id INTEGER PRIMARY KEY,
    person_id INTEGER,
    date TEXT,
    location TEXT,
    FOREIGN KEY (person_id) REFERENCES person(id)
);

-- Table des indices pour guider les joueurs
CREATE TABLE IF NOT EXISTS hint (
    id INTEGER PRIMARY KEY,
    level INTEGER,
    description TEXT,
    query_example TEXT,
    explanation TEXT
); 