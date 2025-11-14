import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from logzero import logger

# ---------------------------------------------------------------------
# Fonctions génériques
# ---------------------------------------------------------------------

def execute_select_query(connexion, query, params=[]):
    """
    Méthode générique pour exécuter une requête SELECT (qui peut retourner
    plusieurs instances).
    Retourne une liste de tuples.
    """
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except psycopg.Error as e:
            logger.error(e)
    return None


def execute_other_query(connexion, query, params=[]):
    """
    Méthode générique pour exécuter une requête INSERT, UPDATE, DELETE.
    Retourne le nombre de lignes affectées, ou None en cas d'erreur.
    """
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query, params)
            result = cursor.rowcount
            return result
        except psycopg.Error as e:
            logger.error(e)
    return None


def get_instances(connexion, nom_table):
    """
    Retourne toutes les instances de la table nom_table.
    String nom_table : nom de la table.
    Résultat : liste de tuples.
    """
    query = sql.SQL("SELECT * FROM {table}").format(
        table=sql.Identifier(nom_table),
    )
    return execute_select_query(connexion, query)


def count_instances(connexion, nom_table):
    """
    Retourne le nombre d'instances de la table nom_table.
    String nom_table : nom de la table.
    Résultat : entier (0 si problème).
    """
    query = sql.SQL("SELECT COUNT(*) AS nb FROM {table}").format(
        table=sql.Identifier(nom_table),
    )
    rows = execute_select_query(connexion, query)
    if rows is None or len(rows) == 0:
        return 0
    # rows[0] est un tuple (nb,)
    return rows[0][0]


# ---------------------------------------------------------------------
# Variante SELECT -> liste de dictionnaires (plus pratique pour les stats)
# ---------------------------------------------------------------------

def execute_select_query_dict(connexion, query, params=None):
    """
    Exécute une requête SELECT et retourne une liste de dictionnaires
    (une par ligne, avec {nom_colonne: valeur}).
    """
    if params is None:
        params = []
    try:
        cursor = connexion.cursor()
        cursor.row_factory = dict_row  # ligne importante
        cursor.execute(query, params)
        return cursor.fetchall()       # liste de dict
    except psycopg.Error as e:
        logger.error(e)
    return None

# ---------------------------------------------------------------------
# Fonctions spécifiques au projet Morpion – Fonctionnalité 1
# ---------------------------------------------------------------------

def get_counts_for_tables(connexion, table_names):
    """
    Retourne une liste de dictionnaires contenant le nombre de lignes
    pour chaque table donnée.

    table_names : liste de noms de tables (strings).
    Résultat : [
        {"table": "team", "count": 4},
        {"table": "morpion", "count": 10},
        ...
    ]
    """
    results = []
    for name in table_names:
        nb = count_instances(connexion, name)
        results.append({"table": name, "count": nb})
    return results


def get_top_teams_by_wins(connexion, limit=3):
    """
    Top des équipes avec le plus de victoires.

    Hypothèses (à adapter selon ton schéma) :
      - table team(id, name, ...)
      - table game(winner_team_id REFERENCES team(id), ...)

    Résultat : liste de dictionnaires
      [
        {"id": 1, "name": "Team A", "wins": 5},
        ...
      ]
    """
    query = """
        SELECT
            t.id_team,
            t.name,
            COUNT(*) AS wins
        FROM team t
        JOIN game g
          ON g.winner_team_id = t.id_team
        GROUP BY t.id_team, t.name
        ORDER BY wins DESC, t.name ASC
        LIMIT %s
    """
    return execute_select_query_dict(connexion, query, [limit]) or []


def get_fastest_and_longest_games(connexion):
    """
    Retourne la partie la plus rapide et la plus longue.

    Hypothèses :
      - table game(id, started_at, ended_at, ...)
      - ended_at peut être NULL si la partie n'est pas terminée.

    Résultat :
      (fastest_game, longest_game)
    où chaque élément est un dict ou None, ex :
      {
        "id": 42,
        "started_at": datetime,
        "ended_at": datetime,
        "duration": timedelta
      }
    """
    base = """
        SELECT
            id_game,
            started_at,
            ended_at,
            (ended_at - started_at) AS duration
        FROM game
        WHERE ended_at IS NOT NULL
    """

    query_fastest = base + " ORDER BY duration ASC LIMIT 1"
    query_longest = base + " ORDER BY duration DESC LIMIT 1"

    fastest_list = execute_select_query_dict(connexion, query_fastest)
    longest_list = execute_select_query_dict(connexion, query_longest)

    fastest = fastest_list[0] if fastest_list else None
    longest = longest_list[0] if longest_list else None

    return fastest, longest


def get_avg_logs_per_month_year(connexion):
    """
    Nombre moyen de lignes de journalisation par couple (année, mois).

    Hypothèses :
      - table logs_entry(game_id, num, created_at, message, ...)
      - created_at : timestamp de la ligne de log.

    Idée :
      1) Pour chaque (game_id, mois), compter nb de lignes.
      2) Moyenne de nb par (année, mois).

    Résultat : liste de dictionnaires
      [
        {"year": 2025, "month": 1, "avg_logs": 3.5},
        ...
      ]
    """
    query = """
        WITH per_game_month AS (
            SELECT
                game_id,
                DATE_TRUNC('month', created_at) AS month_start,
                COUNT(*) AS nb_logs
            FROM logs_entry
            GROUP BY game_id, DATE_TRUNC('month', created_at)
        )
        SELECT
            EXTRACT(YEAR FROM month_start)::int   AS year,
            EXTRACT(MONTH FROM month_start)::int  AS month,
            AVG(nb_logs)::float                   AS avg_logs
        FROM per_game_month
        GROUP BY year, month
        ORDER BY year, month
    """
    return execute_select_query_dict(connexion, query) or []


def get_functionality_one_stats(connexion, table_names=None, top_limit=3):
    """
    Prépare toutes les données nécessaires à la fonctionnalité 1 (page d'accueil).

    table_names : tables pour lesquelles compter les instances (3 minimum recommandées).
    top_limit   : nombre d'équipes à retourner pour le classement (3 par défaut).

    Retourne un dictionnaire avec :
      - counts : [{table, count}, ...]
      - top_teams : classement des équipes
      - fastest_game / longest_game : dict ou None
      - avg_logs : statistiques mensuelles de journaux
    """
    if table_names is None:
        table_names = ["team", "morpion", "game"]

    counts = get_counts_for_tables(connexion, table_names)
    top_teams = get_top_teams_by_wins(connexion, limit=top_limit)
    fastest, longest = get_fastest_and_longest_games(connexion)
    avg_logs = get_avg_logs_per_month_year(connexion)

    return {
        "counts": counts,
        "top_teams": top_teams,
        "fastest_game": fastest,
        "longest_game": longest,
        "avg_logs": avg_logs,
    }
