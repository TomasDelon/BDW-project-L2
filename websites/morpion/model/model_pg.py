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
        with connexion.cursor() as cursor:
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
    Retourne la partie la plus rapide et la plus longue avec les noms et couleurs
    des deux équipes et du gagnant.

    Résultat :
      (fastest_game, longest_game)
    où chaque élément est un dict ou None, par ex. :
      {
        "id_game": 1,
        "started_at": ...,
        "ended_at": ...,
        "duration": ...,
        "team1_id": 1,
        "team1_name": "Verts furieux",
        "team1_color": "green",
        "team2_id": 2,
        "team2_name": "Bleus calmes",
        "team2_color": "blue",
        "winner_id": 1,
        "winner_name": "Verts furieux",
        "winner_color": "green"
      }
    """
    base_query = """
        SELECT
            g.id_game,
            g.started_at,
            g.ended_at,
            g.ended_at - g.started_at AS duration,
            t1.id_team AS team1_id,
            t1.name    AS team1_name,
            t1.color   AS team1_color,
            t2.id_team AS team2_id,
            t2.name    AS team2_name,
            t2.color   AS team2_color,
            tw.id_team AS winner_id,
            tw.name    AS winner_name,
            tw.color   AS winner_color
        FROM game AS g
        JOIN team AS t1 ON t1.id_team = g.team1_id
        JOIN team AS t2 ON t2.id_team = g.team2_id
        LEFT JOIN team AS tw ON tw.id_team = g.winner_team_id
        WHERE g.ended_at IS NOT NULL
        ORDER BY duration {direction}
        LIMIT 1
    """

    # Partie la plus rapide
    fastest_rows = execute_select_query_dict(
        connexion,
        base_query.format(direction="ASC"),
    ) or []
    fastest = fastest_rows[0] if fastest_rows else None

    # Partie la plus longue
    longest_rows = execute_select_query_dict(
        connexion,
        base_query.format(direction="DESC"),
    ) or []
    longest = longest_rows[0] if longest_rows else None

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
