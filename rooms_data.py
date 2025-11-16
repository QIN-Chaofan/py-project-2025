"""
Configuration des données des salles
Définit tous les types de salles et leurs propriétés
"""
from room import Room
from item import FoodItem, TreasureChest, DiggingSpot, Locker, ConsumableItem
import random


def create_room_templates():
    """
    Créer tous les modèles de salles
    
    Returns:
        list: liste d’objets Room
    """
    rooms = []
    
    # Hall d’entrée (déjà créé dans Mansion, pas répété ici)
    
    # Hall avant (salle objectif)
    front_hall = Room(
        name="Hall Avant",
        color="BLUE",
        rarity=0,
        gem_cost=0,
        doors=[],  # Le hall avant n’a pas de portes (point final)
        placement_condition=lambda row, col, mansion: row == 0,  # Ne peut être placé qu’à la première ligne
        image_path="images/HallAvant.png"
    )
    rooms.append(front_hall)
    
    # Salle bleue basique
    basic_room = Room(
        name="Salle Ordinaire",
        color="BLUE",
        rarity=0,
        gem_cost=0,
        doors=['UP', 'DOWN'],
        image_path="images/SalleOrdinaire.png"
    )
    rooms.append(basic_room)
    
    # Salle du trésor
    vault = Room(
        name="Salle du Trésor",
        color="BLUE",
        rarity=3,
        gem_cost=3,
        doors=['UP'],
        items=[ConsumableItem("Pièce d’or", 40)],
        image_path="images/SalleDuTresor.png"
    )
    rooms.append(vault)
    
    # Véranda (salle verte, uniquement en bordure)
    veranda = Room(
        name="Véranda",
        color="GREEN",
        rarity=2,
        gem_cost=2,
        doors=['UP', 'DOWN'],
        placement_condition=lambda row, col, mansion: mansion.is_edge_position(row, col),
        effects={
            "effect": lambda player, mansion: None,  # Augmente la probabilité de salle verte (géré dans room_selector)
            "increase_green_probability": True
        },
        image_path="images/Veranda.png"
    )
    rooms.append(veranda)
    
    # Bureau
    study = Room(
        name="Bureau",
        color="BLUE",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN', 'LEFT', 'RIGHT'],
        items=[ConsumableItem("Gemme", 1)],
        effects={
            "items": [
                {"item": TreasureChest(), "probability": 0.3}
            ]
        },
        image_path="images/Bureau.png"
    )
    rooms.append(study)
    
    # Cave
    cellar = Room(
        name="Cave",
        color="BLUE",
        rarity=1,
        gem_cost=1,
        doors=['UP'],
        items=[ConsumableItem("Clé", random.randint(1, 2))],
        image_path="images/Cave.png"
    )
    rooms.append(cellar)
    
    # Boutique (salle jaune)
    shop = Room(
        name="Boutique",
        color="YELLOW",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN', 'LEFT', 'RIGHT'],
        effects={
            "shop": True,
            "items": [
                {"name": "Clé", "price": 10, "item": ConsumableItem("Clé", 1)},
                {"name": "Gemme", "price": 15, "item": ConsumableItem("Gemme", 1)},
                {"name": "Dé", "price": 20, "item": ConsumableItem("Dé", 1)},
                {"name": "Pomme", "price": 5, "item": FoodItem("Pomme", 2)},
            ]
        },
        image_path="images/Boutique.png"
    )
    rooms.append(shop)
    
    # Chambre (salle violette)
    bedroom = Room(
        name="Chambre",
        color="PURPLE",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN'],
        image_path="images/Chambre.png"
    )
    rooms.append(bedroom)
    
    # Salle du fourneau : augmente la probabilité des salles rouges
    furnace = Room(
        name="Salle du Fourneau",
        color="RED",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN'],
        effects={
            "increase_color_weights": {"RED": 1.5}
        },
        image_path="images/SalleDuFourneau.png"
    )
    rooms.append(furnace)
    
    # Serre : augmente la probabilité des salles vertes
    greenhouse = Room(
        name="Serre",
        color="GREEN",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN', 'LEFT'],
        effects={
            "increase_color_weights": {"GREEN": 1.5}
        },
        image_path="images/Serre.png"
    )
    rooms.append(greenhouse)
    
    # Salle d’exposition solaire : augmente la probabilité des salles bleues
    solarium = Room(
        name="Solarium",
        color="BLUE",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'RIGHT'],
        effects={
            "increase_color_weights": {"BLUE": 1.3}
        },
        image_path="images/Solarium.png"
    )
    rooms.append(solarium)
    
    # Couloir (salle orange)
    corridor = Room(
        name="Couloir",
        color="ORANGE",
        rarity=0,
        gem_cost=0,
        doors=['UP', 'DOWN', 'LEFT', 'RIGHT'],
        image_path="images/Couloir.png"
    )
    rooms.append(corridor)
    
    # Salle dangereuse (rouge)
    dangerous_room = Room(
        name="Salle Dangereuse",
        color="RED",
        rarity=1,
        gem_cost=1,
        doors=['UP'],  # Peu de portes
        effects={
            "lose_steps": 5  # Perdre 5 pas
        },
        image_path="images/SalleDangereuse.png"
    )
    rooms.append(dangerous_room)
    
    # Jardin (salle verte)
    garden = Room(
        name="Jardin",
        color="GREEN",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN', 'LEFT'],
        image_path="images/Jardin.png"
    )
    rooms.append(garden)
    
    # Vestiaire (contient un casier)
    cloakroom = Room(
        name="Vestiaire",
        color="BLUE",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN'],
        items=[Locker()],
        image_path="images/Vestiaire.png"
    )
    rooms.append(cloakroom)
    
    # Cuisine (peut contenir de la nourriture)
    kitchen = Room(
        name="Cuisine",
        color="BLUE",
        rarity=1,
        gem_cost=1,
        doors=['UP', 'DOWN', 'LEFT', 'RIGHT'],
        effects={
            "items": [
                {"item": FoodItem("Sandwich", 15), "probability": 0.5},
                {"item": FoodItem("Repas Copieux", 25), "probability": 0.2}
            ]
        },
        image_path="images/Cuisine.png"
    )
    rooms.append(kitchen)
    
    # Ajouter des copies de certaines salles communes pour augmenter la taille du deck
    common_rooms = [basic_room, corridor, bedroom]
    for room_template in common_rooms:
        # Créer plusieurs copies pour les salles fréquentes
        for i in range(2):
            new_room = Room(
                name=room_template.name,
                color=room_template.color,
                rarity=room_template.rarity,
                gem_cost=room_template.gem_cost,
                doors=room_template.doors.copy(),
                effects=room_template.effects.copy() if room_template.effects else {},
                placement_condition=room_template.placement_condition,
                image_path=room_template.image_path
            )
            rooms.append(new_room)
    
    return rooms


def get_room_by_name(name, rooms_list):
    """
    Obtenir un modèle de salle selon son nom
    
    Args:
        name: nom de la salle
        rooms_list: liste de salles
    
    Returns:
        Objet Room ou None
    """
    for room in rooms_list:
        if room.name == name:
            return room
    return None


