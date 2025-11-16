"""
Système de sélection des salles
Gère la logique de tirage et de sélection des salles
"""
import random
import copy
import config
from room import Room


class RoomSelector:
    """Sélecteur de salles, gère le tirage et la sélection des salles"""
    
    def __init__(self, room_templates):
        """
        Initialiser le sélecteur de salles
        
        Args:
            room_templates: liste de modèles de salles
        """
        self.room_templates = room_templates
        self.available_rooms = copy.deepcopy(room_templates)  # Pioche de salles disponibles
        # Accumulation des effets globaux
        self.green_prob_multiplier_global = 1.0
        # Multiplicateurs globaux par couleur
        self.color_multipliers = {
            "YELLOW": 1.0,
            "GREEN": 1.0,
            "PURPLE": 1.0,
            "ORANGE": 1.0,
            "RED": 1.0,
            "BLUE": 1.0,
        }
    
    def draw_rooms(self, row, col, mansion, player, count=3, required_direction=None):
        """
        Tirer des salles pour les proposer au joueur
        
        Args:
            row: ligne cible
            col: colonne cible
            mansion: objet Mansion
            player: objet Player
            count: nombre de salles à tirer (3 par défaut)
        
        Returns:
            list: liste d’objets Room
        """
        # Filtrer les salles disponibles : doivent respecter la condition de placement
        valid_rooms = []
        for room in self.available_rooms:
            can_place, reason = room.can_place_at(row, col, mansion)
            if can_place:
                # Si une direction est requise, la nouvelle salle doit contenir la porte opposée
                if required_direction:
                    opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}[required_direction]
                    if opposite not in room.doors:
                        continue
                valid_rooms.append(room)
        
        # S’assurer qu’au moins une salle coûte 0 gemme
        zero_cost_rooms = [r for r in valid_rooms if r.gem_cost == 0]
        if len(zero_cost_rooms) == 0:
            # S’il n’y a aucune salle coûtant 0, en créer une
            if required_direction:
                opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}[required_direction]
                # Créer une salle avec la porte opposée + au moins une autre porte
                if opposite in ['UP', 'DOWN']:
                    doors = [opposite, 'LEFT', 'RIGHT']
                else:
                    doors = [opposite, 'UP', 'DOWN']
            else:
                doors = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            
            basic_room = Room(
                name="Salle Ordinaire",
                color="BLUE",
                rarity=0,
                gem_cost=0,
                doors=doors,
                image_path=None
            )
            # Vérifier si cette salle peut être placée
            can_place, _ = basic_room.can_place_at(row, col, mansion)
            if can_place:
                valid_rooms.append(basic_room)
                zero_cost_rooms.append(basic_room)
        
        if len(valid_rooms) == 0:
            return []
        
        # Calcul des poids (rarete + effets)
        weights = []
        green_prob_multiplier = 1.0 * self.green_prob_multiplier_global
        
        # Vérifier si la salle actuelle augmente la probabilité des salles vertes
        current_room = mansion.get_room(player.row, player.col)
        if current_room and current_room.effects.get("increase_green_probability"):
            green_prob_multiplier = 2.0
        
        for room in valid_rooms:
            base_weight = config.RARITY_WEIGHTS.get(room.rarity, 1.0)
            # Multiplicateurs globaux par couleur
            base_weight *= self.color_multipliers.get(room.color, 1.0)
            # Bonus pour les salles vertes
            if room.color == "GREEN" and green_prob_multiplier > 1.0:
                base_weight *= green_prob_multiplier
            weights.append(base_weight)
        
        # Sélection pondérée
        selected_rooms = []
        temp_valid = valid_rooms.copy()
        temp_weights = weights.copy()
        
        # Garantir au moins une salle à coût 0
        if zero_cost_rooms:
            zero_room = random.choice(zero_cost_rooms)
            selected_rooms.append(copy.deepcopy(zero_room))
            if zero_room in temp_valid:
                idx = temp_valid.index(zero_room)
                temp_valid.pop(idx)
                temp_weights.pop(idx)
        
        # Tirer les autres salles
        while len(selected_rooms) < count and len(temp_valid) > 0:
            if len(temp_weights) == 0:
                break
            
            total_weight = sum(temp_weights)
            if total_weight == 0:
                # Si tous les poids sont 0 → choix uniforme
                selected = random.choice(temp_valid)
            else:
                normalized_weights = [w / total_weight for w in temp_weights]
                selected = random.choices(temp_valid, weights=normalized_weights)[0]
            
            selected_rooms.append(copy.deepcopy(selected))
            
            idx = temp_valid.index(selected)
            temp_valid.pop(idx)
            temp_weights.pop(idx)
        
        # Retourner les salles choisies
        return selected_rooms
    
    def select_room(self, room, row, col, mansion, player):
        """
        Sélectionner une salle et la placer dans la grille
        
        Args:
            room: objet Room choisi
            row: ligne cible
            col: colonne cible
            mansion: objet Mansion
            player: objet Player
        
        Returns:
            tuple: (succès, message)
        """
        # Vérifier le coût en gemmes
        if room.gem_cost > 0:
            if not player.inventory.gems.has(room.gem_cost):
                return False, f"Gemmes insuffisantes, il faut {room.gem_cost} gemme(s)"
            player.inventory.remove_gems(room.gem_cost)
        
        # Vérifier la condition de placement
        can_place, reason = room.can_place_at(row, col, mansion)
        if not can_place:
            return False, reason
        
        # Placer la salle dans la grille
        mansion.set_room(row, col, room)
        
        # Récupérer l’objet réel en grille
        placed_room = mansion.get_room(row, col)
        if placed_room is None:
            return False, "Échec du placement de la salle"
        
        # Générer les objets de la salle
        if not placed_room.items:
            placed_room.generate_items(player.inventory)
        
        # Retirer la salle de la pioche (un seul exemplaire)
        for i, available_room in enumerate(self.available_rooms):
            if (available_room.name == room.name and 
                available_room.color == room.color and
                available_room.rarity == room.rarity):
                self.available_rooms.pop(i)
                break
        
        # Enregistrer les effets globaux
        self._note_placed_room_effects(placed_room)
        return True, f"Salle choisie : {placed_room.name}"
    
    def reroll(self, row, col, mansion, player, required_direction=None):
        """
        Utiliser un dé pour relancer un tirage de salles
        
        Args:
            row: ligne cible
            col: colonne cible
            mansion: objet Mansion
            player: objet Player
            required_direction: direction requise (pour la connectivité)
        
        Returns:
            tuple: (succès, nouvelle liste de salles)
        """
        if not player.inventory.dice.has(1):
            return False, "Aucun dé disponible"
        
        player.inventory.remove_dice(1)
        new_rooms = self.draw_rooms(row, col, mansion, player, required_direction=required_direction)
        return True, new_rooms
    
    def reset(self, room_templates):
        """Réinitialiser la pioche de salles disponibles"""
        self.room_templates = room_templates
        self.available_rooms = copy.deepcopy(room_templates)
        self.green_prob_multiplier_global = 1.0
        for k in self.color_multipliers:
            self.color_multipliers[k] = 1.0

    def _note_placed_room_effects(self, room):
        """Enregistrer les effets globaux après placement d’une salle"""
        if room and room.effects and room.effects.get("increase_green_probability"):
            # Chaque Véranda augmente encore ×1.5 la probabilité des salles vertes
            self.green_prob_multiplier_global *= 1.5
        if room and room.effects and room.effects.get("increase_color_weights"):
            mapping = room.effects.get("increase_color_weights") or {}
            for color, factor in mapping.items():
                if color in self.color_multipliers:
                    self.color_multipliers[color] *= float(factor)


