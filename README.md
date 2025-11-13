# bdw-server

Serveur HTTP pour la programmation de site web *en local* (ne pas utiliser en production).
Fonctionnalités :

- exposition d'un répertoire `<directory>` contenant un site programmé selon l'architecture MVC (Model Vue Controleur)
- connexion au SGBD PostgreSQL (avec un fichier de configuration, par défaut `config-bd.toml`)
- routage (simplifié, avec un fichier de routes en TOML, par défaut `<directory>/routes.toml`)
- gestion des commandes GET et POST
- système de templates (Jinja)
- session pour conserver des informations pendant la navigation


Résumé pour démarrer le serveur :
```sh
# activer l'environnement virtuel (déjà créé)
source .venv/bin/activate  # ou .venv\Scripts\activate sous windows
# lancer le serveur avec le paramètre DIRECTORY qui contient votre site web
python server.py DIRECTORY
# si tout est ok, aller sur http://localhost:4242/ (URL par défaut)
```

## Installation

Si besoin, [installez Python](https://www.python.org/). Il faut a-minima la version 3.11.2 de python.
Lors de la première utilisation, il faut créer un environnement virtuel Python et installer les packages nécessaires.
Par la suite, il suffit d'activer votre environnement virtuel et de lancer le serveur sur le répertoire contenant votre site.

### Environnement virtuel Python

Il est nécessaire de créer un environnement virtuel Python pour lancer
l'application. Cela peut se faire via la commande suivante (pour créer
l'environnement dans le répertoire `.venv`) :

```sh
python3 -m venv .venv
```

Pour activer cet environnement dans votre shell :

```sh
source .venv/bin/activate  # sous linux, macos
.venv\Scripts\activate  # sous windows
```

Il faut installer les dépendances du projet, dans un shell où l'environnement
virtuel est activé, faire :

```sh
# python3.11 -m ensurepip  # si pip non disponible avec python
pip install --upgrade pip  # au moins la version 20.3 de pip
pip install -r requirements.in
```

Cette étape n'est à faire qu'une seule fois normalement.

## Utilisation

Le serveur permet d'exposer un site web dans un répertoire. En général, les sites sont placés dans le répertoire `websites`.

> Les sites web utilisant le serveur doivent être dans un sous-répertoire de `bdw-server` (et pas en dehors). Cela permet d'éviter les [attaques de type directory traversal](https://en.wikipedia.org/wiki/Directory_traversal_attack) 

### Démarrer le serveur 

Si besoin, activer l'environnement virtuel :
```sh
source .venv/bin/activate  # .venv\Scripts\activate sous Windows
```

Démarrer le serveur en indiquant le nom du sous-répertoire contenant votre site web :
```sh
python server.py <repertoire_de_votre_site>
```

Si tout s'est bien passé, vous devriez voir [http://localhost:4242](l'interface suivante) :

![Démarrage du serveur](screenshot-server.png)

Le site est exposé à l'URL indiquée (port par défaut) : [http://localhost:4242](http://localhost:4242)

### Lancement du site démo serial_critique

Le site se trouve dans `websites/serial_critique`. Pour lancer le site serial-critique :

```sh
python server.py websites/serial_critique
```

### Lancement de bips

Le site se trouve dans `websites/bips`. BIPS permet de se connecter à une BD PostgreSQL (comme pgweb, DBeaver, ou pgAdmin).

```sh
python server.py websites/bips
```


### Options

Liste des options du serveur :

* -b, --boilerplate : création d'un nouveau site (création du répertoire <directory> et de ses sous-répertoires)
* -c, --config : chemin vers un fichier de configuration (par défaut, `config.toml`)
* -i, --init : chemin vers le fichier d'initialisation (par défaut, <directory>/init.py)
* -p, --port : numéro de port (par défaut, 4242)
* -r, --routes : chemin vers le fichier de routage (par défaut, <directory>/routes.toml)
* -t, --templates : chemin vers un autre répertoire de templates (par défaut, <directory>/templates/)
* -s, --schema : nom du schéma de la base de données (remplace le nom fourni dans le fichier de configuration)

## Contact

Fabien Duchateau (Université Claude Bernard Lyon 1), <prénom.nom@univ-lyon1.fr>

