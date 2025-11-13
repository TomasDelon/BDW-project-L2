"""
Ficher includes contenant des fonctions utilisées par plusieurs controleurs
"""

from model.model_pg import get_schemas, get_tables, update_search_path, query
from logzero import logger


def process_query(connexion, sql_query):
    """
    Execute a query directly and checks its output for setting relevant message in REQUEST_VARS
    sql_query: string representing the SQL query to be executed
    """
    result = query(connexion, sql_query)
    if result.error_code:
        message = f"Erreur {result.error_code} : {result.error_message}"  # {result.error_detail}
        message_class = "error"
    elif result.is_select_query:  # requete SELECT ou SET avec des instances en résultat
        message = f"Requête exécutée avec succès : { len(result.result_instances) } instance(s) résultat."
        message_class = "success"
    else:  # requete DELETE/UPDATE/INSERT/... avec un nombre de tuples affectés
        message = f"Requête exécutée avec succès : { result.result_affected_rows } instance(s) affectée(s)."
        message_class = "success"
    return result, message, message_class


def add_query_to_session(old_queries, sql_query):
    """
    Add a submitted query directly into session (SESSION['old_queries'])
    sql_query: string representing the SQL query to be added
    """
    if sql_query in old_queries:  # avoid duplicates in logged queries
        old_queries.remove(sql_query)  # delete so that query becomes most recent
    old_queries.append(sql_query)
    return old_queries


def get_schema_list(connexion):
    """
    Get the list of schemas given the database connection
    connexion: database connection link
    Returns: a list of schema names
    """
    schema_tuples = get_schemas(connexion)
    schemas = [_[0] for _ in schema_tuples.result_instances]
    logger.info(f"Schemas : {schemas}")
    return schemas

    
def get_tables_per_schema(connexion, schemas):
    """
    Build a dictionary of schemas and their tables list such as {schema1: [table1, table2, ...], schema2: [...]}
    connexion: database connection link
    schemas: list of schemas
    Returns: a dict of lists
    """
    tables_per_schema = dict()
    for sch in schemas:  # get tables for each schema
        tables = [_[0] for _ in get_tables(connexion, sch).result_instances]
        tables_per_schema[sch] = tables
    return tables_per_schema


def reorder_search_path(schemas, current_schema):
    """
    Re-order the list of schemas so that the first one is the current schema.
    schemas: list of schemas
    current_schema : selected current schema
    Returns: a list of schema names
    """
    if current_schema:
        if current_schema in schemas:
            schemas.remove(current_schema)  # supprimer current_schema de la liste
        schemas.insert(0, current_schema)  # insérer current_schema en début de liste
    return schemas


def set_search_path(connexion, schemas, current_schema=None):
    """
    Re-order the list of schemas so that the first one is the current schema and update search_path in the database.
    connexion: database connection link
    schemas: list of schemas
    current_schema : selected current schema
    Returns: a list of schema names
    """
    new_search_path = reorder_search_path(schemas, current_schema)
    update_search_path(connexion, new_search_path)
    return new_search_path
