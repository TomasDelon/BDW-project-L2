from model.model_pg import get_instances, get_episodes_for_num
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "affichage des données")

# récupérer les séries
REQUEST_VARS['series'] = get_instances(SESSION['CONNEXION'], 'series')

# récupérer les actrices
REQUEST_VARS['actrices'] = get_instances(SESSION['CONNEXION'], 'actrices')

"""
À vous de jouer : lister les critiques en vous inspirant du code ci-dessus.
Vous pourrez plus tard améliorer le code en affichant chaque série avec les
critiques qui la concernent !
"""

# récupérer les épisodes 1 et 2
REQUEST_VARS['episodes1'] = get_episodes_for_num(SESSION['CONNEXION'], 1)
REQUEST_VARS['episodes2'] = get_episodes_for_num(SESSION['CONNEXION'], 2)

