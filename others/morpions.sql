-- ============================================================
-- Contexte : schéma "morpion"
-- Si le schéma n'existe pas encore, crée-le une fois pour toutes :
--   CREATE SCHEMA morpion;
-- Puis lance ce script.
-- ============================================================

SET search_path TO morpion, public;

-- ============================================================
-- Nettoyage : on supprime d'abord les tables si elles existent
-- dans le bon ordre (tables dépendantes -> tables de base)
-- ============================================================

DROP TABLE IF EXISTS logs_entry   CASCADE;  -- dépend de game
DROP TABLE IF EXISTS game         CASCADE;  -- dépend de team et config
DROP TABLE IF EXISTS team_morpion CASCADE;  -- dépend de team et morpion
DROP TABLE IF EXISTS config       CASCADE;
DROP TABLE IF EXISTS morpion      CASCADE;
DROP TABLE IF EXISTS team         CASCADE;

-- ============================================================
-- Table TEAM : représente les équipes (les "mazos")
-- - couleur unique
-- - date de création
-- ============================================================

CREATE TABLE team (
  id_team    SERIAL      PRIMARY KEY,                -- identifiant unique de l'équipe
  name       VARCHAR(80) NOT NULL,                   -- nom de l'équipe
  color      VARCHAR(40) NOT NULL,                   -- couleur de l'équipe (badge, UI)
  created_at DATE        NOT NULL DEFAULT CURRENT_DATE,
  CONSTRAINT uq_team_color UNIQUE (color)            -- une couleur ne peut être utilisée que par une seule équipe
);

-- ============================================================
-- Table MORPION : représente les "cartes" (templates réutilisables)
-- - nom
-- - image
-- - hp, attack, mana, accuracy >= 1
-- - somme des 4 caractéristiques = 15
-- Ces morpions ne sont pas détruits quand on supprime une équipe.
-- ============================================================

CREATE TABLE morpion (
  id_morpion SERIAL      PRIMARY KEY,                -- identifiant unique du morpion
  name       VARCHAR(80)  NOT NULL,                  -- nom du morpion
  image_url  VARCHAR(255) NOT NULL,                  -- chemin de l'image (t1.png, t2.png, ...)
  hp         INTEGER      NOT NULL CHECK (hp      >= 1),
  attack     INTEGER      NOT NULL CHECK (attack  >= 1),
  mana       INTEGER      NOT NULL CHECK (mana    >= 1),
  accuracy   INTEGER      NOT NULL CHECK (accuracy >= 1),
  CHECK (hp + attack + mana + accuracy = 15)         -- contrainte globale sur la répartition des points
);

-- ============================================================
-- Table TEAM_MORPION : composition des équipes (mazo ↔ cartes)
-- - une équipe peut avoir plusieurs morpions
-- - un morpion peut être dans plusieurs équipes
-- - si on supprime une équipe, on supprime automatiquement
--   sa composition (mais pas les morpions eux-mêmes).
-- ============================================================

CREATE TABLE team_morpion (
  team_id    INTEGER NOT NULL REFERENCES team(id_team)
                      ON DELETE CASCADE,            -- suppression du team => suppression auto de sa composition
  morpion_id INTEGER NOT NULL REFERENCES morpion(id_morpion)
                      ON DELETE RESTRICT,           -- impossible de supprimer un morpion s'il est utilisé dans un team
  PRIMARY KEY (team_id, morpion_id)                 -- un même morpion ne peut apparaître qu'une fois par équipe
  -- La contrainte "6 à 8 morpions par équipe" se gère par requêtes ou triggers, pas directement par CHECK.
);

-- ============================================================
-- Table CONFIG : configurations de parties (taille de grille, max tours)
-- - configuration datée
-- ============================================================

CREATE TABLE config (
  id_config  SERIAL     PRIMARY KEY,                 -- identifiant unique de la configuration
  created_at TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  grid_size  INTEGER    NOT NULL CHECK (grid_size IN (3, 4)),  -- 3x3 ou 4x4
  max_turns  INTEGER    NOT NULL CHECK (max_turns > 0)         -- nombre maximal de tours
);

-- ============================================================
-- Table GAME : représente une partie jouée entre deux équipes
-- - deux équipes différentes
-- - configuration utilisée
-- - date de début/fin
-- - équipe gagnante (optionnelle)
-- - on ne peut pas supprimer une équipe qui a déjà joué
-- ============================================================

