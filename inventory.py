""" 
Classe de gestion de l'inventaire 
"""
from item import ConsumableItem, PermanentItem


class Inventory:
    """Gestion de l'inventaire du joueur"""
    
    def __init__(self, initial_steps=70, initial_coins=0, initial_gems=2, 
                 initial_keys=0, initial_dice=0):
        """
        Initialisation de l'inventaire
        
        Args:
            initial_steps: Pas initiaux
            initial_coins: Pièces initiales
            initial_gems: Gemmes initiales
            initial_keys: Clés initiales
            initial_dice: Dés initiaux
        """
        # Consommables
        self.steps = ConsumableItem("Pas", initial_steps)
        self.coins = ConsumableItem("pièces", initial_coins)
        self.gems = ConsumableItem("gemmes", initial_gems)
        self.keys = ConsumableItem("clés", initial_keys)
        self.dice = ConsumableItem("dés", initial_dice)
        
        # Articles permanents
        self.shovel = PermanentItem("Pelle", "Permet de creuser à certains endroits")
        self.hammer = PermanentItem("Marteau", "Peut casser les cadenas des coffres")
        self.lockpick = PermanentItem("Kit de crochetage", "Permet d’ouvrir des portes de niveau 1 sans consommer de clé")
        self.metal_detector = PermanentItem("Détecteur de métaux", "Augmente la probabilité de trouver des clés et des pièces")
        self.lucky_rabbit_foot = PermanentItem("Patte de lapin", "Augmente la probabilité de trouver des objets")
    
    def add_steps(self, amount):
        """Augmenter les pas"""
        self.steps.add(amount)
    
    def consume_step(self):
        """Consommer un pas, retourner si encore des pas disponibles"""
        if self.steps.has(1):
            self.steps.remove(1)
            return True
        return False
    
    def add_coins(self, amount):
        """Augmenter les pièces"""
        self.coins.add(amount)
    
    def remove_coins(self, amount):
        """Consommer des pièces"""
        return self.coins.remove(amount)
    
    def add_gems(self, amount):
        """Augmenter les gemmes"""
        self.gems.add(amount)
    
    def remove_gems(self, amount):
        """Consommer des gemmes"""
        return self.gems.remove(amount)
    
    def add_keys(self, amount):
        """Augmenter les clés"""
        self.keys.add(amount)
    
    def remove_keys(self, amount):
        """Consommer des clés"""
        return self.keys.remove(amount)
    
    def add_dice(self, amount):
        """Augmenter les dés"""
        self.dice.add(amount)
    
    def remove_dice(self, amount):
        """Consommer des dés"""
        return self.dice.remove(amount)
    
    def add_permanent_item(self, item_name):
        """Ajouter un article permanent"""
        if item_name == "Pelle":
            self.shovel.add()
        elif item_name == "Marteau":
            self.hammer.add()
        elif item_name == "Kit de crochetage":
            self.lockpick.add()
        elif item_name == "Détecteur de métaux":
            self.metal_detector.add()
        elif item_name == "Patte de lapin":
            self.lucky_rabbit_foot.add()

    
    def get_item_find_probability(self):
        """
        Obtenir le multiplicateur de probabilité de découverte (patte de lapin)
        
        Returns:
            float: multiplicateur
        """
        multiplier = 1.0
        if self.lucky_rabbit_foot.has():
            multiplier += 0.5 * self.lucky_rabbit_foot.get_count()
        return multiplier
    
    def get_key_coin_probability(self):
        """
        Obtenir le multiplicateur de probabilité de trouver des clés et des pièces
        (détecteur de métaux)
        
        Returns:
            float: multiplicateur
        """
        multiplier = 1.0
        if self.metal_detector.has():
            multiplier += 0.5 * self.metal_detector.get_count()
        return multiplier
    
    def get_dict(self):
        """Obtenir le dictionnaire de l'inventaire pour affichage"""
        return {
            "Consommables": {
                "Pas": self.steps.amount,
                "pièces": self.coins.amount,
                "gemmes": self.gems.amount,
                "clés": self.keys.amount,
                "dés": self.dice.amount
            },
            "Articles permanents": {
                "Pelle": self.shovel.get_count(),
                "Marteau": self.hammer.get_count(),
                "Kit de crochetage": self.lockpick.get_count(),
                "Détecteur de métaux": self.metal_detector.get_count(),
                "Patte de lapin": self.lucky_rabbit_foot.get_count()
            }
        }
