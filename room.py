"""
Définition de la classe Room
"""
import random
from item import FoodItem, TreasureChest, DiggingSpot, Locker, ConsumableItem
from door import Door
import config


class Room:
    """Classe Salle"""
    
    def __init__(self, name, color="BLUE", rarity=0, gem_cost=0, 
                 doors=None, items=None, effects=None, placement_condition=None,
                 image_path=None):
        """
        Initialiser la salle
        
        Args:
            name: Nom de la salle
            color: Couleur de la salle (YELLOW, GREEN, PURPLE, ORANGE, RED, BLUE)
            rarity: Niveau de rareté (0-3)
            gem_cost: Coût en gemmes
            doors: Liste des directions des portes, ex: ['UP', 'DOWN', 'LEFT', 'RIGHT']
            items: Liste des objets dans la salle
            effects: Effets spéciaux de la salle (dictionnaire ou fonction)
            placement_condition: Fonction de condition de placement, accepte (row, col) et retourne bool
            image_path: Chemin de l'image de la salle
        """
        self.name = name
        self.color = color
        self.rarity = rarity
        self.gem_cost = gem_cost
        self.doors = doors or []
        self.items = items or []
        self.effects = effects or {}
        self.placement_condition = placement_condition
        self.image_path = image_path
        
        # Position de la salle dans la grille
        self.row = None
        self.col = None
        
        # Objets porte de la salle (instances de Door)
        self.door_objects = {}
        
        # Si elle a été explorée
        self.explored = False
    
    def set_position(self, row, col):
        """Définir la position de la salle dans la grille"""
        # Sauvegarder l'état des portes ouvertes
        opened_doors = set()
        if hasattr(self, 'door_objects') and self.door_objects:
            for direction, door in self.door_objects.items():
                if door.opened:
                    opened_doors.add(direction)
        
        self.row = row
        self.col = col
        # Créer les objets porte
        self._create_doors()
        
        # Restaurer l'état des portes ouvertes
        for direction in opened_doors:
            if direction in self.door_objects:
                self.door_objects[direction].opened = True
    
    def _create_doors(self):
        """Créer des objets Door en fonction des directions des portes"""
        self.door_objects = {}
        for direction in self.doors:
            self.door_objects[direction] = Door(direction, row=self.row)
    
    def can_place_at(self, row, col, mansion):
        """
        Vérifier si la salle peut être placée à la position spécifiée
        
        Args:
            row: Position de la ligne
            col: Position de la colonne
            mansion: Objet Mansion
        
        Returns:
            tuple: (peut_placer, raison)
        """
        # Vérifier la condition de placement
        if self.placement_condition:
            if not self.placement_condition(row, col, mansion):
                return False, "Ne satisfait pas la condition de placement de la salle"
        
        # Vérifier les bordures
        for direction in self.doors:
            dr, dc = config.DIRECTIONS[direction]
            new_row, new_col = row + dr, col + dc
            if not (0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS):
                # La porte mène hors de la grille, vérifier si elle est connectée à une salle existante
                # Si c'est la première salle, autoriser
                if mansion.count_explored_rooms() == 0:
                    continue
                # Sinon, ne pas autoriser la porte à mener hors de la grille
                return False, "La porte ne peut pas mener hors de la grille"
        
        return True, "Peut être placée"
    
    def generate_items(self, inventory):
        """
        Générer des objets aléatoires en fonction du type de salle et de l'inventaire du joueur
        
        Args:
            inventory: Objet Inventory, utilisé pour considérer les effets des objets permanents
        """
        base_probability = inventory.get_item_find_probability()
        key_coin_prob = inventory.get_key_coin_probability()
        
        # Générer des objets en fonction de la couleur de la salle
        if self.color == "GREEN":
            # Salle VERTE : Forte probabilité de contenir des gemmes, des points à creuser, des objets permanents
            if random.random() < 0.6 * base_probability:
                self.items.append(ConsumableItem("Gemme", random.randint(1, 3)))
            if random.random() < 0.4 * base_probability:
                self.items.append(DiggingSpot())
            if random.random() < 0.1 * base_probability:
                permanent_items = ["Pelle", "Marteau", "Kit de crochetage", "Détecteur de métaux", "Patte de lapin porte-bonheur"]
                self.items.append(("Objet Permanent", random.choice(permanent_items)))
        
        elif self.color == "YELLOW":
            # Salle JAUNE (Magasin) : Contient généralement des pièces d'or
            if random.random() < 0.5:
                self.items.append(ConsumableItem("Pièces d'or", random.randint(10, 30)))
        
        elif self.color == "PURPLE":
            # Salle VIOLETTE (Chambre) : Peut contenir de la nourriture
            if random.random() < 0.5 * base_probability:
                foods = [
                    FoodItem("Pomme", 2),
                    FoodItem("Banane", 3),
                    FoodItem("Gâteau", 10)
                ]
                self.items.append(random.choice(foods))
        
        elif self.color == "BLUE":
            # Salle BLEUE : Objets divers
            if random.random() < 0.3 * key_coin_prob:
                self.items.append(ConsumableItem("Clé", random.randint(1, 2)))
            if random.random() < 0.3 * key_coin_prob:
                self.items.append(ConsumableItem("Pièces d'or", random.randint(5, 15)))
            if random.random() < 0.2 * base_probability:
                self.items.append(ConsumableItem("Gemme", 1))
            if random.random() < 0.1 * base_probability:
                self.items.append(TreasureChest())
        
        # Génération d'objets pour les salles spéciales (définie dans rooms_data.py)
        # Note : Les articles du magasin (quand effects["shop"] est True) ne doivent pas être générés comme des objets à ramasser
        if "items" in self.effects and not self.effects.get("shop"):
            for item_spec in self.effects["items"]:
                # Vérifier s'il y a un champ "probability" (les articles du magasin n'en ont pas, seulement les objets de salle spéciale)
                if "probability" in item_spec:
                    if random.random() < item_spec.get("probability", 1.0) * base_probability:
                        self.items.append(item_spec["item"])
                else:
                    # Pas de champ "probability", ajouter directement (peut être un autre type de définition d'objet)
                    pass
    
    def apply_effect(self, player, mansion):
        """
        Appliquer l'effet de la salle
        
        Args:
            player: Objet Player
            mansion: Objet Mansion
        """
        # La salle VIOLETTE restaure des pas
        if self.color == "PURPLE":
            steps = random.randint(2, 5)
            player.inventory.add_steps(steps)
            return f"Repos dans {self.name}, {steps} pas restaurés"
        
        # La salle ROUGE peut réduire les pas
        if self.color == "RED" and "lose_steps" in self.effects:
            steps_lost = self.effects["lose_steps"]
            player.inventory.steps.remove(min(steps_lost, player.inventory.steps.amount))
            return f"Perdu {steps_lost} pas dans {self.name}"
        
        # Autres effets spéciaux
        if "effect" in self.effects:
            effect_func = self.effects["effect"]
            return effect_func(player, mansion)
        
        return None
    
    def get_door(self, direction):
        """Obtenir la porte dans la direction spécifiée"""
        return self.door_objects.get(direction)
    
    def has_door(self, direction):
        """Vérifier s'il y a une porte dans la direction spécifiée"""
        return direction in self.door_objects
    
    def __str__(self):
        return f"Room({self.name}, {self.color}, Rareté {self.rarity}, Coût {self.gem_cost} gemmes)"





