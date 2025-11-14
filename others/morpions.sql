create table team (
  id_team     serial primary key,
  name        varchar(80)  not null,
  color       varchar(40)  not null,
  created_at  date         not null default current_date,  
  unique (name, color)
);

create table morpion (
  id_morpion  serial primary key,
  name        varchar(80)  not null,
  image_url   varchar(255) not null, -- default 'not_find_img.png',
  hp         integer not null default 1 check (hp >= 0),
  attack     integer not null default 1 check (attack >= 0),
  mana       integer not null default 1 check (mana >= 0),
  accuracy   integer not null default 1 check (accuracy >= 0),
  -- les defaults et la contrainte de la somme sont compatibles ????
  check (hp + attack + mana + accuracy = 15)
);

-- Association N-N: une équipe ne peut pas avoir deux fois le même morpion
create table team_morpion (
  team_id     integer not null references team(id_team),
  morpion_id  integer not null references morpion(id_morpion) on delete restrict,
  primary key (team_id, morpion_id)
);


create table config (
  id_config   serial primary key,
  created_at  timestamp not null,
  grid_size   integer   not null check (grid_size in (3,4)),
  max_turns   integer   check(max_turns > 0)
);

create table game (
  id_game           serial primary key,
  team1_id          integer not null references team(id_team) on delete restrict,
  team2_id          integer not null references team(id_team) on delete restrict,
  configuration_id  integer not null references config(id_config) on delete restrict,
  started_at        timestamp not null,
  ended_at          timestamp,
  winner_team_id    integer references team(id_team) on delete set null,
  check (team1_id <> team2_id),
  check (
    winner_team_id is null
    or winner_team_id = team1_id
    or winner_team_id = team2_id
  )
);

create table logs_entry (
  game_id     integer   not null references game(id_game) on delete cascade,
  num         integer   not null check (num > 0),
  created_at  timestamp not null,
  message     text      not null,
  primary key (game_id, num)
);

---------------------------------



-- On supprime d'abord les tables si elles existent déjà, pour pouvoir rejouer le script proprement
drop table if exists logs_entry cascade; -- le journal dépend de game, donc on supprime en premier
drop table if exists game cascade;       -- une partie dépend des équipes et des configurations
drop table if exists team_morpion cascade; -- table d'association N-N entre équipe et morpion
drop table if exists config cascade;     -- table des configurations de partie (grille, tours max)
drop table if exists morpion cascade;    -- table des modèles de morpions
drop table if exists team cascade;       -- table des équipes

-- =====================================================================
-- Table TEAM : "Une équipe possède un nom, une couleur unique, une date
-- de création" (section 1 du sujet).
-- =====================================================================
create table team (                                             -- table qui représente les équipes de morpions
  id_team    serial primary key,                                -- identifiant technique unique de l’équipe (clé primaire, plus pratique que le nom)
  name       varchar(80)  not null,                            -- nom de l’équipe, comme indiqué dans les spécifications
  color      varchar(40)  not null,                            -- couleur de l’équipe, utilisée pour la distinguer visuellement
  created_at date         not null default current_date,        -- date de création de l’équipe, valeur par défaut = aujourd’hui (cf. sujet)
  constraint uq_team_color unique (color)                       -- on impose qu’une couleur ne soit utilisée que par une seule équipe (couleur unique)
);

-- =====================================================================
-- Table MORPION : "un morpion possède un nom, une image, des points de
-- vie, d’attaque, de mana, de réussite" et "la somme vaut 15" (section 1).
-- =====================================================================
create table morpion (                                          -- table des modèles de morpions (templates) réutilisables par plusieurs équipes
  id_morpion serial primary key,                                -- identifiant technique unique du morpion (clé primaire)
  name       varchar(80)  not null,                            -- nom du morpion, utile pour les interfaces et les sélections
  image_url  varchar(255) not null,                            -- chemin vers l’image fournie dans le projet (cf. consigne d’utiliser les images)
  hp         integer     not null check (hp      >= 1),         -- points de vie, au moins 1 comme indiqué ("au minimum 1 point")
  attack     integer     not null check (attack  >= 1),         -- points d’attaque, au moins 1
  mana       integer     not null check (mana    >= 1),         -- points de mana, au moins 1
  accuracy   integer     not null check (accuracy >= 1),        -- points de réussite, au moins 1 (sert à calculer la probabilité de réussite)
  check (hp + attack + mana + accuracy = 15)                    -- contrainte qui impose que la somme des 4 caractéristiques vaut 15 (paramètre par défaut du sujet)
  -- Remarque : ici on stocke les caractéristiques de base (template) ; les valeurs qui évoluent en partie seront gérées côté application.
);

