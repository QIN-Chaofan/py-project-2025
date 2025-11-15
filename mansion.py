"""
Classe de gestion de la grille du Manoir
"""
import config
from room import Room


class Mansion:
    """Classe Manoir, gère la grille 5x9 et la disposition des pièces"""
    
    def __init__(self):
        """Initialise le manoir"""
        self.grid = [[None for _ in range(config.GRID_COLS)] 
                     for _ in range(config.GRID_ROWS)]
        self.entrance_room = None
        self.front_hall_room = None
        self._initialize_entrance()
    
    def _initialize_entrance(self):
        """Initialise la pièce d'entrée"""
        entrance = Room(
            name="Hall d'entrée",
            color="BLUE",
            rarity=0,
            gem_cost=0,
            doors=['UP'],  # La seule entrée est une porte orientée vers le haut.
            image_path="images/pièce ordinaire.png"  # L'entrée utilise l'image de pièce ordinaire
        )
        entrance.set_position(config.ENTRANCE_ROW, config.ENTRANCE_COL)
        entrance.explored = True
        self.set_room(config.ENTRANCE_ROW, config.ENTRANCE_COL, entrance)
        self.entrance_room = entrance
        # S'assurer que la porte de l'entrée vers le haut est déverrouillée (pour faciliter le début du jeu)
        if 'UP' in entrance.door_objects:
            entrance.door_objects['UP'].lock_level = 0
    
    def set_room(self, row, col, room):
        """
        Définit la pièce à la position spécifiée
        
        Args:
            row: Position en ligne
            col: Position en colonne
            room: Objet Room
        """
        if 0 <= row < config.GRID_ROWS and 0 <= col < config.GRID_COLS:
            room.set_position(row, col)
            self.grid[row][col] = room
            
            # Si c'est le hall d'entrée (Front Hall), l'enregistrer
            if room.name == "Hall d'entrée":
                self.front_hall_room = room
    
    def get_room(self, row, col):
        """
        Obtient la pièce à la position spécifiée
        
        Args:
            row: Position en ligne
            col: Position en colonne
        
        Returns:
            Objet Room ou None
        """
        if 0 <= row < config.GRID_ROWS and 0 <= col < config.GRID_COLS:
            return self.grid[row][col]
        return None
    
    def count_explored_rooms(self):
        """Compte le nombre de pièces explorées"""
        count = 0
        for row in range(config.GRID_ROWS):
            for col in range(config.GRID_COLS):
                room = self.grid[row][col]
                if room and room.explored:
                    count += 1
        return count
    
    def get_adjacent_room(self, row, col, direction):
        """
        Obtient la pièce adjacente
        
        Args:
            row: Ligne actuelle
            col: Colonne actuelle
            direction: Direction
        
        Returns:
            Objet Room ou None
        """
        if direction not in config.DIRECTIONS:
            return None
        
        dr, dc = config.DIRECTIONS[direction]
        new_row = row + dr
        new_col = col + dc
        
        return self.get_room(new_row, new_col)
    
    def check_door_connection(self, row, col, direction, target_row, target_col):
        """
        Vérifie si la connexion de la porte est correcte
        
        Args:
            row: Ligne de la pièce actuelle
            col: Colonne de la pièce actuelle
            direction: Direction de la porte
            target_row: Ligne de la pièce cible
            target_col: Colonne de la pièce cible
        
        Returns:
            bool: La connexion est-elle correcte
        """
        dr, dc = config.DIRECTIONS[direction]
        expected_row = row + dr
        expected_col = col + dc
        
        return expected_row == target_row and expected_col == target_col
    
    def is_edge_position(self, row, col):
        """
        Vérifie si la position est sur le bord
        
        Args:
            row: Position en ligne
            col: Position en colonne
        
        Returns:
            bool:Est-ce sur le bord
        """
        return (row == 0 or row == config.GRID_ROWS - 1 or 
                col == 0 or col == config.GRID_COLS - 1)
    
    def is_last_row(self, row):
        """Vérifie si c'est la dernière ligne (ligne du Hall d'entrée)"""
        return row == config.FRONT_HALL_ROW
    
    def get_all_rooms(self):
        """Obtient toutes les pièces placées"""
        rooms = []
        for row in range(config.GRID_ROWS):
            for col in range(config.GRID_COLS):
                room = self.grid[row][col]
                if room:
                    rooms.append(room)
        return rooms
    
    def check_win_condition(self, player):
        """
        Vérifie si la condition de victoire est remplie
        
        Args:
            player: Player objet
        
        Returns:
            bool: Est-ce que le Hall d'entrée est atteint
        """
        #Obtient la pièce à la position actuelle du joueur
        current_room = self.get_room(player.row, player.col)
        
        #Méthode 1: Vérifie si la pièce actuelle est le Hall d'entrée (la méthode la plus directe)
        if current_room is not None and current_room.name == "Hall d'entrée":
            return True
        
        # Méthode 2: Si front_hall_room est défini, vérifie si la position correspond (méthode alternative)
        if self.front_hall_room is not None:
            if (player.row == self.front_hall_room.row and 
                player.col == self.front_hall_room.col):
                return True
        
        # Méthode 3: Vérifie si à la position standard du Hall d'entrée (config.FRONT_HALL_ROW, config.FRONT_HALL_COL)
        # Et si la pièce actuelle est le Hall d'entrée (empêche les cas où la position correspond mais la pièce n'est pas le Hall d'entrée)
        if (player.row == config.FRONT_HALL_ROW and 
            player.col == config.FRONT_HALL_COL and
            current_room is not None and 
            current_room.name == "Hall d'entrée"):
            return True
        
        return False
    
    def check_lose_condition(self, player):
        """
        Vérifie si la condition de défaite est remplie (ne peut pas avancer)
        
        Args:
            player: Player objet
        
        Returns:
            tuple: (Défaite, Raison)
        """
        # Vérifie si l'on peut continuer à avancer
        current_room = self.get_room(player.row, player.col)
        if current_room is None:
            return True, "Pas de pièce à la position actuelle"
        
        # Vérifie les pas
        if player.inventory.steps.amount <= 0:
            # Lorsque les pas sont à 0, vérifie si la pièce actuelle contient des objets qui peuvent restaurer les pas
            # S'il y en a, donne au joueur la chance de les ramasser, ne déclare pas immédiatement la défaite
            has_recoverable_items = False
            for item in current_room.items:
                # Vérifie s'il y a de la nourriture pour restaurer les pas
                if isinstance(item, tuple):
                    item_name = item[0]
                    if item_name in ["Pomme", "Banane", "Gâteau", "Sandwich", "Grand repas"]:
                        has_recoverable_items = True
                        break
                elif hasattr(item, "name"):
                    if item.name in ["Pomme", "Banane", "Gâteau", "Sandwich", "Grand repas"]:
                        has_recoverable_items = True
                        break
                    # Vérifie s'il y a des pièces d'or pour acheter de la nourriture (s'il y a une boutique)
                    if item.name == "pièces" and current_room.effects and current_room.effects.get("shop"):
                        has_recoverable_items = True
                        break
            
            # Si les pas sont à 0 et qu'il n'y a pas d'objets restaurateurs, déclare la défaite
            if not has_recoverable_items:
                return True, "Pas épuisés"
        
        # Vérifie s'il y a des portes qui peuvent être ouvertes
        # Doit vérifier s'il y a des portes menant à une nouvelle pièce (position vide) ou à une pièce explorée
        has_available_door = False
        opened_doors_count = 0
        openable_doors_count = 0
        opened_door_directions = []
        openable_door_directions = []
        
        for direction in current_room.door_objects:
            door = current_room.door_objects[direction]
            dr, dc = config.DIRECTIONS[direction]
            target_row = player.row + dr
            target_col = player.col + dc
            
            # Vérifie si la position cible est dans la grille
            if not (0 <= target_row < config.GRID_ROWS and 0 <= target_col < config.GRID_COLS):
                continue
            
            # Vérifie si la porte peut être ouverte ou est déjà ouverte
            if door.opened:
                opened_doors_count += 1
                opened_door_directions.append(direction)
                has_available_door = True
                # La porte est ouverte, le mouvement est possible (quelle que soit la présence d'une pièce cible)
                # Pas besoin de break, continuer à vérifier toutes les portes pour le débogage
            else:
                # La porte n'est pas ouverte, vérifie si elle peut être ouverte
                can_open, _ = door.can_open(player)
                if can_open:
                    openable_doors_count += 1
                    openable_door_directions.append(direction)
                    has_available_door = True
                    # Porte qui peut être ouverte, le mouvement est possible (quelle que soit la présence d'une pièce cible)
                    # Pas besoin de break, continuer à vérifier toutes les portes pour le débogage
        
        # S'il y a une porte disponible (ouverte ou ouvrable), ne déclare pas la défaite
        if has_available_door:
            return False, None
        
        # Aucune porte disponible
        # Ajoute des informations de débogage détaillées
        all_door_directions = list(current_room.door_objects.keys())
        debug_msg = (f"Aucune voie pour continuer (Portes ouvertes : {opened_doors_count}{opened_door_directions}, "
                    f"Portes ouvrables :{openable_doors_count}{openable_door_directions}, "
                    f"Nombre total de portes : {len(current_room.door_objects)}{all_door_directions})")
        return True, debug_msg

