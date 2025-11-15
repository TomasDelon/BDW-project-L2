"""
Contrôleur pour lister les équipes et permettre leur suppression.
"""

from model.model_pg import get_all_teams_with_morpions, delete_team, get_games_for_team

REQUEST_VARS.setdefault('message', None)
REQUEST_VARS.setdefault('message_class', None)
REQUEST_VARS.setdefault('team_to_delete', None)
REQUEST_VARS.setdefault('games_to_delete', None)

# Récupérer toutes les équipes avec leurs morpions
teams = get_all_teams_with_morpions(SESSION["CONNEXION"])
REQUEST_VARS["teams"] = teams

# Pour chaque équipe, récupérer les parties associées (pour affichage)
for team in teams:
    games = get_games_for_team(SESSION["CONNEXION"], team['id_team'])
    team['games'] = games
    team['games_count'] = len(games)

# Traitement de la suppression
# On déclenche la logique de suppression dès qu'un team_id est envoyé en POST
if 'team_id' in POST:
    team_id_str = POST.get('team_id', [''])[0].strip()
    
    if not team_id_str:
        REQUEST_VARS['message'] = "Erreur : aucun identifiant d'équipe fourni."
        REQUEST_VARS['message_class'] = "alert-error"
        REQUEST_VARS['team_to_delete'] = None
        REQUEST_VARS['games_to_delete'] = None
    else:
        try:
            team_id = int(team_id_str)
            
            # Trouver l'équipe et ses parties
            team_to_delete = None
            for team in teams:
                if team['id_team'] == team_id:
                    team_to_delete = team
                    break
            
            if not team_to_delete:
                REQUEST_VARS['message'] = "Erreur : équipe introuvable."
                REQUEST_VARS['message_class'] = "alert-error"
                REQUEST_VARS['team_to_delete'] = None
                REQUEST_VARS['games_to_delete'] = None
            else:
                # Vérifier si l'équipe est utilisée dans des parties
                games = get_games_for_team(SESSION["CONNEXION"], team_id)
                
                if len(games) > 0:
                    # L'équipe est utilisée dans des parties
                    # Vérifier si l'utilisateur a confirmé la suppression des parties
                    if 'confirm_delete_games' in POST:
                        # L'utilisateur a confirmé : supprimer les parties puis l'équipe
                        delete_games = POST.get('confirm_delete_games', [''])[0].strip().lower() == 'yes'
                        
                        if delete_games:
                            success = delete_team(SESSION["CONNEXION"], team_id, delete_games=True)
                            
                            if success:
                                REQUEST_VARS['message'] = f"L'équipe '{team_to_delete['name']}' et ses {len(games)} partie(s) associée(s) ont été supprimées avec succès !"
                                REQUEST_VARS['message_class'] = "alert-success"
                                # Recharger la liste des équipes
                                teams = get_all_teams_with_morpions(SESSION["CONNEXION"])
                                for team in teams:
                                    games = get_games_for_team(SESSION["CONNEXION"], team['id_team'])
                                    team['games'] = games
                                    team['games_count'] = len(games)
                                REQUEST_VARS["teams"] = teams
                                REQUEST_VARS['team_to_delete'] = None
                                REQUEST_VARS['games_to_delete'] = None
                            else:
                                REQUEST_VARS['message'] = "Erreur : impossible de supprimer l'équipe et ses parties."
                                REQUEST_VARS['message_class'] = "alert-error"
                                REQUEST_VARS['team_to_delete'] = None
                                REQUEST_VARS['games_to_delete'] = None
                        else:
                            # L'utilisateur a choisi de conserver les parties
                            REQUEST_VARS['message'] = "Suppression annulée : l'équipe est conservée car elle est utilisée dans des parties."
                            REQUEST_VARS['message_class'] = "alert-info"
                            REQUEST_VARS['team_to_delete'] = None
                            REQUEST_VARS['games_to_delete'] = None
                    else:
                        # Afficher les parties et demander confirmation
                        REQUEST_VARS['team_to_delete'] = team_to_delete
                        REQUEST_VARS['games_to_delete'] = games
                        REQUEST_VARS['message'] = f"L'équipe '{team_to_delete['name']}' est utilisée dans {len(games)} partie(s). Souhaitez-vous supprimer ces parties également ?"
                        REQUEST_VARS['message_class'] = "alert-warning"
                else:
                    # L'équipe n'est pas utilisée dans des parties, suppression directe
                    success = delete_team(SESSION["CONNEXION"], team_id, delete_games=False)
                    
                    if success:
                        REQUEST_VARS['message'] = f"L'équipe '{team_to_delete['name']}' a été supprimée avec succès !"
                        REQUEST_VARS['message_class'] = "alert-success"
                        # Recharger la liste des équipes
                        teams = get_all_teams_with_morpions(SESSION["CONNEXION"])
                        for team in teams:
                            games = get_games_for_team(SESSION["CONNEXION"], team['id_team'])
                            team['games'] = games
                            team['games_count'] = len(games)
                        REQUEST_VARS["teams"] = teams
                        REQUEST_VARS['team_to_delete'] = None
                        REQUEST_VARS['games_to_delete'] = None
                    else:
                        REQUEST_VARS['message'] = "Erreur : impossible de supprimer l'équipe."
                        REQUEST_VARS['message_class'] = "alert-error"
                        REQUEST_VARS['team_to_delete'] = None
                        REQUEST_VARS['games_to_delete'] = None
        except ValueError:
            REQUEST_VARS['message'] = "Erreur : identifiant d'équipe invalide."
            REQUEST_VARS['message_class'] = "alert-error"
            REQUEST_VARS['team_to_delete'] = None
            REQUEST_VARS['games_to_delete'] = None
        except Exception as e:
            REQUEST_VARS['message'] = f"Erreur lors de la suppression : {str(e)}"
            REQUEST_VARS['message_class'] = "alert-error"
            REQUEST_VARS['team_to_delete'] = None
            REQUEST_VARS['games_to_delete'] = None

