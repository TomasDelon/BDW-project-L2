"""
Gère la déconnexion de l'utilisateur (fermeture connexion SGBD, suppression session)
"""

from model.model_pg import disconnect

if "CONNEXION" in SESSION:  # déconnexion de la BD
    disconnect(SESSION["CONNEXION"])

# suppression de la session
SESSION.clear()
SESSION = None

