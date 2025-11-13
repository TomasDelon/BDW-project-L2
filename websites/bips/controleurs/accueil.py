from controleurs.includes import get_schema_list, get_tables_per_schema

# checking if a refresh (of schemas list) is needed
if 'bouton-refresh' in POST:
    SESSION['schemas'] = get_schema_list(SESSION['CONNEXION']) # list of schemas
    SESSION['schema_to_tables'] = get_tables_per_schema(SESSION['CONNEXION'], SESSION['schemas'])
    SESSION['nb_tables_user'] = sum([len(_) for _ in SESSION['schema_to_tables'].values()])
    SESSION['schemas_to_tables_to_atts'] = dict() # reinitalize list of attributes in each schema
    REQUEST_VARS['message'] = "La liste des schémas a bien été mise à jour."
    REQUEST_VARS['message_class'] = "success"

