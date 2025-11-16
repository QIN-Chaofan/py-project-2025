"""
Définition de la classe Door
"""
import random
import config


class Door:
    """Classe Door, gère l'état de verrouillage des portes"""
    
    def __init__(self, direction, lock_level=None, row=None):
        """
        Initialisation d'une porte
        
        Args:
            direction: Direction de la porte ('UP', 'DOWN', 'LEFT', 'RIGHT')
            lock_level: Niveau de verrouillage (0=non verrouillée, 1=verrouillée, 2=doublement verrouillée),
                        si None alors généré aléatoirement selon la ligne
            row: Ligne de la salle, utilisée pour calculer le niveau de verrouillage
        """
        self.direction = direction
        self.opened = False
        
        if lock_level is not None:
            self.lock_level = lock_level
        else:
            self.lock_level = self._calculate_lock_level(row)
    
    def _calculate_lock_level(self, row):
        """
        Calculer le niveau de verrouillage en fonction de la ligne
        
        Args:
            row: Ligne de la salle (0-4)
        
        Returns:
            int: Niveau de verrouillage (0, 1 ou 2)
        """
        if row is None:
            return 0

        # Ligne de l’entrée : uniquement niveau 0
        if row == config.ENTRANCE_ROW:
            return 0

        # Ligne du hall avant : uniquement niveau 2
        if row == config.FRONT_HALL_ROW:
            return 2

        # Lignes intermédiaires : calcul du niveau selon le “progrès” de l’entrée vers le hall avant
        # progress: 0 = proche de l’entrée ; 1 = proche du hall avant
        total_span = max(1, config.ENTRANCE_ROW - config.FRONT_HALL_ROW)
        progress = (config.ENTRANCE_ROW - row) / total_span
        
        rand = random.random()
        if progress < 0.3:
            # Premiers 30% : surtout niveau 0, quelques niveau 1
            if rand < 0.8:
                return 0
            else:
                return 1
        elif progress < 0.7:
            # Milieu 40% : mélange de niveaux 0 et 1, quelques niveau 2
            if rand < 0.5:
                return 0
            elif rand < 0.9:
                return 1
            else:
                return 2
        else:
            # Derniers 30% : principalement niveaux 1 et 2
            if rand < 0.3:
                return 0
            elif rand < 0.7:
                return 1
            else:
                return 2
    
    def can_open(self, player):
        """
        Vérifie si le joueur peut ouvrir la porte
        
        Args:
            player: Objet Player
        
        Returns:
            tuple: (peut ouvrir ou non, message d'explication)
        """
        if self.opened:
            return True, "La porte est déjà ouverte"
        
        if self.lock_level == 0:
            return True, "La porte n’est pas verrouillée"
        
        if self.lock_level == 1:
            # Niveau 1 : peut être ouverte avec un kit de crochetage ou une clé
            if player.inventory.lockpick.has():
                return True, "Utilisation d’un kit de crochetage"
            elif player.inventory.keys.has(1):
                return True, "Nécessite 1 clé"
            else:
                return False, "Une clé ou un kit de crochetage est nécessaire"
        
        if self.lock_level == 2:
            # Niveau 2 : nécessite obligatoirement une clé
            if player.inventory.keys.has(1):
                return True, "Nécessite 1 clé"
            else:
                return False, "1 clé est requise (double verrouillage)"
        
        return False, "Erreur inconnue"
    
    def open(self, player):
        """
        Ouvrir la porte
        
        Args:
            player: Objet Player
        
        Returns:
            tuple: (succès ou non, message)
        """
        can_open, message = self.can_open(player)
        
        if not can_open:
            return False, message
        
        if self.opened:
            return True, "La porte est déjà ouverte"
        
        # Consommation de ressources
        if self.lock_level == 1:
            if not player.inventory.lockpick.has():
                # Utiliser une clé
                player.inventory.keys.remove(1)
        elif self.lock_level == 2:
            # Doit utiliser une clé
            player.inventory.keys.remove(1)
        
        self.opened = True
        return True, f"Porte ouverte avec succès ({message})"
    
    def __str__(self):
        status = "ouverte" if self.opened else f"niveau de verrouillage {self.lock_level}"
        return f"Porte({self.direction}, {status})"



