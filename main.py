"""
Point d'entrée principal du jeu
"""
import pygame
import sys
from game import Game
from ui import UI


def main():
    """Fonction principale"""
    # Initialiser pygame
    pygame.init()
    clock = pygame.time.Clock()
    
    # Créer le jeu et l'interface (UI)
    game = Game()
    ui = UI()
    
    # Suivi de l'état des touches pour éviter les déclenchements répétés (compatibilité Windows)
    keys_pressed_last_frame = set()
    key_repeat_timer = {}  # Minuteries de répétition des touches (en millisecondes)
    
    # Groupes de touches directionnelles (flèches + WASD/ZQSD)
    # Défini en dehors de la boucle afin de garantir qu'il reste accessible tout au long de la boucle du jeu
    direction_keys = [
        (pygame.K_UP, pygame.K_w, pygame.K_z),
        (pygame.K_DOWN, pygame.K_s),
        (pygame.K_LEFT, pygame.K_a, pygame.K_q),
        (pygame.K_RIGHT, pygame.K_d)
    ]
    
    # Boucle principale du jeu
    running = True
    # Suivi des touches de confirmation déjà traitées via KEYDOWN pour éviter les doublons
    confirmed_keys_this_frame = set()
    # Suivi des touches directionnelles déjà traitées pendant cette frame
    processed_direction_keys_this_frame = set()
    
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Pour les touches de confirmation, toujours tenter de les traiter
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # Enregistrer l'état avant traitement
                    from game import GameState
                    old_state = getattr(game, 'state', None)
                    old_selected_index = getattr(game, 'selected_room_index', 0)
                    
                    # Tenter de traiter l'événement
                    game.handle_key_event(event.key)
                    
                    # Vérifier si le traitement a réussi
                    new_state = getattr(game, 'state', None)
                    new_selected_index = getattr(game, 'selected_room_index', 0)
                    
                    # Si l'état a changé ou que l'index de salle a changé, le traitement a réussi
                    if old_state != new_state:
                        # L'état a changé, marquer la touche comme déjà traitée
                        confirmed_keys_this_frame.add(event.key)
                    elif old_state == GameState.SELECTING_ROOM and old_selected_index != new_selected_index:
                        # En sélection de salle, si l’index change (par exemple relance), c’est un succès
                        confirmed_keys_this_frame.add(event.key)
                    # Si l'état et l’index ne changent pas, il peut s'agir d'un échec (ex. gemmes insuffisantes)
                    # On vérifie le message pour savoir si un traitement a eu lieu
                    if old_state == GameState.SELECTING_ROOM:
                        # En sélection de salle, un échec ne change pas d'état
                        # On vérifie le message pour savoir si l'action a été tentée
                        current_message = getattr(game, 'message', '')
                        if current_message and (
                            "échec" in current_message
                            or "insuffisant" in current_message
                            or "erreur" in current_message
                            or "non satisfait" in current_message
                        ):
                            # Il y a un message d’erreur, donc l’action a déjà été traitée
                            confirmed_keys_this_frame.add(event.key)
                        # S'il n'y a pas de message d'erreur, il peut s'agir d'une première tentative
                        # La détection continue (via l'état) évitera les doublons
                else:
                    # Pour les autres touches, traitement normal
                    # Vérifier s'il s'agit d'une touche directionnelle
                    is_direction_key = False
                    for key_group in direction_keys:
                        if event.key in key_group:
                            is_direction_key = True
                            break
                    
                    if is_direction_key:
                        # Touche directionnelle : vérifier le verrou de mouvement
                        if not (hasattr(game, 'is_moving') and game.is_moving):
                            game.handle_key_event(event.key)
                            # Marquer cette touche comme traitée pour cette frame
                            processed_direction_keys_this_frame.add(event.key)
                    else:
                        # Touche non directionnelle, traitement normal
                        game.handle_key_event(event.key)
                # Réinitialiser le compteur de répétition pour cette touche
                if event.key in key_repeat_timer:
                    key_repeat_timer[event.key] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si le bouton de réinitialisation a été cliqué
                if hasattr(ui, 'reset_button_rect') and ui.reset_button_rect:
                    if ui.reset_button_rect.collidepoint(event.pos):
                        game.restart()
                        continue
                game.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.KEYUP:
                # Dans certains environnements (IME, etc.), KEYDOWN peut être intercepté ;
                # on utilise aussi KEYUP pour permettre un redémarrage
                if getattr(game, "state", None) == "game_over":
                    game.restart()
                # Nettoyer l'état de la touche
                if event.key in keys_pressed_last_frame:
                    keys_pressed_last_frame.discard(event.key)
                if event.key in key_repeat_timer:
                    del key_repeat_timer[event.key]
            elif event.type == pygame.TEXTINPUT:
                # Compatibilité avec les événements de saisie texte (IME chinois, etc.)
                if getattr(game, "state", None) == "game_over":
                    game.restart()
            elif event.type == pygame.MOUSEBUTTONUP:
                if getattr(game, "state", None) == "game_over":
                    game.restart()
        
        # Détection des touches maintenues (compatibilité Windows)
        # Sur Windows, certains KEYDOWN peuvent ne pas être émis correctement
        # On utilise pygame.key.get_pressed() comme méthode de secours
        keys = pygame.key.get_pressed()
        current_pressed = set()
        
        # Délai de répétition des touches directionnelles (en ms) — souvent plus long sur Windows
        repeat_delay = 200   # Après 200 ms, commencer la répétition
        repeat_interval = 100  # Intervalle de répétition de 100 ms
        frame_time = clock.get_time()  # Temps de la frame précédente (ms)
        if frame_time == 0:
            frame_time = 16  # Valeur par défaut ~60 FPS
        
        for key_group in direction_keys:
            for key in key_group:
                if keys[key]:
                    current_pressed.add(key)
                    # Première barrière : si un mouvement est en cours, ignorer cette touche
                    if hasattr(game, 'is_moving') and game.is_moving:
                        break
                    
                    # Si la touche n'était pas pressée à la frame précédente, déclenchement immédiat
                    if key not in keys_pressed_last_frame:
                        # Deuxième barrière : re-vérifier le verrou de mouvement avant d’appeler handle_key_event
                        if hasattr(game, 'is_moving') and game.is_moving:
                            break
                        # Troisième barrière : si la touche a déjà été traitée via KEYDOWN dans cette frame, ne pas répéter
                        if key in processed_direction_keys_this_frame:
                            break
                        game.handle_key_event(key)
                        key_repeat_timer[key] = 0
                        # Marquer comme déjà traitée pour cette frame
                        processed_direction_keys_this_frame.add(key)
                    else:
                        # Touche maintenue : utilisation d’un timer pour contrôler la répétition
                        if key not in key_repeat_timer:
                            key_repeat_timer[key] = 0
                        else:
                            key_repeat_timer[key] += frame_time
                            if key_repeat_timer[key] >= repeat_delay:
                                # Vérifier si on doit répéter
                                # Quatrième barrière : vérifier le verrou de mouvement avant de répéter
                                if hasattr(game, 'is_moving') and game.is_moving:
                                    break
                                elapsed = key_repeat_timer[key] - repeat_delay
                                if elapsed >= repeat_interval:
                                    # Dernière vérification avant déclenchement
                                    if hasattr(game, 'is_moving') and game.is_moving:
                                        break
                                    game.handle_key_event(key)
                                    key_repeat_timer[key] = repeat_delay
                    break
        
        # Vérifier les touches de confirmation (Entrée et Espace) — ne doivent pas se répéter
        # Ici, c'est un mécanisme de secours au cas où KEYDOWN serait perdu
        confirm_keys = [pygame.K_RETURN, pygame.K_SPACE]
        for key in confirm_keys:
            if keys[key]:
                current_pressed.add(key)
                # Si la touche n’était pas pressée à la frame précédente, et pas déjà traitée via KEYDOWN
                if key not in keys_pressed_last_frame and key not in confirmed_keys_this_frame:
                    # Vérifier l'état du jeu, et traiter dans les états nécessitant une confirmation
                    if hasattr(game, 'state'):
                        from game import GameState
                        # Dans ces états, Entrée/Espace sert à valider
                        if game.state in (
                            GameState.SELECTING_ROOM,
                            GameState.SELECTING_DIRECTION,
                            GameState.PICKING_ITEMS,
                            GameState.SHOP,
                        ):
                            # Enregistrer l'état avant traitement
                            old_state = game.state
                            old_selected_index = getattr(game, 'selected_room_index', 0)
                            old_message = getattr(game, 'message', '')
                            
                            # Tenter de traiter l’événement
                            game.handle_key_event(key)
                            
                            # Vérifier les changements
                            new_state = getattr(game, 'state', None)
                            new_selected_index = getattr(game, 'selected_room_index', 0)
                            new_message = getattr(game, 'message', '')
                            
                            if old_state != new_state:
                                confirmed_keys_this_frame.add(key)
                            elif old_state == GameState.SELECTING_ROOM and old_selected_index != new_selected_index:
                                confirmed_keys_this_frame.add(key)
                            elif old_state == GameState.SELECTING_ROOM and old_message != new_message:
                                # Si le message a changé (par ex. message d’erreur), on considère que c'est déjà traité
                                if new_message and (
                                    "échec" in new_message
                                    or "insuffisant" in new_message
                                    or "erreur" in new_message
                                    or "non satisfait" in new_message
                                ):
                                    confirmed_keys_this_frame.add(key)
            else:
                # Si la touche est relâchée, la retirer des touches pressées
                if key in keys_pressed_last_frame:
                    current_pressed.discard(key)
        
        # Nettoyer les minuteries des touches relâchées
        released_keys = keys_pressed_last_frame - current_pressed
        for key in released_keys:
            if key in key_repeat_timer:
                del key_repeat_timer[key]
        
        # Mettre à jour l’état des touches pour la frame suivante
        keys_pressed_last_frame = current_pressed
        
        # Nettoyer les touches directionnelles traitées dans cette frame
        processed_direction_keys_this_frame.clear()
        
        # Mettre à jour l’état du jeu
        game.update()
        
        # Nettoyer les touches de confirmation traitées dans cette frame
        confirmed_keys_this_frame.clear()
        
        # Rendu de l’interface
        ui.render(game)
        
        # Limiter la fréquence d’images
        clock.tick(60)
    
    # Quitter proprement
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
