from model.model_pg import get_attributes, query
from controleurs.includes import set_search_path, add_query_to_session, process_query

url_components = REQUEST_VARS['url_components']  # URL should be /s/<schema>, and url_components be ['s', '<schema>']

if len(url_components) < 2:  # missing a schema component
    REQUEST_VARS['message'] = "Erreur : URL invalide (devrait être de la forme /s/<schema>)."
    REQUEST_VARS['message_class'] = "error"
elif url_components[1] not in SESSION['schemas']:  # schema does not exist
    REQUEST_VARS['message'] = f"Erreur : le schéma {url_components[1]} n'existe pas !"
    REQUEST_VARS['message_class'] = "error"
else:  # update relational schema of the schema (if not existing)
    REQUEST_VARS['current_schema'] = url_components[1]
    if REQUEST_VARS['current_schema'] not in SESSION['schemas_to_tables_to_atts']:
        SESSION['schemas_to_tables_to_atts'][REQUEST_VARS['current_schema']] = dict()
    for tab in SESSION['schema_to_tables'][REQUEST_VARS['current_schema']]:  # update list of attributes for each table of schema 
        atts = get_attributes(SESSION['CONNEXION'], REQUEST_VARS['current_schema'], tab)
        SESSION['schemas_to_tables_to_atts'][REQUEST_VARS['current_schema']][tab] = atts.result_instances
    # mise à jour du search_path (réordonnancement et update en BD)
    SESSION['search_path'] = set_search_path(SESSION["CONNEXION"], SESSION['schemas'], REQUEST_VARS['current_schema'])


if 'requete_sql' in POST:  # formulaire soumis
    sql_query = POST['requete_sql'][0]  # first element because HTML names are not unique
    SESSION['old_queries'] = add_query_to_session(SESSION['old_queries'], sql_query)
    REQUEST_VARS['query_result'], REQUEST_VARS['message'], REQUEST_VARS['message_class'] = process_query(SESSION['CONNEXION'], sql_query)


