"""
Contrôleur de la page d'accueil (fonctionnalité 1).
Récupère les statistiques nécessaires à l'affichage.
"""

from model.model_pg import get_functionality_one_stats

REQUEST_VARS.setdefault('message', None)
REQUEST_VARS.setdefault('message_class', None)

stats = get_functionality_one_stats(
    SESSION["CONNEXION"],
    table_names=["team", "morpion", "game"],
    top_limit=3,
)

REQUEST_VARS["stats"] = stats