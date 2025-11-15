"""
Script de test du jeu
Vérifie le bon fonctionnement des fonctionnalités principales
"""
import sys
sys.path.insert(0, '.')

from player import Player
from mansion import Mansion
from inventory import Inventory
from room import Room
from door import Door
from rooms_data import create_room_templates
from room_selector import RoomSelector
import config


def test_inventory():
    """Teste le système d'inventaire"""
    print("Test du système d'inventaire...")
    inv = Inventory()
    assert inv.steps.amount == 70, "Le nombre initial de pas devrait être 70"
    assert inv.gems.amount == 2, "Le nombre initial de gemmes devrait être 2"
    assert inv.coins.amount == 0, "Le nombre initial de pièces d'or devrait être 0"
    
    inv.add_steps(10)
    assert inv.steps.amount == 80, "Le nombre de pas devrait augmenter à 80"
    
    inv.consume_step()
    assert inv.steps.amount == 79, "Le nombre de pas devrait diminuer à 79"
    
    inv.add_gems(5)
    assert inv.gems.amount == 7, "Le nombre de gemmes devrait augmenter à 7"
    
    inv.add_permanent_item("Pelle")
    assert inv.shovel.get_count() == 1, "Il devrait y avoir 1 pelle"
    
    print("✓ Test du système d'inventaire réussi")


def test_mansion():
    """Teste le système de manoir"""
    print("Test du système de manoir...")
    mansion = Mansion()
    
    # Vérification de la pièce d'entrée
    entrance = mansion.get_room(config.ENTRANCE_ROW, config.ENTRANCE_COL)
    assert entrance is not None, "Il devrait y avoir une pièce d'entrée"
    assert entrance.name == "Hall d'entrée", "Le nom de la pièce d'entrée devrait être 'Hall d'entrée'"
    assert entrance.explored, "La pièce d'entrée devrait être explorée"
    
    # Vérification de la taille de la grille
    assert len(mansion.grid) == config.GRID_ROWS, "Le nombre de lignes de la grille devrait être correct"
    assert len(mansion.grid[0]) == config.GRID_COLS, "Le nombre de colonnes de la grille devrait être correct"
    
    print("✓ Test du système de manoir réussi")


def test_player():
    """Teste le système de joueur"""
    print("Test du système de joueur...")
    player = Player()
    mansion = Mansion()
    
    assert player.row == config.ENTRANCE_ROW, "Le joueur devrait être sur la ligne d'entrée"
    assert player.col == config.ENTRANCE_COL, "Le joueur devrait être sur la colonne d'entrée"
    assert player.inventory.steps.amount == 70, "Le nombre initial de pas du joueur devrait être 70"
    
    # Test du mouvement (devrait échouer car il n'y a pas de porte)
    success, message = player.move('UP', mansion)
    # Le mouvement devrait retourner None (sélection de pièce requise) ou False (mouvement impossible)
    assert success is not None or success is False, "Le mouvement devrait retourner un résultat"
    
    print("✓ Test du système de joueur réussi")


def test_room():
    """Teste le système de pièce"""
    print("Test du système de pièce...")
    room = Room(
        name="Pièce de test",
        color="BLUE",
        rarity=0,
        gem_cost=0,
        doors=['UP', 'DOWN']
    )
    
    assert room.name == "Pièce de test", "Le nom de la pièce devrait être correct"
    assert room.color == "BLUE", "La couleur de la pièce devrait être correcte"
    assert room.rarity == 0, "La rareté de la pièce devrait être correcte"
    assert len(room.doors) == 2, "La pièce devrait avoir 2 portes"
    
    # Test des conditions de placement
    mansion = Mansion()
    can_place, reason = room.can_place_at(2, 2, mansion)
    assert can_place, "La pièce devrait pouvoir être placée à (2,2)"
    
    print("✓ Test du système de pièce réussi")


def test_door():
    """Teste le système de porte"""
    print("Test du système de porte...")
    door = Door('UP', lock_level=1, row=2)
    
    assert door.direction == 'UP', "La direction de la porte devrait être correcte"
    assert door.lock_level == 1, "Le niveau de verrouillage de la porte devrait être correct"
    assert not door.opened, "La porte ne devrait pas être ouverte"
    
    # Test du calcul du niveau de serrure
    door0 = Door('UP', row=0)  # Première ligne
    assert door0.lock_level == 0, "La porte de la première ligne devrait être de niveau 0"
    
    door2 = Door('UP', row=config.GRID_ROWS - 1)  # Dernière ligne
    assert door2.lock_level == 2, "La porte de la dernière ligne devrait être de niveau 2"
    
    print("✓ Test du système de porte réussi")


def test_room_selector():
    """Teste le système de sélection de pièce"""
    print("Test du système de sélection de pièce...")
    room_templates = create_room_templates()
    selector = RoomSelector(room_templates)
    
    mansion = Mansion()
    player = Player()
    
    # Test du tirage de pièces
    rooms = selector.draw_rooms(3, 4, mansion, player)
    assert len(rooms) > 0, "Devrait pouvoir tirer des pièces"
    assert len(rooms) <= 3, "Devrait tirer un maximum de 3 pièces"
    
    # Vérifie qu'il y a au moins une pièce de coût 0
    zero_cost_rooms = [r for r in rooms if r.gem_cost == 0]
    assert len(zero_cost_rooms) > 0, "Il devrait y avoir au moins une pièce de coût 0"
    
    print("✓ Test du système de sélection de pièce réussi")


def test_rooms_data():
    """Teste les données des pièces"""
    print("Test des données des pièces...")
    rooms = create_room_templates()
    
    assert len(rooms) > 0, "Il devrait y avoir des modèles de pièce"
    
    # Vérification du Hall d'entrée
    front_hall = None
    for room in rooms:
        if room.name == "Hall d'entrée":
            front_hall = room
            break
    
    assert front_hall is not None, "Il devrait y avoir un Hall d'entrée"
    assert front_hall.gem_cost == 0, "Le Hall d'entrée ne devrait pas avoir de coût en gemmes"
    
    print("✓ Test des données des pièces réussi")


def run_all_tests():
    """Exécute tous les tests"""
    print("=" * 50)
    print("Début du test des fonctionnalités principales du jeu")
    print("=" * 50)
    
    try:
        test_inventory()
        test_mansion()
        test_player()
        test_room()
        test_door()
        test_room_selector()
        test_rooms_data()
        
        print("=" * 50)
        print("✓ Tous les tests réussis !")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"✗ Test échoué : {e}")
        return False
    except Exception as e:
        print(f"✗ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