CREATE TABLE game (
  id_game        SERIAL    PRIMARY KEY,              -- identifiant unique de la partie

  team1_id       INTEGER   NOT NULL REFERENCES team(id_team)
                             ON DELETE RESTRICT,     -- protège l'historique : une équipe ayant joué ne peut pas être supprimée
  team2_id       INTEGER   NOT NULL REFERENCES team(id_team)
                             ON DELETE RESTRICT,

  config_id      INTEGER   NOT NULL REFERENCES config(id_config)
                             ON DELETE RESTRICT,     -- on ne supprime pas une config utilisée

  started_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at       TIMESTAMP,                          -- NULL = partie non terminée

  winner_team_id INTEGER REFERENCES team(id_team)
                             ON DELETE SET NULL,     -- si on supprimait un team gagnant sans être dans team1/2 (cas théorique), on mettrait le gagnant à NULL

  CHECK (team1_id <> team2_id),                      -- une partie ne peut pas opposer la même équipe à elle-même
  CHECK (
    winner_team_id IS NULL
    OR winner_team_id = team1_id
    OR winner_team_id = team2_id
  )
);

-- ============================================================
-- Table LOGS_ENTRY : journal des actions pendant une partie
-- - identifiée par (game_id, num)
-- - datée
-- - message texte
-- ============================================================

CREATE TABLE logs_entry (
  game_id    INTEGER   NOT NULL REFERENCES game(id_game)
                        ON DELETE CASCADE,           -- suppression d'une partie => suppression de son journal
  num        INTEGER   NOT NULL CHECK (num > 0),     -- numéro d'ordre de la ligne dans la partie
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  message    TEXT      NOT NULL,
  PRIMARY KEY (game_id, num)                         -- unique par (partie, numéro)
);

-- ============================================================
-- INSERTS INICIALES
-- ============================================================

-- ------------------------------------------------------------
-- 1) EQUIPES (TEAM) – 10 équipes, couleurs toutes différentes
-- ------------------------------------------------------------

INSERT INTO team (name, color) VALUES
  ('Rouges furieux',      'red'),
  ('Bleus calmes',        'blue'),
  ('Verts agiles',        'green'),
  ('Jaunes rapides',      'yellow'),
  ('Noirs mystiques',     'black'),
  ('Blancs sereins',      'white'),
  ('Violets électriques', 'purple'),
  ('Oranges ardents',     'orange'),
  ('Cyan stratèges',      'cyan'),
  ('Roses ludiques',      'pink');

-- id_team seront 1 à 10 si la table était vide.


-- ------------------------------------------------------------
-- 2) MORPIONS (TEMPLATES) – 16 cartes t1.png ... t16.png
--    hp, attack, mana, accuracy >= 1 et somme = 15
-- ------------------------------------------------------------

INSERT INTO morpion (name, image_url, hp, attack, mana, accuracy) VALUES
  ('Tanky',             't1.png',  8, 3, 2, 2),
  ('Berserker',         't2.png',  7, 4, 2, 2),
  ('Chevalier',         't3.png',  6, 5, 2, 2),
  ('Paladin',           't4.png',  5, 5, 3, 2),
  ('Équilibré',         't5.png',  4, 4, 4, 3),
  ('Gardien mystique',  't6.png',  3, 5, 4, 3),
  ('Assassin rapide',   't7.png',  2, 6, 5, 2),
  ('Dueliste',          't8.png',  2, 5, 5, 3),
  ('Invocateur',        't9.png',  3, 3, 6, 3),
  ('Mage de feu',       't10.png', 2, 3, 4, 6),
  ('Mage de glace',     't11.png', 4, 2, 3, 6),
  ('Sniper',            't12.png', 5, 2, 2, 6),
  ('Ranger',            't13.png', 3, 4, 2, 6),
  ('Prêtre de guerre',  't14.png', 2, 2, 5, 6),
  ('Brute sacrée',      't15.png', 1, 7, 3, 4),
  ('Archimage',         't16.png', 1, 4, 7, 3);

-- id_morpion seront 1 à 16 si la table était vide.


-- ------------------------------------------------------------
-- 3) CONFIG (CONFIGURATIONS DE PARTIE) – 10 configs
--    grid_size ∈ {3,4}, max_turns > 0
-- ------------------------------------------------------------

INSERT INTO config (grid_size, max_turns) VALUES
  (3, 20),
  (3, 25),
  (3, 30),
  (4, 25),
  (4, 30),
  (3, 15),
  (4, 20),
  (3, 18),
  (4, 22),
  (3, 35);

