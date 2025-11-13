from model.model_pg import query
from controleurs.includes import add_query_to_session, process_query


if 'requete_sql' in POST:  # formulaire soumis
    sql_query = POST['requete_sql'][0]  # first element because HTML names are not unique
    SESSION['old_queries'] = add_query_to_session(SESSION['old_queries'], sql_query)
    REQUEST_VARS['query_result'], REQUEST_VARS['message'], REQUEST_VARS['message_class'] = process_query(SESSION['CONNEXION'], sql_query)

