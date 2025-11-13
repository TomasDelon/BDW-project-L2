from model.model_pg import get_attributes, query
from controleurs.includes import set_search_path

url_components = REQUEST_VARS['url_components']  # URL should be /t/<schema>/<table>, and url_components be ['t', '<schema>', '<table>']

REQUEST_VARS['current_schema'] = None  # devrait être dans une variable liée à la request (et pas en session)
REQUEST_VARS['current_table'] = None  # idem
if len(url_components) < 3:  # missing a schema component
    REQUEST_VARS['message'] = "Erreur : URL invalide (devrait être de la forme /t/<schema>/<table>)."
    REQUEST_VARS['message_class'] = "error"
elif url_components[1] not in SESSION['schemas']:  # schema does not exist
    REQUEST_VARS['message'] = f"Erreur : le schéma {url_components[1]} n'existe pas !"
    REQUEST_VARS['message_class'] = "error"
elif url_components[2] not in SESSION['schema_to_tables'][url_components[1]]:  # table does not exist
    REQUEST_VARS['message'] = f"Erreur : la table {url_components[2]} n'existe pas dans le schéma {url_components[1]} !"
    REQUEST_VARS['message_class'] = "error"
else:  # update relational schema of the schema
    REQUEST_VARS['current_schema'] = url_components[1]
    REQUEST_VARS['current_table'] = url_components[2]
    if REQUEST_VARS['current_schema'] not in SESSION['schemas_to_tables_to_atts']:
        SESSION['schemas_to_tables_to_atts'][REQUEST_VARS['current_schema']] = dict()
    for tab in SESSION['schema_to_tables'][REQUEST_VARS['current_schema']]:  # update list of attributes for each table of schema 
        atts = get_attributes(SESSION['CONNEXION'], REQUEST_VARS['current_schema'], tab)
        SESSION['schemas_to_tables_to_atts'][REQUEST_VARS['current_schema']][tab] = atts.result_instances
    # mise à jour du search_path (réordonnancement et update en BD)
    SESSION['search_path'] = set_search_path(SESSION["CONNEXION"], SESSION['schemas'], REQUEST_VARS['current_schema'])
    # récupération des instances de la table courante
    REQUEST_VARS['query_result'] = query(SESSION['CONNEXION'], f"select * from {REQUEST_VARS['current_table']}")
