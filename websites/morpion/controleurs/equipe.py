"""
Contrôleur pour créer une nouvelle équipe avec sélection de morpions.
"""

from model.model_pg import (
    get_all_morpions,
    check_team_name_color_exists,
    check_team_color_exists,
    create_team,
    add_morpions_to_team
)

REQUEST_VARS.setdefault('message', None)
REQUEST_VARS.setdefault('message_class', None)
REQUEST_VARS.setdefault('form_team_name', '')
REQUEST_VARS.setdefault('form_team_color', '')
REQUEST_VARS.setdefault('form_selected_morpions', [])

# Récupérer tous les morpions disponibles
morpions = get_all_morpions(SESSION["CONNEXION"])
REQUEST_VARS["morpions"] = morpions

# Traitement du formulaire POST
# On se base sur la présence du champ team_name (toujours envoyé lors de la soumission)
if 'team_name' in POST:
    # Récupérer les données du formulaire
    team_name = POST.get('team_name', [''])[0].strip()
    team_color = POST.get('team_color', [''])[0].strip()
    selected_morpions = POST.get('morpions', [])
    
    # Mémoriser pour réaffichage en cas d'erreur
    REQUEST_VARS['form_team_name'] = team_name
    REQUEST_VARS['form_team_color'] = team_color
    REQUEST_VARS['form_selected_morpions'] = [int(m_id) for m_id in selected_morpions] if selected_morpions else []
    
    # Validation
    if not team_name:
        REQUEST_VARS['message'] = "Erreur : le nom de l'équipe est obligatoire."
        REQUEST_VARS['message_class'] = "alert-error"
    elif not team_color:
        REQUEST_VARS['message'] = "Erreur : la couleur de l'équipe est obligatoire."
        REQUEST_VARS['message_class'] = "alert-error"
    elif not selected_morpions or len(selected_morpions) == 0:
        REQUEST_VARS['message'] = "Erreur : vous devez sélectionner au moins un morpion."
        REQUEST_VARS['message_class'] = "alert-error"
    elif len(selected_morpions) < 6:
        REQUEST_VARS['message'] = f"Erreur : vous devez sélectionner au moins 6 morpions (actuellement {len(selected_morpions)})."
        REQUEST_VARS['message_class'] = "alert-error"
    elif len(selected_morpions) > 8:
        REQUEST_VARS['message'] = f"Erreur : vous ne pouvez pas sélectionner plus de 8 morpions (actuellement {len(selected_morpions)})."
        REQUEST_VARS['message_class'] = "alert-error"
    elif check_team_name_color_exists(SESSION["CONNEXION"], team_name, team_color):
        REQUEST_VARS['message'] = f"Erreur : une équipe avec le nom '{team_name}' et la couleur '{team_color}' existe déjà."
        REQUEST_VARS['message_class'] = "alert-error"
    elif check_team_color_exists(SESSION["CONNEXION"], team_color):
        REQUEST_VARS['message'] = f"Erreur : une équipe avec la couleur '{team_color}' existe déjà (la couleur doit être unique)."
        REQUEST_VARS['message_class'] = "alert-error"
    else:
        # Créer l'équipe
        team_id = create_team(SESSION["CONNEXION"], team_name, team_color)
        
        if team_id:
            # Convertir les IDs de morpions en entiers
            morpion_ids = [int(m_id) for m_id in selected_morpions]
            
            # Ajouter les morpions à l'équipe
            count = add_morpions_to_team(SESSION["CONNEXION"], team_id, morpion_ids)
            
            if count is not None:
                REQUEST_VARS['message'] = f"L'équipe '{team_name}' a été créée avec succès avec {count} morpion(s) !"
                REQUEST_VARS['message_class'] = "alert-success"
                # Réinitialiser les champs du formulaire
                REQUEST_VARS['form_team_name'] = ''
                REQUEST_VARS['form_team_color'] = ''
                REQUEST_VARS['form_selected_morpions'] = []
                REQUEST_VARS["morpions"] = get_all_morpions(SESSION["CONNEXION"])
            else:
                REQUEST_VARS['message'] = "Erreur : l'équipe a été créée mais les morpions n'ont pas pu être ajoutés."
                REQUEST_VARS['message_class'] = "alert-error"
        else:
            REQUEST_VARS['message'] = "Erreur : impossible de créer l'équipe."
            REQUEST_VARS['message_class'] = "alert-error"
