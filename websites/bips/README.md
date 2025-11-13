# Basic Interface for PostgreSQL (BIPS)

Interface web minimaliste pour les TP SQL en BDW.

Prérequis : installer le serveur `bdw-server` (voir page de l'UE).

Résumé pour démarrer BIPS :
```sh
# activer l'environnement virtuel (déjà créé) dans bdw-server/
source .venv/bin/activate  # ou .venv\Scripts\activate sous windows
# lancer le serveur avec le paramètre DIRECTORY qui contient votre site web
python server.py bips
# si tout est ok, aller sur http://localhost:4242/ (URL par défaut)
```

## Utilisation

Lors de la première utilisation, il faut créer un environnement virtuel Python et installer le serveur `bdw-server`.

### Installer le serveur bdw-server

Voir la page BDW.

### Installer BIPS

Téléchargez l'archive de BIPS sur [https://perso.liris.cnrs.fr/fabien.duchateau/bdw](la page BDW).

Extrayez le contenu de l'archive : un répertoire `bips/` devrait apparaitre. Placez ce répertoire `bips` dans le répertoire `bdw-server/`.

Ces 2 étapes (installer serveur et BIPS) ne sont à faire que la première fois.

### Démarrer BIPS 

Ouvrir un terminal et allez dans le répertoire `bdw-server/`.

```
source .venv/bin/activate
python server.py bips
```

Si tout s'est bien passé, vous devriez voir [http://localhost:4242](l'interface suivante) :

![Démarrage du serveur](screenshot-server.png)

## Contact

Fabien Duchateau (Université Claude Bernard Lyon 1), <prénom.nom@univ-lyon1.fr>