-- =====================================================================
-- Table TEAM_MORPION : liaison N-N "un morpion peut faire partie de
-- plusieurs équipes" et "une équipe possède entre 6 et 8 morpions".
-- =====================================================================
create table team_morpion (                                     -- table d’association entre une équipe et ses modèles de morpions
  team_id    integer not null references team(id_team)          -- clé étrangère vers l’équipe, car une équipe est composée de morpions
             on delete restrict,                                -- on interdit la suppression d’une équipe si elle est encore utilisée dans des compositions
  morpion_id integer not null references morpion(id_morpion)    -- clé étrangère vers le modèle de morpion
             on delete restrict,                                -- on interdit la suppression d’un morpion si des équipes l’utilisent encore
  primary key (team_id, morpion_id)                             -- clé primaire composée : un même morpion ne peut apparaître qu’une fois dans une équipe
  -- Remarque : la contrainte "entre 6 et 8 morpions par équipe" est globale,
  -- elle se vérifiera via des requêtes SQL ou des triggers, plutôt que par une simple contrainte CHECK.
);

-- =====================================================================
-- Table CONFIG : "Une partie utilise une configuration datée, qui stocke
-- taille de la grille et nombre maximal de tours" (section 1).
-- =====================================================================
create table config (                                           -- table des configurations de partie
  id_config  serial    primary key,                             -- identifiant technique unique de la configuration
  created_at timestamp not null default current_timestamp,      -- date et heure de création de cette configuration (configuration datée)
  grid_size  integer   not null check (grid_size in (3, 4)),    -- taille de la grille, limitée à 3x3 ou 4x4 comme dans les règles du sujet
  max_turns  integer   not null check (max_turns > 0)           -- nombre maximal de tours, strictement positif (la partie s’arrête quand ce nombre est atteint)
  -- On pourrait ajouter plus tard d’autres paramètres (par ex. total de points = 15) si on veut les rendre configurables.
);

-- =====================================================================
-- Table GAME : "Une partie oppose deux équipes, on stocke ses dates de
-- début et de fin, et l’équipe gagnante" + configuration utilisée.
-- =====================================================================
create table game (                                             -- table qui représente une partie jouée entre deux équipes
  id_game        serial    primary key,                         -- identifiant technique unique de la partie
  team1_id       integer   not null references team(id_team)    -- première équipe, cf. "une partie oppose deux équipes"
                 on delete restrict,                            -- on empêche de supprimer une équipe qui a servi dans une partie
  team2_id       integer   not null references team(id_team)    -- deuxième équipe, opposée à la première
                 on delete restrict,                            -- même logique que pour team1_id
  config_id      integer   not null references config(id_config) -- configuration de la partie (taille de grille, nombre max de tours)
                 on delete restrict,                            -- on ne supprime pas une configuration utilisée par une partie
  started_at     timestamp not null default current_timestamp,  -- date/heure de début de la partie (stockée comme demandé dans le sujet)
  ended_at       timestamp,                                     -- date/heure de fin de la partie, nulle si la partie est en cours
  winner_team_id integer references team(id_team)               -- équipe gagnante éventuelle (peut être nulle si égalité ou partie non terminée)
                 on delete set null,                            -- si une équipe gagnante est supprimée, on garde l’historique de la partie mais sans gagnant
  check (team1_id <> team2_id),                                 -- on interdit qu’une partie oppose deux fois la même équipe
  check (                                                   
    winner_team_id is null                                      
    or winner_team_id = team1_id                                
    or winner_team_id = team2_id                                
  )
  -- Cette structure permet plus tard de calculer les statistiques demandées :
  -- top-3 des équipes avec le plus de victoires, durée des parties, etc.
);

-- =====================================================================
-- Table LOGS_ENTRY : "journal qui liste toutes les actions réalisées.
-- Chaque ligne est identifiée par un numéro unique au niveau de la partie,
-- datée, avec un texte décrivant l’action" (section 1).
-- =====================================================================
create table logs_entry (                                       -- table du journal des actions effectuées pendant une partie
  game_id    integer   not null references game(id_game)        -- chaque ligne appartient à une partie donnée
             on delete cascade,                                 -- si on supprime une partie, on supprime aussi toutes ses lignes de journal
  num        integer   not null check (num > 0),                -- numéro d’ordre de la ligne dans la partie, strictement positif
  created_at timestamp not null default current_timestamp,      -- horodatage de l’action, comme demandé ("Chaque ligne est datée")
  message    text      not null,                               -- description textuelle de l’action réalisée (attaque, sort, placement, etc.)
  primary key (game_id, num)                                    -- la combinaison (id de partie, numéro) est unique, comme dans le sujet
);

