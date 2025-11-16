"""
Définition de la classe d'objets
"""
import random
from enum import Enum


class ItemType(Enum):
    """Enumération des types d'objets"""
    CONSUMABLE = "Consommable"
    PERMANENT = "Article permanent"
    FOOD = "Nourriture"
    CONTAINER = "Conteneur"
    INTERACTABLE = "Objet interactif"


class Item:
    """Classe de base des objets"""
    
    def __init__(self, name, item_type, description=""):
        """
        Initialisation de l'objet
        
        Args:
            name: Nom de l'objet
            item_type: Type d'objet
            description: Description de l'objet
        """
        self.name = name
        self.item_type = item_type
        self.description = description
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Item({self.name})"


class FoodItem(Item):
    """Objet nourriture, peut restaurer des pas"""
    
    def __init__(self, name, steps_restored):
        """
        Initialisation de l'objet nourriture
        
        Args:
            name: Nom de la nourriture
            steps_restored: Nombre de pas restaurés
        """
        super().__init__(name, ItemType.FOOD)
        self.steps_restored = steps_restored
    
    def consume(self, player):
        """
        Consommer la nourriture et restaurer des pas
        
        Args:
            player: Objet Player
        """
        player.inventory.add_steps(self.steps_restored)
        return f"A mangé {self.name}, a restauré {self.steps_restored} pas !"


class ConsumableItem(Item):
    """Objet consommable (pièces, gemmes, clés, dés)"""
    
    def __init__(self, name, initial_amount=0):
        """
        Initialisation de l'objet consommable
        
        Args:
            name: Nom de l'objet
            initial_amount: Quantité initiale
        """
        super().__init__(name, ItemType.CONSUMABLE)
        self.amount = initial_amount
    
    def add(self, amount):
        """Augmenter la quantité"""
        self.amount += amount
    
    def remove(self, amount):
        """Réduire la quantité, retourner si réussite"""
        if self.amount >= amount:
            self.amount -= amount
            return True
        return False
    
    def has(self, amount=1):
        """Vérifier si quantité suffisante"""
        return self.amount >= amount


class PermanentItem(Item):
    """Article permanent"""
    
    def __init__(self, name, description=""):
        """
        Initialisation de l'article permanent
        
        Args:
            name: Nom de l'objet
            description: Description de l'objet
        """
        super().__init__(name, ItemType.PERMANENT, description)
        self.count = 0  # Certains objets permanents peuvent être multiples
    
    def add(self):
        """Ajouter un article permanent"""
        self.count += 1
    
    def has(self):
        """Vérifier possession"""
        return self.count > 0
    
    def get_count(self):
        """Obtenir la quantité"""
        return self.count


class TreasureChest(Item):
    """Coffre, peut être ouvert avec une clé ou un marteau"""
    
    def __init__(self):
        super().__init__("Coffre", ItemType.CONTAINER)
        self.opened = False
        self.contents = []
    
    def generate_contents(self, base_probability=1.0):
        """
        Génération du contenu du coffre
        
        Args:
            base_probability: Probabilité de base (effets type patte de lapin)
        """
        if random.random() < 0.3 * base_probability:
            self.contents.append(("pièces", random.randint(5, 20)))
        if random.random() < 0.4 * base_probability:
            self.contents.append(("clés", random.randint(1, 2)))
        if random.random() < 0.3 * base_probability:
            self.contents.append(("gemmes", random.randint(1, 2)))
        if random.random() < 0.2 * base_probability:
            self.contents.append(("dés", 1))
        if random.random() < 0.1 * base_probability:
            foods = [
                ("Pomme", 2),
                ("Banane", 3),
                ("Gâteau", 10),
                ("Sandwich", 15)
            ]
            food_name, steps = random.choice(foods)
            self.contents.append((food_name, steps))
    
    def open_with_key(self, player):
        """Ouvrir le coffre avec une clé"""
        if self.opened:
            return None, "Le coffre a déjà été ouvert"
        if not player.inventory.keys.has(1):
            return None, "Clés insuffisantes"
        
        player.inventory.keys.remove(1)
        self.opened = True
        self.generate_contents(player.inventory.get_item_find_probability())
        return self.contents, "Coffre ouvert avec une clé"
    
    def open_with_hammer(self, player):
        """Ouvrir le coffre avec un marteau"""
        if self.opened:
            return None, "Le coffre a déjà été ouvert"
        if not player.inventory.hammer.has():
            return None, "Pas de marteau"
        
        self.opened = True
        self.generate_contents(player.inventory.get_item_find_probability())
        return self.contents, "Coffre brisé avec un marteau"


class DiggingSpot(Item):
    """Point de fouille, peut être creusé avec une pelle"""
    
    def __init__(self):
        super().__init__("Point de fouille", ItemType.INTERACTABLE)
        self.dug = False
        self.contents = []
    
    def generate_contents(self, base_probability=1.0):
        """
        Génération du contenu à la fouille
        
        Args:
            base_probability: Probabilité de base
        """
        if random.random() < 0.5 * base_probability:
            self.contents.append(("pièces", random.randint(3, 15)))
        if random.random() < 0.3 * base_probability:
            self.contents.append(("clés", 1))
        if random.random() < 0.2 * base_probability:
            self.contents.append(("gemmes", 1))
        if random.random() < 0.1 * base_probability:
            permanent_items = ["Pelle", "Marteau", "Kit de crochetage", "Détecteur de métaux", "Patte de lapin"]
            self.contents.append(("Article permanent", random.choice(permanent_items)))
    
    def dig(self, player):
        """Creuser"""
        if self.dug:
            return None, "Déjà fouillé ici"
        if not player.inventory.shovel.has():
            return None, "Pas de pelle"
        
        self.dug = True
        self.generate_contents(player.inventory.get_item_find_probability())
        return self.contents, "Fouille terminée"


class Locker(Item):
    """Casier, uniquement dans le vestiaire, s’ouvre avec une clé"""
    
    def __init__(self):
        super().__init__("Casier", ItemType.CONTAINER)
        self.opened = False
        self.contents = []
    
    def generate_contents(self, base_probability=1.0):
        """Générer le contenu du casier"""
        if random.random() < 0.4 * base_probability:
            self.contents.append(("pièces", random.randint(5, 25)))
        if random.random() < 0.3 * base_probability:
            self.contents.append(("clés", random.randint(1, 3)))
        if random.random() < 0.2 * base_probability:
            self.contents.append(("gemmes", random.randint(1, 3)))
    
    def open(self, player):
        """Ouvrir le casier avec une clé"""
        if self.opened:
            return None, "Le casier a déjà été ouvert"
        if not player.inventory.keys.has(1):
            return None, "Clés insuffisantes"
        
        player.inventory.keys.remove(1)
        self.opened = True
        self.generate_contents(player.inventory.get_item_find_probability())
        return self.contents, "Casier ouvert avec une clé"
