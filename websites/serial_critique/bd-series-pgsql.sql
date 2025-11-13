DROP SCHEMA IF EXISTS series CASCADE;
CREATE SCHEMA IF NOT EXISTS series;
SET search_path TO series;

/* Creating tables */ 

CREATE TABLE SERIES (
  nomsérie VARCHAR(42),
  PRIMARY KEY (nomsérie)
);

CREATE TABLE SAISONS (
  idsaison INTEGER,
  datelancement DATE,
  nomsérie VARCHAR(42),
  PRIMARY KEY (idsaison)
);

CREATE TABLE ACTRICES (
  numinsee INTEGER,
  nom VARCHAR(42),
  prénom VARCHAR(42),
  PRIMARY KEY (numinsee)
);

CREATE TABLE JOUER (
  idsaison INTEGER,
  numéro INTEGER,
  numinsee INTEGER,
  salaire REAL,
  PRIMARY KEY (idsaison, numéro, numinsee)
);

CREATE TABLE EPISODES (
  idsaison INTEGER,
  numéro INTEGER,
  titre VARCHAR(100),
  PRIMARY KEY (idsaison, numéro)
);

CREATE TABLE CRITIQUES ( 
  idcritique SERIAL NOT NULL, 
  datecritique TIMESTAMP,
  pseudo VARCHAR(42),
  texte VARCHAR(255),
  nomsérie VARCHAR(42) REFERENCES SERIES(nomsérie), 
  PRIMARY KEY(idcritique)
);

ALTER TABLE SAISONS ADD FOREIGN KEY (nomsérie) REFERENCES SERIES (nomsérie);
ALTER TABLE JOUER ADD FOREIGN KEY (numinsee) REFERENCES ACTRICES (numinsee);
ALTER TABLE JOUER ADD FOREIGN KEY (idsaison, numéro) REFERENCES EPISODES (idsaison, numéro);
ALTER TABLE EPISODES ADD FOREIGN KEY (idsaison) REFERENCES SAISONS (idsaison);

/* Inserting instances */ 
 
INSERT INTO SERIES VALUES('The Big Bang Theory');
INSERT INTO SERIES VALUES('Game of Thrones');
INSERT INTO SERIES VALUES('Breaking Bad');
INSERT INTO SERIES VALUES('The Wire');
INSERT INTO SERIES VALUES('Black Clover');
INSERT INTO SERIES VALUES('The 100');
INSERT INTO SERIES VALUES('Kaamelott');
INSERT INTO SAISONS VALUES(1, '2011-09-22', 'The Big Bang Theory');
INSERT INTO SAISONS VALUES(2, '2012-09-27', 'The Big Bang Theory');
INSERT INTO SAISONS VALUES(3, '2011-04-17', 'Game of Thrones');
INSERT INTO SAISONS VALUES(4, '2014-03-19', 'The 100');
INSERT INTO SAISONS VALUES(5, '2005-03-01', 'Kaamelott');
INSERT INTO EPISODES VALUES(1, 1, 'The Skank Reflex Analysis');
INSERT INTO EPISODES VALUES(2, 1, 'The Date Night Variable');
INSERT INTO EPISODES VALUES(3, 1, 'Winter is coming');
INSERT INTO EPISODES VALUES(3, 2, 'The Kingsroad');
INSERT INTO EPISODES VALUES(4, 1, 'Pilot');
INSERT INTO EPISODES VALUES(5, 3, 'La Table de Breccan');
INSERT INTO ACTRICES VALUES(111, 'Bean', 'Sean');
INSERT INTO ACTRICES VALUES(222, 'Fairley', 'Michelle');
INSERT INTO ACTRICES VALUES(333, 'Cuoco', 'Kaley');
INSERT INTO ACTRICES VALUES(444, 'Parsons', 'Jims');
INSERT INTO ACTRICES VALUES(555, 'Avgeropoulos', 'Marie');
INSERT INTO JOUER VALUES(1, 1, 333, 3200);
INSERT INTO JOUER VALUES(1, 1, 444, 3200);
INSERT INTO JOUER VALUES(2, 1, 333, 3200);
INSERT INTO JOUER VALUES(3, 1, 111, 8437);
INSERT INTO JOUER VALUES(3, 1, 222, 6000);
INSERT INTO JOUER VALUES(3, 2, 111, NULL);
INSERT INTO JOUER VALUES(3, 2, 222, 6000);
INSERT INTO CRITIQUES(datecritique, pseudo, texte, nomsérie) VALUES('2012-02-05 22:03:54', 'user12345', 'Une super série !', 'The Big Bang Theory');
INSERT INTO CRITIQUES(datecritique, pseudo, texte, nomsérie) VALUES('2016-11-25 15:42:06', 'welshman', 'j kiff tro daeneris !!!!! :) 8)', 'Game of Thrones');
INSERT INTO CRITIQUES(datecritique, pseudo, texte, nomsérie) VALUES('2019-02-02 21:33:36', 'fan2100', 'vivement la prochaine saison !', 'The 100');
INSERT INTO CRITIQUES(datecritique, pseudo, texte, nomsérie) VALUES('2020-12-27 12:43:01', 'user12345', 'Encore 6 mois avant le film !', 'Kaamelott');