-- =====================================================================
-- INSERTS D’EXEMPLE : "insérez quelques instances fictives" (section 1).
-- =====================================================================

-- On insère quelques modèles de morpions avec des répartitions différentes de points
insert into morpion (name, image_url, hp, attack, mana, accuracy)  -- insertion de 4 modèles de morpions de base
values
  ('Tanky',   'img/morpions/tanky.png',   8, 3, 2, 2),             -- morpion axé points de vie (tank)
  ('Mage',    'img/morpions/mage.png',    3, 2, 7, 3),             -- morpion spécialisé dans les sorts (beaucoup de mana)
  ('Assassin','img/morpions/assassin.png',4, 7, 1, 3),             -- morpion très offensif (attaque élevée)
  ('Support', 'img/morpions/support.png', 5, 1, 5, 4);             -- morpion orienté soutien (bonne réussite et mana)

-- On insère deux équipes avec des couleurs différentes (couleur unique)
insert into team (name, color)                                    -- insertion de deux équipes jouables
values
  ('Verts furieux',  'green'),                                    -- première équipe, associée à la couleur verte
  ('Rouges sournois','red');                                      -- deuxième équipe, associée à la couleur rouge

-- On crée deux configurations : une pour 3x3, une pour 4x4
insert into config (grid_size, max_turns)                         -- insertion de configurations de partie
values
  (3, 20),                                                        -- configuration pour une grille 3x3 avec 20 tours maximum
  (4, 30);                                                        -- configuration pour une grille 4x4 avec 30 tours maximum

-- Pour associer des morpions aux équipes, on utilise les identifiants auto-générés
-- (on suppose ici que les id_team sont 1 et 2, et les id_morpion de 1 à 4, ce qui est vrai dans un schéma vide)
insert into team_morpion (team_id, morpion_id)                    -- association des morpions à l’équipe "Verts furieux"
values
  (1, 1),                                                         -- équipe 1 utilise le morpion Tanky
  (1, 2),                                                         -- équipe 1 utilise le morpion Mage
  (1, 3),                                                         -- équipe 1 utilise le morpion Assassin
  (1, 4);                                                         -- équipe 1 utilise le morpion Support
-- Remarque : en pratique, il faudra ajouter suffisamment de morpions pour atteindre 6 à 8 par équipe.

insert into team_morpion (team_id, morpion_id)                    -- association des morpions à l’équipe "Rouges sournois"
values
  (2, 1),                                                         -- équipe 2 réutilise le morpion Tanky (un modèle peut appartenir à plusieurs équipes)
  (2, 3),                                                         -- équipe 2 réutilise le morpion Assassin
  (2, 4);                                                         -- équipe 2 réutilise le morpion Support

-- On crée une partie exemple entre les deux équipes avec la configuration 3x3
insert into game (team1_id, team2_id, config_id, started_at, ended_at, winner_team_id) -- insertion d’une partie jouée
values
  (1, 2, 1, current_timestamp - interval '5 minutes', current_timestamp, 1);          -- partie de test où l’équipe 1 gagne après 5 minutes

-- Enfin, on journalise quelques actions fictives pour cette partie
insert into logs_entry (game_id, num, created_at, message)        -- première action de la partie 1
values
  (1, 1, current_timestamp - interval '4 minutes', 'L''équipe verte place un morpion Tanky au centre.');

insert into logs_entry (game_id, num, created_at, message)        -- deuxième action de la partie 1
values
  (1, 2, current_timestamp - interval '3 minutes', 'L''équipe rouge place un morpion Assassin en haut à gauche.');

insert into logs_entry (game_id, num, created_at, message)        -- troisième action de la partie 1
values
  (1, 3, current_timestamp - interval '2 minutes', 'Tanky attaque l''Assassin et lui inflige 3 points de dégâts.');

insert into logs_entry (game_id, num, created_at, message)        -- quatrième action de la partie 1 (fin de partie)
values
  (1, 4, current_timestamp - interval '1 minutes', 'L''équipe verte aligne trois morpions et gagne la partie.');