-- id_config seront 1 à 10 si la table était vide.


-- ------------------------------------------------------------
-- 4) TEAM_MORPION – composition des équipes
--    Ici, chaque équipe a 6 morpions (entre 6 et 8 comme dans le sujet)
-- ------------------------------------------------------------

-- Équipe 1 : morpions 1,2,3,4,5,6
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6);

-- Équipe 2 : morpions 3,4,5,6,7,8
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8);

-- Équipe 3 : morpions 1,4,7,9,10,11
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (3, 1), (3, 4), (3, 7), (3, 9), (3, 10), (3, 11);

-- Équipe 4 : morpions 2,5,8,9,12,13
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (4, 2), (4, 5), (4, 8), (4, 9), (4, 12), (4, 13);

-- Équipe 5 : morpions 6,7,10,11,14,15
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (5, 6), (5, 7), (5, 10), (5, 11), (5, 14), (5, 15);

-- Équipe 6 : morpions 3,5,9,12,15,16
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (6, 3), (6, 5), (6, 9), (6, 12), (6, 15), (6, 16);

-- Équipe 7 : morpions 2,4,6,8,10,14
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (7, 2), (7, 4), (7, 6), (7, 8), (7, 10), (7, 14);

-- Équipe 8 : morpions 1,7,9,11,13,16
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (8, 1), (8, 7), (8, 9), (8, 11), (8, 13), (8, 16);

-- Équipe 9 : morpions 2,5,8,12,14,15
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (9, 2), (9, 5), (9, 8), (9, 12), (9, 14), (9, 15);

-- Équipe 10 : morpions 3,6,9,13,15,16
INSERT INTO team_morpion (team_id, morpion_id) VALUES
  (10, 3), (10, 6), (10, 9), (10, 13), (10, 15), (10, 16);


-- ------------------------------------------------------------
-- 5) GAME – 10 parties, certaines terminées, d'autres non
--    team1_id <> team2_id
--    winner_team_id ∈ {team1_id, team2_id} ou NULL
-- ------------------------------------------------------------

INSERT INTO game (team1_id, team2_id, config_id, started_at, ended_at, winner_team_id) VALUES
  (1,  2,  1, '2025-01-10 14:00:00', '2025-01-10 14:10:00', 1),  -- victoire Rouges furieux
  (3,  4,  2, '2025-01-11 15:00:00', '2025-01-11 15:20:00', 4),  -- victoire Jaunes rapides
  (5,  6,  3, '2025-01-12 16:00:00', '2025-01-12 16:30:00', 6),  -- victoire Blancs sereins
  (7,  8,  4, '2025-01-13 17:00:00', '2025-01-13 17:25:00', NULL), -- égalité
  (9, 10,  5, '2025-01-14 18:00:00', NULL,                      NULL), -- partie en cours
  (1,  3,  6, '2025-01-15 19:00:00', NULL,                      NULL),
  (2,  4,  7, '2025-01-16 20:00:00', '2025-01-16 20:40:00', 2),
  (5,  7,  8, '2025-01-17 21:00:00', '2025-01-17 21:35:00', 5),
  (6,  8,  9, '2025-01-18 22:00:00', NULL,                      NULL),
  (1, 10, 10, '2025-01-19 23:00:00', '2025-01-19 23:50:00', 10);

-- id_game seront 1 à 10 si la table était vide.


-- ------------------------------------------------------------
-- 6) LOGS_ENTRY – au moins 10 lignes de journal
--    (game_id, num) = clé primaire
-- ------------------------------------------------------------

INSERT INTO logs_entry (game_id, num, message) VALUES
  (1, 1, 'Début de la partie entre Rouges furieux et Bleus calmes'),
  (1, 2, 'Rouges furieux jouent en premier'),
  (1, 3, 'Bleus calmes placent un morpion au centre'),

  (2, 1, 'Début de la partie entre Verts agiles et Jaunes rapides'),
  (2, 2, 'Jaunes rapides prennent un avantage rapide'),
  (2, 3, 'Jaunes rapides gagnent la partie'),

  (3, 1, 'Début de la partie entre Noirs mystiques et Blancs sereins'),
  (3, 2, 'Blancs sereins défendent parfaitement'),

  (4, 1, 'Partie entre Violets électriques et Oranges ardents'),
  (4, 2, 'La partie se termine sur une égalité');

