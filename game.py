"""
Classe principale du jeu, gérant les états du jeu et la boucle principale.
"""
import random
import pygame
from item import TreasureChest, DiggingSpot, Locker, FoodItem, ConsumableItem
from player import Player
from mansion import Mansion
from room_selector import RoomSelector
from rooms_data import create_room_templates
import config


class GameState:
    """Énumération des états du jeu."""
    PLAYING = "playing"
    SELECTING_ROOM = "selecting_room"
    SELECTING_DIRECTION = "selecting_direction"
    GAME_OVER = "game_over"
    SHOP = "shop"
    PICKING_ITEMS = "picking_items"


class Game:
    """Classe principale du jeu."""
    
    def __init__(self):
        """Initialiser le jeu."""
        # Définir une graine aléatoire (différente pour chaque jeu).
        import time
        random.seed(int(time.time() * 1000) % 1000000)
        
        # initialiser pygame
        pygame.init()
        
        # Création d’un objet de jeu
        self.mansion = Mansion()
        self.player = Player()
        self.room_templates = create_room_templates()
        self.room_selector = RoomSelector(self.room_templates)
        
        # État du jeu
        self.state = GameState.PLAYING
        self.selected_direction = None
        self.available_rooms = []
        self.selected_room_index = 0
        self.target_position = None
        self.message = ""
        self.game_over_message = ""
        
        # Sélection de chambre actuelle pertinente
        self.pending_room_selection = False
        self.pending_direction = None
        self.pending_position = None
        # Index de sélection d’articles/magasins
        self.item_selection_index = 0
        self.shop_selection_index = 0
        
        # Verrouillage mobile: empêche le déclenchement de nouveaux mouvements pendant le déplacement
        self.is_moving = False
    
    def handle_key_event(self, key):
        """
        Gérer les événements clavier.
        
        Args:
            key: Valeur de clé pygame
        """
        if self.state == GameState.GAME_OVER:
            # Le jeu se termine, appuyez sur n’importe quelle touche pour recommencer
            self.restart()
            return
        
        if self.state == GameState.SELECTING_ROOM:
            self._handle_room_selection(key)
        elif self.state == GameState.SELECTING_DIRECTION:
            self._handle_direction_selection(key)
        elif self.state == GameState.PLAYING:
            self._handle_playing(key)
        elif self.state == GameState.SHOP:
            self._handle_shop(key)
        elif self.state == GameState.PICKING_ITEMS:
            self._handle_item_picking(key)
    
    def handle_mouse_click(self, pos=None, button=None):
        """
        Gérer les clics de souris (permet aussi de redémarrer lorsque la partie est terminée).
        """
        if self.state == GameState.GAME_OVER:
            self.restart()
            return
        
        # Vérifier si le bouton de réinitialisation a été cliqué (cette vérification doit être effectuée dans l'interface utilisateur ; pour l'instant, renvoyer None et laisser l'interface utilisateur gérer cela).
        # La détection de clic du bouton de réinitialisation réelle est traitée dans l'UI
        return None
    
    def _handle_playing(self, key):
        """Gérer les touches pendant la phase de jeu."""
        # Si vous vous déplacez, ignorez toutes les entrées des touches fléchées (pour éviter de sauter des pièces).
        # Il s'agit de la première ligne de défense, garantissant qu'aucune nouvelle demande de déplacement ne soit traitée pendant le déménagement.
        if self.is_moving:
            return
        
        # Touches fléchées : Décidez si une confirmation d’espace est requise en fonction de STRICT_MODE
        if key == pygame.K_w or key == pygame.K_UP or key == pygame.K_z:
            self.selected_direction = 'UP'
            if config.STRICT_MODE:
                self.state = GameState.SELECTING_DIRECTION
            else:
                self._try_move(self.selected_direction)
                self.selected_direction = None
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.selected_direction = 'DOWN'
            if config.STRICT_MODE:
                self.state = GameState.SELECTING_DIRECTION
            else:
                self._try_move(self.selected_direction)
                self.selected_direction = None
        elif key == pygame.K_a or key == pygame.K_LEFT or key == pygame.K_q:
            self.selected_direction = 'LEFT'
            if config.STRICT_MODE:
                self.state = GameState.SELECTING_DIRECTION
            else:
                self._try_move(self.selected_direction)
                self.selected_direction = None
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            self.selected_direction = 'RIGHT'
            if config.STRICT_MODE:
                self.state = GameState.SELECTING_DIRECTION
            else:
                self._try_move(self.selected_direction)
                self.selected_direction = None
        # Barre d'espace pour confirmation (ou laissez-la).
        elif key == pygame.K_SPACE:
            if self.selected_direction:
                self._try_move(self.selected_direction)
                self.selected_direction = None
        elif key == pygame.K_e:
            # Ouvrir la liste d'interaction avec l'objet
            room = self.get_current_room()
            if room and room.items:
                self.item_selection_index = 0
                self.state = GameState.PICKING_ITEMS
                self.message = "Ouvrir la liste d’interaction avec les objets."
        elif key == pygame.K_b:
            # Entrer dans la boutique.
            room = self.get_current_room()
            if room and room.effects and room.effects.get("shop"):
                self.shop_selection_index = 0
                self.state = GameState.SHOP
                self.message = "Boutique: Haut et Bas Sélectionner, Entrée pour acheter, ESC Retour"
        elif key == pygame.K_i:
            # Debug : afficher l’état des portes à la position actuelle.
            current_room = self.mansion.get_room(self.player.row, self.player.col)
            if current_room:
                door_info = []
                for direction, door in current_room.door_objects.items():
                    dr, dc = config.DIRECTIONS[direction]
                    target_row = self.player.row + dr
                    target_col = self.player.col + dc
                    target_room = self.mansion.get_room(target_row, target_col)
                    status = "déjà ouvert" if door.opened else "Non ouvert"
                    can_open, reason = door.can_open(self.player)
                    if can_open:
                        status += " (Peut être ouvert)"
                    else:
                        status += f" (Impossible à ouvrir: {reason})"
                    target_info = f"Cible({target_row},{target_col}): {'Il y a des chambres' if target_room else 'espace vide'}"
                    door_info.append(f"{direction}: {status}, {target_info}")
                self.message = f"Emplacement({self.player.row},{self.player.col}) État de la porte: " + "; ".join(door_info)
            else:
                self.message = f"Erreur : Emplacement({self.player.row},{self.player.col})pas de place"
    
    def _handle_direction_selection(self, key):
        """sélection du sens de traitement"""
        if key == pygame.K_SPACE:
            # Confirmer le déplacement
            if self.selected_direction:
                self._try_move(self.selected_direction)
                self.selected_direction = None
                self.state = GameState.PLAYING
        elif key == pygame.K_ESCAPE:
            # Annuler la sélection.
            self.selected_direction = None
            self.state = GameState.PLAYING
        else:
            # Changer de direction.
            self._handle_playing(key)
    
    def _handle_room_selection(self, key):
        """sélection de chambre"""
        if len(self.available_rooms) == 0:
            # S’il n’y a aucune salle disponible (cas anormal), on ajoute une protection.
            self.message = "Erreur : Aucune chambre disponible."
            self.state = GameState.PLAYING
            return
        
        # S’assurer que l’indice est dans la plage valide.
        if not (0 <= self.selected_room_index < len(self.available_rooms)):
            self.selected_room_index = 0
        
        if key == pygame.K_LEFT or key == pygame.K_a or key == pygame.K_q:
            # Sélectionner la salle suivante (déplacement vers la droite dans la liste).
            self.selected_room_index = (self.selected_room_index + 1) % len(self.available_rooms)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            # Sélectionner la salle précédente (déplacement vers la gauche dans la liste).
            self.selected_room_index = (self.selected_room_index - 1) % len(self.available_rooms)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Confirmer la sélection
            # Vérifier une nouvelle fois que l’indice est valide.
            if not (0 <= self.selected_room_index < len(self.available_rooms)):
                self.selected_room_index = 0
            # Appeler la méthode de validation de la sélection.
            self._confirm_room_selection()
        elif key == pygame.K_r:
            # Relancer les dés pour tirer à nouveau.
            self._reroll_rooms()
        elif key == pygame.K_ESCAPE:
            # Annuler la sélection de salle et revenir au jeu.
            # Remarque : la porte est déjà ouverte, mais le joueur n’a pas choisi de salle ; la porte reste donc ouverte.
            # Ainsi, le joueur pourra plus tard choisir de nouveau une salle ou une autre direction.
            self.message = "La sélection de chambres a été annulée"
            self.state = GameState.PLAYING
            # Réinitialiser les données liées à la sélection de salle.
            self.available_rooms = []
            self.selected_room_index = 0
            self.target_position = None
            self.pending_direction = None
    
    def _handle_shop(self, key):
        """Traite l'interaction avec le magasin"""
        room = self.get_current_room()
        if key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
            return
        if not room or not (room.effects and room.effects.get("shop")):
            self.state = GameState.PLAYING
            return
        items = room.effects.get("items", [])
        if not items:
            self.message = "Le magasin n'a pas d'articles pour le moment"
            return
        if key in (pygame.K_UP, pygame.K_w):
            self.shop_selection_index = (self.shop_selection_index - 1) % len(items)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.shop_selection_index = (self.shop_selection_index + 1) % len(items)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            spec = items[self.shop_selection_index]
            price = spec.get("price", 0)
            if self.player.inventory.coins.amount < price:
                self.message = "Pièces d'or insuffisantes"
                return
            # Payer et obtenir l'article
            self.player.inventory.remove_coins(price)
            it = spec.get("item")
            if hasattr(it, "name"):
                if isinstance(it, ConsumableItem):
                    if it.name == "Pièces d'or":
                        self.player.inventory.add_coins(it.amount)
                    elif it.name == "Gemmes":
                        self.player.inventory.add_gems(it.amount)
                    elif it.name == "Clés":
                        self.player.inventory.add_keys(it.amount)
                    elif it.name == "Dés":
                        self.player.inventory.add_dice(it.amount)
                elif isinstance(it, FoodItem):
                    self.player.inventory.add_steps(it.steps_restored)
            self.message = f"Achat réussi :{spec.get('name','Article')}"
    
    def _handle_item_picking(self, key):
        """Traite le ramassage d'objets"""
        room = self.get_current_room()
        if key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
            return
        if not room or not room.items:
            self.state = GameState.PLAYING
            return
        if key in (pygame.K_UP, pygame.K_w):
            self.item_selection_index = (self.item_selection_index - 1) % len(room.items)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.item_selection_index = (self.item_selection_index + 1) % len(room.items)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            item = room.items[self.item_selection_index]
            success, msg = self._interact_with_item(item, room)
            self.message = msg or ""
            if success and self.item_selection_index >= len(room.items):
                self.item_selection_index = max(0, len(room.items) - 1)
            if not room.items:
                self.state = GameState.PLAYING
    
    def _try_move(self, direction):
        """
        Tente de déplacer le joueur.
        
        Args:
            direction: direction de déplacement
        """
        # Si en mouvement, ignore la nouvelle requête de mouvement (empêche de sauter des pièces)
        # C'est la deuxième ligne de défense, double vérification pour s'assurer qu'aucune pièce n'est sautée
        if self.is_moving:
            return
        
        # Configure le verrou de mouvement (défini avant de commencer à bouger, assure qu'il n'y a pas de mouvement concurrent)
        self.is_moving = True
        
        try:
            success, message = self.player.move(direction, self.mansion)
            
            if success is None:
                # Nécessite la sélection d'une pièce
                self._start_room_selection(direction)
                # Note : Lors de la sélection de la pièce, le verrou de mouvement doit être relâché, car aucun mouvement réel n'a eu lieu à ce stade
                self.is_moving = False
            elif success:
                self.message = message
                # Vérifie si le hall d'entrée est atteint
                if self.mansion.check_win_condition(self.player):
                    self.state = GameState.GAME_OVER
                    self.game_over_message = "🎉 Félicitations ! Vous avez atteint le hall d'entrée avec succès ! Victoire du jeu !"
                    self.is_moving = False
                # Vérifie si le jeu est perdu
                elif self.mansion.check_lose_condition(self.player)[0]:
                    self.state = GameState.GAME_OVER
                    lose_reason = self.mansion.check_lose_condition(self.player)[1]
                    self.game_over_message = f"Fin du jeu:{lose_reason}"
                    self.is_moving = False
                else:
                    # Mouvement réussi, relâche le verrou de mouvement (après vérification de l'état du jeu)
                    self.is_moving = False
            else:
                self.message = message
                # Mouvement échoué, relâche le verrou de mouvement
                self.is_moving = False
        except Exception as e:
            # Une erreur s'est produite, assurez-vous de relâcher le verrou de mouvement
            self.is_moving = False
            self.message = f"Erreur de mouvement:{str(e)}"
    
    def _interact_with_item(self, item, room):
        """Interagit avec l'article et traite le résultat"""
        # Type tuple (Nom, Quantité/Valeur)
        if isinstance(item, tuple):
            success, msg = self.player.pick_up_item(item, self.mansion)
            if success:
                if item in room.items:
                    room.items.remove(item)
            return success, msg
        # Conteneur/Interactif
        if isinstance(item, TreasureChest):
            # Clé en priorité, sinon marteau
            contents, msg = (None, None)
            if self.player.inventory.keys.has(1):
                contents, msg = item.open_with_key(self.player)
            elif self.player.inventory.hammer.has():
                contents, msg = item.open_with_hammer(self.player)
            else:
                return False, "Manque de clé ou de marteau"
            if contents is not None:
                self._gain_contents(contents)
                if item in room.items:
                    room.items.remove(item)
            return True, msg
        if isinstance(item, DiggingSpot):
            contents, msg = item.dig(self.player)
            if contents is not None:
                self._gain_contents(contents)
                if item in room.items:
                    room.items.remove(item)
            return True, msg
        if isinstance(item, Locker):
            contents, msg = item.open(self.player)
            if contents is not None:
                self._gain_contents(contents)
                if item in room.items:
                    room.items.remove(item)
            return True, msg
        # Nourriture ou produits de consommation, etc.
        success, msg = self.player.pick_up_item(item, self.mansion)
        if success and item in room.items:
            room.items.remove(item)
        return success, msg

    def _gain_contents(self, contents):
        """Ajoute le contenu obtenu des conteneurs/fouilles à l'inventaire"""
        if not contents:
            return
        for entry in contents:
            if isinstance(entry, tuple):
                name, val = entry
                if name == "pièces":
                    self.player.inventory.add_coins(val)
                elif name == "gemmes":
                    self.player.inventory.add_gems(val)
                elif name == "clés":
                    self.player.inventory.add_keys(val)
                elif name == "dés":
                    self.player.inventory.add_dice(val)
                elif name == "Article permanent":
                    self.player.inventory.add_permanent_item(val)
                elif name in ["Pomme", "Banane", "Gâteau", "Sandwich", "Grand repas"]:
                    # Mangé directement
                    food_map = {"Pomme": 2, "Banane": 3, "Gâteau": 10, "Sandwich": 15, "Grand repas": 25}
                    self.player.inventory.add_steps(food_map.get(name, 0))
            # Autres types ignorés
    
    def _start_room_selection(self, direction):
        """
        Démarre le processus de sélection de pièce.
        
        Args:
            direction: direction de la porte
        """
        # Assurez-vous que la porte de la pièce actuelle est ouverte (devrait être ouverte dans player.move, mais on le vérifie)
        current_room = self.mansion.get_room(self.player.row, self.player.col)
        if current_room and current_room.door_objects.get(direction):
            current_room.door_objects[direction].opened = True
        
        # Calcule la position cible
        dr, dc = config.DIRECTIONS[direction]
        target_row = self.player.row + dr
        target_col = self.player.col + dc
        
        # Tire les pièces (exige que la nouvelle pièce contienne une porte inversée pour assurer la connectivité)
        self.available_rooms = self.room_selector.draw_rooms(
            target_row, target_col, self.mansion, self.player, required_direction=direction
        )
        
        if len(self.available_rooms) == 0:
            self.message = "Aucune pièce disponible"
            self.state = GameState.PLAYING
            return
        
        self.target_position = (target_row, target_col)
        self.selected_room_index = 0
        self.state = GameState.SELECTING_ROOM
        self.pending_direction = direction
    
    def _confirm_room_selection(self):
        """Confirme la sélection de pièce"""
        if len(self.available_rooms) == 0:
            self.message = "Erreur : Aucune pièce sélectionnable"
            self.state = GameState.PLAYING
            return
        
        # Vérifiez que l'index se situe dans la plage valide.
        if not (0 <= self.selected_room_index < len(self.available_rooms)):
            self.selected_room_index = 0
            self.message = "Erreur : Index de pièce invalide, réinitialisé à la première pièce"
        
        selected_room = self.available_rooms[self.selected_room_index]
        target_row, target_col = self.target_position
        
        # Sélectionne la pièce
        success, message = self.room_selector.select_room(
            selected_room, target_row, target_col, self.mansion, self.player
        )
        
        if not success:
            # Échec de la sélection (par exemple, pas assez de gemmes, impossible de placer, etc.), maintient l'état de sélection pour que le joueur puisse resélectionner
            self.message = f"Échec de la sélection:{message}(Appuyez sur ÉCHAP pour annuler)"
            # L'état SELECTING_ROOM est conservé, permettant aux joueurs de resélectionner, d'utiliser des dés ou d'appuyer sur ÉCHAP pour annuler.
            # Remarque : Si l'état n'a pas changé, mais que le message a changé, cela sera détecté par une surveillance continue.
            return
        
        # Sélection réussie, vérifie si la pièce est réellement placée sur la grille
        placed_room = self.mansion.get_room(target_row, target_col)
        if placed_room is None:
            self.message = "Erreur : La pièce n'a pas été placée correctement sur la grille"
            self.state = GameState.PLAYING
            return
        
        if success:
            # La pièce a été placée, déplace maintenant le joueur
            self.message = message
            
            # Obtient la pièce actuelle (position avant le mouvement)
            current_room = self.mansion.get_room(self.player.row, self.player.col)
            if not current_room:
                self.message = "Erreur : La pièce actuelle n'existe pas"
                self.state = GameState.PLAYING
                return
            
            # Assurez-vous que la porte de la pièce actuelle est ouverte (devrait être ouverte dans player.move, mais on vérifie à nouveau)
            current_door = current_room.door_objects.get(self.pending_direction)
            if current_door:
                current_door.opened = True
            else:
                # C'est une erreur grave si la porte n'existe pas.
                self.message = f"Erreur : La pièce actuelle n'a pas de porte dans la direction{self.pending_direction}"
                self.state = GameState.PLAYING
                return
            
            # Consomme un pas et bouge
            if not self.player.inventory.consume_step():
                self.message = "Pas insuffisants, impossible de bouger"
                self.state = GameState.PLAYING
                return
            
            # Déplace la position du joueur
            self.player.row = target_row
            self.player.col = target_col
            
            # Utilise l'objet pièce réel dans la grille qui a été vérifié précédemment
            # Le paramètre `placed_room` a déjà été vérifié ci-dessus ; veuillez vous assurer qu'il existe.
            placed_room.explored = True
            
            # Ouvre la porte bidirectionnelle : la porte inversée de la pièce cible doit être ouverte
            opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}[self.pending_direction]
            
            # Calcule le décalage de direction
            dr, dc = config.DIRECTIONS[self.pending_direction]
            previous_row = self.player.row - dr
            previous_col = self.player.col - dc
            
            # Assure que les deux portes bidirectionnelles sont ouvertes
            # 1. Porte de la pièce actuelle (position avant le mouvement)
            current_room_after = self.mansion.get_room(previous_row, previous_col)
            if current_room_after:
                current_door_after = current_room_after.door_objects.get(self.pending_direction)
                if current_door_after:
                    current_door_after.opened = True
                else:
                    self.message = f"Erreur : La pièce actuelle n'a pas de porte dans la direction{self.pending_direction}"
                    self.state = GameState.PLAYING
                    return
            
            # 2. Porte inversée de la nouvelle pièce (C'est la clé !)
            # Utilise l'objet pièce réel dans la grille
            opposite_door = placed_room.door_objects.get(opposite)
            if opposite_door:
                opposite_door.opened = True
            else:
                # C'est une erreur grave si la porte arrière n'existe pas.
                self.message = f"Erreur critique : La nouvelle pièce n'a pas de porte dans la direction{opposite}"
                self.state = GameState.PLAYING
                return
            
            # Applique l'effet de la pièce (utilise l'objet pièce réel dans la grille)
            effect_msg = placed_room.apply_effect(self.player, self.mansion)
            if effect_msg:
                self.message += f",{effect_msg}"
            
            # Les objets de la pièce ont déjà été générés dans select_room, il n'est pas nécessaire de les regénérer ici
            
            # Dernière vérification de l'état de la porte avant de vérifier les conditions de défaite
            # Réobtient l'objet pièce, assurez-vous d'utiliser le dernier état de la porte
            final_room = self.mansion.get_room(self.player.row, self.player.col)
            if final_room:
                # Assurez-vous que la porte arrière est ouverte.
                final_opposite_door = final_room.door_objects.get(opposite)
                if final_opposite_door:
                    final_opposite_door.opened = True
                else:
                    self.message = f"Erreur critique : L'objet pièce final n'a pas de porte dans la direction{opposite}"
                    self.state = GameState.PLAYING
                    return
            
            # Vérifie les conditions de fin de jeu (assurez-vous que la porte inversée est ouverte avant de vérifier)
            if self.mansion.check_win_condition(self.player):
                self.state = GameState.GAME_OVER
                self.game_over_message = "🎉 Félicitations ! Vous avez atteint le hall d'entrée avec succès ! Victoire du jeu !"
                # Assurez-vous que le verrouillage du téléphone portable a été déverrouillé.
                self.is_moving = False
            else:
                # Vérifie les conditions de défaite
                lose_result = self.mansion.check_lose_condition(self.player)
                if lose_result[0]:
                    # Si la défaite est déterminée, ajoute des informations de débogage détaillées
                    debug_info = f"Position actuelle: ({self.player.row}, {self.player.col}), "
                    if final_room:
                        opened_doors = [d for d, door in final_room.door_objects.items() if door.opened]
                        all_doors = list(final_room.door_objects.keys())
                        debug_info += f"Toutes les portes : {all_doors}, Portes ouvertes : {opened_doors}, "
                        debug_info += f"Porte inversée({opposite}): {'Ouverte' if final_room.door_objects.get(opposite) and final_room.door_objects[opposite].opened else 'Non ouverte'}"
                    self.state = GameState.GAME_OVER
                    self.game_over_message = f"Fin du jeu:{lose_result[1]} ({debug_info})"
                else:
                    self.state = GameState.PLAYING
    
    def _reroll_rooms(self):
        """Utilise un dé pour retier des pièces"""
        if not self.player.inventory.dice.has(1):
            self.message = "Pas de dé"
            return
        
        # Assure qu'il y a une position cible et une direction en attente
        if not hasattr(self, 'target_position') or self.target_position is None:
            self.message = "Erreur : Pas de position cible"
            return
        
        if not hasattr(self, 'pending_direction') or self.pending_direction is None:
            self.message = "Erreur : Pas de direction en attente"
            return
        
        success, new_rooms = self.room_selector.reroll(
            self.target_position[0], self.target_position[1], 
            self.mansion, self.player,
            required_direction=self.pending_direction
        )
        
        if success:
            if new_rooms and len(new_rooms) > 0:
                self.available_rooms = new_rooms
                # Vérifiez que l'index se situe dans la plage valide.
                self.selected_room_index = min(self.selected_room_index, len(new_rooms) - 1)
                self.selected_room_index = max(0, self.selected_room_index)
                self.message = "Pièces retriées avec le dé"
            else:
                self.message = "Aucune pièce disponible après le nouveau tirage"
                self.state = GameState.PLAYING
        else:
            self.message = "Impossible de retier"
    
    def restart(self):
        """Redémarre le jeu"""
        # Réinitialise
        self.mansion = Mansion()
        self.player = Player()
        self.room_templates = create_room_templates()
        self.room_selector = RoomSelector(self.room_templates)
        
        self.state = GameState.PLAYING
        self.selected_direction = None
        self.available_rooms = []
        self.selected_room_index = 0
        self.target_position = None
        self.message = ""
        self.game_over_message = ""
    
    def get_current_room(self):
        """Obtient la pièce actuelle"""
        return self.mansion.get_room(self.player.row, self.player.col)
    
    def update(self):
        """Met à jour l'état du jeu"""
        # Vérifie les conditions de fin de jeu
        if self.state == GameState.PLAYING:
            if self.mansion.check_win_condition(self.player):
                self.state = GameState.GAME_OVER
                self.game_over_message = "🎉 Félicitations ! Vous avez atteint le hall d'entrée avec succès ! Victoire du jeu !"
                # Assurez-vous que le verrouillage du téléphone portable a été déverrouillé.
                self.is_moving = False
            elif self.mansion.check_lose_condition(self.player)[0]:
                self.state = GameState.GAME_OVER
                lose_reason = self.mansion.check_lose_condition(self.player)[1]
                self.game_over_message = f"Fin du jeu:{lose_reason}"
                # Assurez-vous que le verrouillage du téléphone portable a été déverrouillé.
                self.is_moving = False

