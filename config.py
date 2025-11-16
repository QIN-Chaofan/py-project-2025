"""
Constantes de configuration du jeu
"""
# Dimensions de la grille
GRID_ROWS = 5
GRID_COLS = 9

# Inventaire initial du joueur
INITIAL_STEPS = 70
INITIAL_COINS = 0
INITIAL_GEMS = 2
INITIAL_KEYS = 0
INITIAL_DICE = 0

# Mode d'interaction : Le mode strict nécessite "Sélection par touches directionnelles + Espace pour confirmer" ; le mode pratique permet de se déplacer en appuyant sur la touche directionnelle.
STRICT_MODE = False

# Position de l'entrée (milieu de la dernière ligne)
ENTRANCE_ROW = GRID_ROWS - 1
ENTRANCE_COL = GRID_COLS // 2

# Position du Hall d'entrée (milieu de la première ligne)
FRONT_HALL_ROW = 0
FRONT_HALL_COL = GRID_COLS // 2

# Directions
DIRECTIONS = {
    'UP': (-1, 0),
    'DOWN': (1, 0),
    'LEFT': (0, -1),
    'RIGHT': (0, 1)
}

# Mappage des noms de direction
DIRECTION_NAMES = {
    'UP': 'Haut',
    'DOWN': 'Bas',
    'LEFT': 'Gauche',
    'RIGHT': 'Droite'
}

# Couleurs des pièces
ROOM_COLORS = {
    'YELLOW': 'Jaune',
    'GREEN': 'Vert',
    'PURPLE': 'Violet',
    'ORANGE': 'Orange',
    'RED': 'Rouge',
    'BLUE': 'Bleu'
}

# Poids de probabilité de rareté (la probabilité est divisée par 3 pour chaque augmentation de niveau de rareté)
RARITY_WEIGHTS = {
    0: 1.0,
    1: 1.0 / 3,
    2: 1.0 / 9,
    3: 1.0 / 27
}

#Probabilité du niveau de serrure de la porte (basée sur la position de la ligne)
# Ligne 1 (index 0) : Ne génère que le niveau 0
# Dernière ligne (index GRID_ROWS-1) : Ne génère que le niveau 2
# Lignes intermédiaires : Distribution mixte

