"""
Ficher initialisation (eg, constantes chargées au démarrage dans la session)
"""

from datetime import datetime
from controleurs.includes import get_schema_list, get_tables_per_schema, set_search_path

SESSION['APP'] = "BIPS"
SESSION['BASELINE'] = "Basic Interface for PostgreSQL"
SESSION['CURRENT_YEAR'] = datetime.now().year
SESSION['old_queries'] = list()

SESSION['schemas'] = get_schema_list(SESSION['CONNEXION']) # list of schemas
SESSION['search_path'] = set_search_path(SESSION['CONNEXION'], SESSION['schemas'])
# SESSION['schema_to_tables'] = list of tables per schema {'schema1': [table1, table2, ...], 'schema2': [...], ...}
SESSION['schema_to_tables'] = get_tables_per_schema(SESSION['CONNEXION'], SESSION['schemas'])
SESSION['nb_tables_user'] = sum([len(_) for _ in SESSION['schema_to_tables'].values()])

# SESSION['schemas_to_tables_to_atts'] = list of attributes per table and per schema, such as {'schema1': {table1: [atts], table2:[atts], ...}, 'schema2': ...} with atts = [(nom_att, type_att, 'PRIMARY KEY|FOREIGN KEY'), (...), ...]
SESSION['schemas_to_tables_to_atts'] = dict()  
