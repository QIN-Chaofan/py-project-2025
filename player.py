"""
Classe du joueur
"""
import config
from inventory import Inventory


class Player:
    """Classe du joueur"""
    
    def __init__(self, row=None, col=None):
        """
        Initialise le joueur
        
        Args:
            row: Position initiale en ligne
            col: Position initiale en colonne
        """
        self.inventory = Inventory()
        self.row = row if row is not None else config.ENTRANCE_ROW
        self.col = col if col is not None else config.ENTRANCE_COL
    
    def move(self, direction, mansion):
        """
        Déplace le joueur
        
        Args:
            direction: Direction de déplacement ('UP', 'DOWN', 'LEFT', 'RIGHT')
            mansion: Objet Mansion
        
        Returns:
            tuple: (Succès du mouvement, Message)
        """
        # Vérifier si la direction est valide
        if direction not in config.DIRECTIONS:
            return False, "Direction invalide"
        
        # Calculer la position cible
        dr, dc = config.DIRECTIONS[direction]
        new_row = self.row + dr
        new_col = self.col + dc
        
        # Vérifier les limites de la grille
        if not (0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS):
            return False, "Ne peut pas se déplacer en dehors de la grille"
        
        # Obtenir la pièce actuelle
        current_room = mansion.get_room(self.row, self.col)
        if current_room is None:
            return False, "Pas de pièce à l'emplacement actuel"
        
        # Vérifier s'il y a une porte dans la direction cible
        if not current_room.has_door(direction):
            return False, "Il n'y a pas de porte dans cette direction"
        
        # Obtenir la porte
        door = current_room.get_door(direction)
        
        #Vérifier s'il y a une pièce à la position cible
        target_room = mansion.get_room(new_row, new_col)
        if target_room is None:
            # Aucune pièce à l'emplacement cible, la sélection d'une pièce est requise
            # Tenter d'abord d'ouvrir la porte (si elle n'est pas ouverte)
            if not door.opened:
                success, message = door.open(self)
                if not success:
                    return False, message
            return None, "Sélection de pièce requise"
        
        # Il y a une pièce à l'emplacement cible, vérifier si l'on peut se déplacer vers une pièce déjà explorée
        # Si la pièce cible a été explorée, vérifier si la porte inverse est ouverte
        opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}[direction]
        opposite_door = target_room.door_objects.get(opposite)
        
        if target_room.explored:
            # La pièce cible a été explorée, vérifier si la porte inverse est ouverte
            if opposite_door is None:
                return False, f"La pièce cible n'a pas de porte dans la direction{opposite}"
            # Si la porte inverse n'est pas ouverte, l'ouvrir directement (permet le mouvement entre pièces explorées)
            # Note: Si la pièce a été explorée, elle a déjà été visitée, la porte devrait être ouverte
            # Mais si elle ne l'est pas pour une raison quelconque, nous l'ouvrons directement pour assurer le mouvement
            if not opposite_door.opened:
                opposite_door.opened = True
        
        # Vérifier si la porte est ouverte, sinon tenter de l'ouvrir
        if not door.opened:
            # Tenter d'ouvrir la porte
            success, message = door.open(self)
            if not success:
                # La porte ne peut pas être ouverte (clé nécessaire, mais non possédée), retourner l'échec
                return False, message
        
        # Si la pièce cible a été explorée, s'assurer que la porte inverse est également ouverte
        if target_room.explored and opposite_door and not opposite_door.opened:
            # La porte inverse devrait déjà être ouverte, mais si ce n'est pas le cas, l'ouvrir directement
            # Remarque : Si la pièce a été explorée, cela signifie que vous l'avez déjà visitée, et la porte devrait déjà être ouverte.
            # Toutefois, si pour une raison quelconque il n'est pas ouvert, nous l'ouvrirons directement afin de nous assurer qu'il peut être déplacé.
            opposite_door.opened = True
        
        # Après avoir confirmé le mouvement, consommer un pas (avant de changer de position)
        # Cela garantit que la consommation du pas est effectuée au bon moment, que ce soit pour une nouvelle pièce ou une pièce explorée
        if not self.inventory.consume_step():
            return False, "Pas insuffisants, impossible de se déplacer"
        
        # Déplacer la position du joueur (après avoir consommé le pas)
        self.row = new_row
        self.col = new_col
        
        # Ré-obtenir l'objet pièce actuel (position avant le mouvement), s'assurer d'utiliser l'objet réel dans la grille
        previous_row = self.row - dr
        previous_col = self.col - dc
        current_room_actual = mansion.get_room(previous_row, previous_col)
        if current_room_actual is None:
            return False, "La pièce à la position précédente n'existe pas"
        
        # Ré-obtenir l'objet pièce cible, s'assurer d'utiliser l'objet réel dans la grille
        target_room_actual = mansion.get_room(self.row, self.col)
        if target_room_actual is None:
            return False, "La pièce à la position cible n'existe pas"
        
        # Marquer la pièce comme explorée
        target_room_actual.explored = True
        
        # Ouvrir les portes bidirectionnelles : s'assurer que la porte de la pièce actuelle et la porte inverse de la pièce cible sont ouvertes
        # 1. S'assurer que la porte de la pièce actuelle (position avant le mouvement) est ouverte (doit être ouverte, sinon impossible de se déplacer)
        current_door = current_room_actual.door_objects.get(direction)
        if current_door:
            current_door.opened = True
        else:
            return False, f"La pièce actuelle n'a pas de porte dans la direction{direction}"
        
        # 2. Ouvrir la porte inverse de la pièce cible (C'est la clé ! Doit être ouverte, sinon impossible de revenir)
        opposite_door_actual = target_room_actual.door_objects.get(opposite)
        if opposite_door_actual:
            opposite_door_actual.opened = True
        else:
            # Si la porte inverse n'existe pas, cela signifie que la configuration de la pièce est problématique
            # Cela ne devrait pas se produire car la connectivité est assurée lors de la sélection des pièces
            return False, f"La pièce cible n'a pas de porte dans la direction{opposite}"
        
        # 3. Vérification supplémentaire: S'assurer que la pièce cible a bien une porte inverse et que l'état de la porte est enregistré
        # Ré-obtenir une fois pour s'assurer d'utiliser le dernier objet porte
        target_room_verify = mansion.get_room(self.row, self.col)
        if target_room_verify and target_room_verify.door_objects.get(opposite):
            target_room_verify.door_objects[opposite].opened = True
        
        # Appliquer l'effet de la pièce
        effect_message = target_room_actual.apply_effect(self, mansion)
        
        return True, f"Déplacement vers{target_room_actual.name}" + (f"，{effect_message}" if effect_message else "")
    
    def pick_up_item(self, item, mansion):
        """
        Ramasse un objet
        
        Args:
            item: Objet article ou tuple(item_name, amount)
            mansion: Objet Mansion(utilisé pour retirer l'article de la pièce)
        
        Returns:
            tuple: (Succès du ramassage, Message)
        """
        current_room = mansion.get_room(self.row, self.col)
        if current_room is None:
            return False, "Il n'y a pas de chambres disponibles à cet emplacement."
        
        # Traiter les différents types d'objets
        if isinstance(item, tuple):
            item_name, amount = item
            if item_name == "pièces":
                self.inventory.add_coins(amount)
                return True, f"Ramassé{amount}pièces"
            elif item_name == "gemmes":
                self.inventory.add_gems(amount)
                return True, f"Ramassé{amount}gemmes"
            elif item_name == "clés":
                self.inventory.add_keys(amount)
                return True, f"Ramassé{amount}clés"
            elif item_name == "dés":
                self.inventory.add_dice(amount)
                return True, f"Ramassé{amount}dés"
            elif item_name == "Article permanent":
                self.inventory.add_permanent_item(amount)
                return True, f"Obtenu l'article permanent：{amount}"
            elif item_name in ["Pomme", "Banane", "Gâteau", "Sandwich", "Grand repas"]:
                # Nourriture consommée directement
                from item import FoodItem
                food_map = {
                    "Pomme": 2,
                    "Banane": 3,
                    "Gâteau": 10,
                    "Sandwich": 15,
                    "Grand repas": 25
                }
                steps = food_map.get(item_name, 0)
                self.inventory.add_steps(steps)
                return True, f"Consommé{item_name},restauré{steps}pas"
        
        elif hasattr(item, 'name'):
            # Objet article
            if item.name in ["Pomme", "Banane", "Gâteau", "Sandwich", "Grand repas"]:
                # Nourriture
                if hasattr(item, 'consume'):
                    message = item.consume(self)
                    # Retirer de la pièce
                    if item in current_room.items:
                        current_room.items.remove(item)
                    return True, message
            elif item.name == "pièces":
                self.inventory.add_coins(item.amount)
                if item in current_room.items:
                    current_room.items.remove(item)
                return True, f"Ramassé{item.amount}pièces"
            elif item.name == "gemmes":
                self.inventory.add_gems(item.amount)
                if item in current_room.items:
                    current_room.items.remove(item)
                return True, f"Ramassé{item.amount}gemmes"
            elif item.name == "	clés":
                self.inventory.add_keys(item.amount)
                if item in current_room.items:
                    current_room.items.remove(item)
                return True, f"Ramassé{item.amount}clés"
            elif item.name == "dés":
                self.inventory.add_dice(item.amount)
                if item in current_room.items:
                    current_room.items.remove(item)
                return True, f"Ramassé{item.amount}dés"
        
        return False, "Impossible de ramasser cet article"
    
    def get_position(self):
        """Obtient la position actuelle"""
        return (self.row, self.col)
    
    def __str__(self):
        return f"Player(Position: ({self.row}, {self.col}), Pas: {self.inventory.steps.amount})"



