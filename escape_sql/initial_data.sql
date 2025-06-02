-- Insertion des données pour le murder mystery

-- Rapport de la scène de crime
INSERT INTO crime_scene_report (date, type, description, location) VALUES 
('2024-03-15', 'Meurtre', 'Corps découvert dans le parc central. La victime, Jean Martin, 45 ans, a été retrouvée près de la fontaine. Cause probable de la mort : empoisonnement. Heure estimée du décès : entre 21h et 23h.', 'Parc Central');

-- Personnes impliquées
INSERT INTO person (name, age, address, occupation, phone_number) VALUES
('Jean Martin', 45, '123 Rue des Lilas', 'Banquier', '0123456789'),
('Marie Dubois', 38, '45 Avenue des Roses', 'Pharmacienne', '0234567890'),
('Pierre Durand', 52, '78 Boulevard des Pins', 'Chef cuisinier', '0345678901'),
('Sophie Lambert', 29, '15 Rue du Commerce', 'Serveuse', '0456789012'),
('Lucas Moreau', 41, '92 Avenue Centrale', 'Gardien du parc', '0567890123');

-- Témoignages
INSERT INTO interview (person_id, date, transcript) VALUES
(2, '2024-03-16', 'J''ai vu M. Martin au restaurant hier soir. Il dînait avec une femme que je ne connaissais pas. Ils semblaient se disputer.'),
(3, '2024-03-16', 'M. Martin a dîné dans mon restaurant hier soir. Il a commandé le plat du jour et un verre de vin rouge. Il est parti vers 21h.'),
(4, '2024-03-16', 'J''ai servi M. Martin et Mme Dubois hier soir. Elle semblait très en colère contre lui. J''ai entendu quelque chose à propos d''argent.'),
(5, '2024-03-15', 'Je faisais ma ronde habituelle quand j''ai trouvé le corps près de la fontaine vers 23h30. J''ai immédiatement appelé la police.');

-- Preuves
INSERT INTO evidence (type, description, location_found, date_found) VALUES
('Fiole', 'Petite fiole en verre vide avec des traces de substance inconnue', 'Près de la fontaine', '2024-03-15'),
('Téléphone', 'Téléphone portable de la victime', 'Dans la poche de la victime', '2024-03-15'),
('Note', 'Note manuscrite : "Il faut qu''on parle de l''argent. 20h au restaurant."', 'Dans le portefeuille de la victime', '2024-03-15');

-- Relations
INSERT INTO relationship (person1_id, person2_id, relationship_type) VALUES
(1, 2, 'Collègue'),
(1, 3, 'Client régulier'),
(2, 4, 'Connaissance'),
(3, 4, 'Patron-Employé');

-- Mouvements
INSERT INTO movement (person_id, date, location) VALUES
(1, '2024-03-15 20:00', 'Restaurant Le Gourmet'),
(2, '2024-03-15 20:00', 'Restaurant Le Gourmet'),
(1, '2024-03-15 21:00', 'Parc Central'),
(2, '2024-03-15 21:15', 'Parc Central'),
(2, '2024-03-15 22:00', 'Pharmacie Centrale'),
(5, '2024-03-15 23:30', 'Parc Central');

-- Indices pour guider les joueurs
INSERT INTO hint (level, description, query_example, explanation) VALUES
(1, 'Commencez par examiner le rapport de la scène de crime pour comprendre ce qui s''est passé.', 
'SELECT * FROM crime_scene_report WHERE type = ''Meurtre''',
'Cette requête vous permet de voir les détails du crime qui a été commis.'),

(2, 'Identifiez les personnes qui étaient présentes au restaurant le soir du meurtre.',
'SELECT p.name, m.date, m.location 
FROM person p 
JOIN movement m ON p.id = m.person_id 
WHERE m.location LIKE ''%Restaurant%''',
'Cette requête vous montre qui était au restaurant ce soir-là.'),

(3, 'Examinez les témoignages concernant les événements au restaurant.',
'SELECT p.name, i.transcript 
FROM interview i 
JOIN person p ON i.person_id = p.id 
WHERE i.transcript LIKE ''%restaurant%''',
'Les témoignages peuvent révéler des informations cruciales sur ce qui s''est passé.'),

(4, 'Suivez les mouvements suspects après le restaurant.',
'SELECT p.name, m.date, m.location 
FROM person p 
JOIN movement m ON p.id = m.person_id 
WHERE m.date BETWEEN ''2024-03-15 21:00'' AND ''2024-03-15 23:00''',
'Cette requête vous montre les déplacements des suspects pendant la période du crime.'),

(5, 'Examinez les preuves trouvées sur la scène de crime.',
'SELECT * FROM evidence WHERE date_found = ''2024-03-15''',
'Les preuves physiques sont cruciales pour résoudre l''affaire.'); 