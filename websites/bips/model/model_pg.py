import psycopg
from model.query_result import query_result
from logzero import logger

def get_schemas(connection):
    """
    Get the list of schemas in current database.

    Returns: a query_result object containing the list of schema names
    """
    sql_query = """select s.nspname as table_schema
            from pg_catalog.pg_namespace s join pg_catalog.pg_user u on u.usesysid = s.nspowner
            where nspname not in ('information_schema', 'pg_catalog') and nspname not like 'pg_toast%%'
            and nspname not like 'pg_temp_%%'
            order by table_schema;"""  # double percent symbol to avoid conflict with params symbol
    return query(connection, sql_query)

def update_search_path(connection, schemas):
    """
    Update search path (ordered list of schemas in which tables are searched).
    schemas: list of schemas representing the search path

    Returns: a query_result object
    """
    sql_query = 'SET search_path = ' + str(','.join(schemas))
    return query(connection, sql_query)

def get_tables(connection, schema=None):
    """
    Get the list of tables in current database or in the provided schema.

    Returns: a query_result object containing a list of table names
    """
    sql_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
    if schema:
        sql_query += f" AND schemaname = '{schema}'"
    return query(connection, sql_query)

def get_attributes(connection, schema, table_name):
    """
    Get the list of attributes in given table_name inside given schema.

    Returns: a query_result object containing a list of attributes with attribute name, data type, and a string with PRIMARY and/or FOREIGN key constraints
    """
    # information_schema is simpler and more portative, but slower
    # pg_catalog is faster, but less portative and requires specific privileges to access it
    sql_query = f"""select column_name, data_type,  COALESCE(string_agg(constraint_type, ','), '') AS types_constraint
    from information_schema.columns col
    left join information_schema.key_column_usage using(table_schema, table_name, column_name)
    left join information_schema.table_constraints using (table_schema, table_name, constraint_name)
    where col.table_schema='{schema}' and col.table_name='{table_name}'
    group by column_name, data_type, col.ordinal_position 
    order by col.ordinal_position;
    """
    return query(connection, sql_query)

def query(connection, sql_query, params=()):
    """
    Execute a SQL query sql on the given connection using optional params.
    The optional parameter return_attributes indicates whether the attributes of the query are returned (as first row) or not.

    Returns: a query_result object containing the result of the query (list of instances, nb of affected rows or error)
    """
    qr = query_result(sql_query, params)
    sql_query = sql_query.replace('%', '%%')  # % is a special character, need escaping bu doubling the symbol
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql_query, params)
            qr.statusmessage = cursor.statusmessage
            qr.full_query = cursor._query
            if sql_query.lower().startswith("select") or sql_query.lower().startswith("show"):  # SELECT or SHOW query
                qr.result_instances = cursor.fetchall()
                qr.result_attributes = tuple([_[0]  for _ in cursor.description])
            else:  # INSERT / DELETE / UPDATE query, returns the number of affected rows
                qr.is_select_query = False
                qr.result_affected_rows = cursor.rowcount
        except psycopg.Error as e:
            qr.error_code = e.diag.sqlstate
            qr.error_message = e.diag.message_primary
            qr.error_type = e.diag.severity
            qr.error_detail = e.diag.message_detail
            logger.exception(e)
    return qr

def disconnect(connection):
    """
    Close the database connection

    Returns: True
    """
    connection.close()
    return True
