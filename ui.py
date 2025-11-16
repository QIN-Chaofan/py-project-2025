"""
Interface graphique pygame
"""
import pygame
import config
import os


# Définition des couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
HIGHLIGHT = (255, 255, 0)

# Mappage des couleurs des salles
ROOM_COLOR_MAP = {
    "YELLOW": YELLOW,
    "GREEN": GREEN,
    "PURPLE": PURPLE,
    "ORANGE": ORANGE,
    "RED": RED,
    "BLUE": BLUE,
}


class UI:
    """Classe de l'interface graphique"""

    def __init__(self, width=1200, height=800):
        """
        Initialisation de l'UI

        Args:
            width: largeur de la fenêtre
            height: hauteur de la fenêtre
        """
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Prince Bleu - Blue Prince")

        # Position du bouton de réinitialisation (initialisée à None, définie au rendu)
        self.reset_button_rect = None

        # Cache d'images
        self.room_images = {}          # Cache des images de salles
        self.background_image = None   # Image d'arrière-plan

        # Chargement de l'image d'arrière-plan
        try:
            bg_path = "images/Interface_du_jeu.png"
            if os.path.exists(bg_path):
                self.background_image = pygame.image.load(bg_path)
                # Redimensionner l'image pour s'adapter à la fenêtre
                self.background_image = pygame.transform.scale(self.background_image, (width, height))
        except Exception as e:
            print(f"Impossible de charger l'image d'arrière-plan : {e}")
            self.background_image = None

        # S'assurer que la fenêtre reçoit bien les entrées clavier (compatibilité Windows)
        try:
            import platform

            if platform.system() == "Windows":
                # Sous Windows, s'assurer que la fenêtre peut recevoir les événements clavier
                pygame.event.set_allowed([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT])
        except Exception:
            pass

        # Polices
        pygame.font.init()
        self.font_small = self._get_cjk_font(20)
        self.font_medium = self._get_cjk_font(24)
        self.font_large = self._get_cjk_font(32)
        self.font_title = self._get_cjk_font(48)

        # Paramètres de mise en page
        self.grid_x = 50
        self.grid_y = 50
        self.cell_size = 60
        self.panel_x = 700
        self.panel_y = 50
        self.panel_width = 450

    def _get_cjk_font(self, size):
        """
        Obtenir une police supportant au mieux l'affichage CJK
        """
        import os
        import platform

        system = platform.system()
        file_candidates = []

        if system == "Windows":
            # Chemins fréquents de polices chinoises sous Windows
            windir = os.environ.get("WINDIR", "C:\\Windows")
            file_candidates = [
                os.path.join(windir, "Fonts", "msyh.ttc"),      # Microsoft YaHei
                os.path.join(windir, "Fonts", "msyhbd.ttc"),    # Microsoft YaHei Bold
                os.path.join(windir, "Fonts", "simhei.ttf"),    # SimHei
                os.path.join(windir, "Fonts", "simsun.ttc"),    # SimSun
                os.path.join(windir, "Fonts", "simkai.ttf"),    # KaiTi
                os.path.join(windir, "Fonts", "STSONG.TTF"),    # STSong
                os.path.join(windir, "Fonts", "STHEITI.TTF"),   # STHeiti
            ]
        elif system == "Darwin":  # macOS
            file_candidates = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/Supplemental/Songti SC.ttc",
                "/System/Library/Fonts/Supplemental/STSong.ttf",
                "/System/Library/Fonts/Supplemental/Hiragino Sans GB W3.ttc",
                "/System/Library/Fonts/Supplemental/Hiragino Sans GB W6.ttc",
                "/System/Library/Fonts/Supplemental/Heiti TC.ttc",
                "/System/Library/Fonts/Supplemental/Heiti SC.ttc",
            ]
        elif system == "Linux":
            # Chemins fréquents de polices chinoises sous Linux
            file_candidates = [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf",
            ]

        # Essayer de charger directement via le chemin
        for path in file_candidates:
            try:
                if os.path.exists(path):
                    f = pygame.font.Font(path, size)
                    if f is not None:
                        return f
            except Exception:
                continue

        # Essayer via le nom de fonte système
        if system == "Windows":
            font_candidates = [
                "Microsoft YaHei",
                "SimHei",
                "SimSun",
                "KaiTi",
                "FangSong",
                "STSong",
                "STHeiti",
                "Noto Sans CJK SC",
                "Source Han Sans SC",
            ]
        elif system == "Darwin":  # macOS
            font_candidates = [
                "PingFang SC",
                "Hiragino Sans GB",
                "Heiti SC",
                "STHeiti",
                "Songti SC",
                "STSong",
                "Microsoft YaHei",
                "SimHei",
                "Noto Sans CJK SC",
                "Source Han Sans SC",
            ]
        else:  # Linux
            font_candidates = [
                "Noto Sans CJK SC",
                "WenQuanYi Micro Hei",
                "WenQuanYi Zen Hei",
                "Source Han Sans SC",
                "Microsoft YaHei",
                "SimHei",
            ]

        for name in font_candidates:
            try:
                f = pygame.font.SysFont(name, size)
                if f is not None:
                    return f
            except Exception:
                continue

        # Repli sur la police par défaut
        return pygame.font.SysFont(None, size)

    def render(self, game):
        """
        Rendu de l'écran de jeu

        Args:
            game: objet Game
        """
        # Effacer l'écran
        self.screen.fill(BLACK)

        # Dessiner l'image d'arrière-plan (si disponible)
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))

        from game import GameState

        if game.state == GameState.GAME_OVER:
            self._render_game_over(game)
        elif game.state == GameState.SELECTING_ROOM:
            self._render_room_selection(game)
        elif game.state == GameState.PICKING_ITEMS:
            self._render_item_picking(game)
        elif game.state == GameState.SHOP:
            self._render_shop(game)
        else:
            self._render_main(game)

        pygame.display.flip()

    def _render_main(self, game):
        """Rendu de l'interface principale du jeu"""
        # Dessiner la grille
        self._render_grid(game)

        # Dessiner le panneau d'inventaire
        self._render_inventory_panel(game)

        # Dessiner le bouton de réinitialisation
        self._render_reset_button(game)

        # Dessiner le message
        self._render_message(game.message)

        # Dessiner les aides de contrôle
        self._render_controls()

    def _render_grid(self, game):
        """Dessiner la grille de jeu"""
        for row in range(config.GRID_ROWS):
            for col in range(config.GRID_COLS):
                x = self.grid_x + col * self.cell_size
                y = self.grid_y + row * self.cell_size

                room = game.mansion.get_room(row, col)
                is_current = (row == game.player.row and col == game.player.col)
                is_selected_direction = False

                # Vérifier si c'est la case correspondant à la direction sélectionnée
                from game import GameState

                if game.selected_direction and game.state == GameState.SELECTING_DIRECTION:
                    dr, dc = config.DIRECTIONS[game.selected_direction]
                    if row == game.player.row + dr and col == game.player.col + dc:
                        is_selected_direction = True

                # Dessiner la salle
                if room:
                    if room.explored:
                        # Salle déjà explorée
                        # Bordure de surbrillance
                        if is_current:
                            # Salle actuelle en surbrillance
                            pygame.draw.rect(
                                self.screen,
                                HIGHLIGHT,
                                (x - 2, y - 2, self.cell_size + 4, self.cell_size + 4),
                                3,
                            )
                        elif is_selected_direction:
                            # Salle dans la direction sélectionnée en surbrillance
                            pygame.draw.rect(
                                self.screen,
                                CYAN,
                                (x - 2, y - 2, self.cell_size + 4, self.cell_size + 4),
                                2,
                            )

                        # Essayer de charger et dessiner l'image de la salle
                        room_image = self._get_room_image(room)
                        if room_image:
                            self.screen.blit(room_image, (x, y))
                        else:
                            # Pas d'image : remplir par une couleur
                            color = ROOM_COLOR_MAP.get(room.color, BLUE)
                            pygame.draw.rect(
                                self.screen, color, (x, y, self.cell_size, self.cell_size)
                            )

                        # Bordure de la salle
                        pygame.draw.rect(
                            self.screen,
                            WHITE,
                            (x, y, self.cell_size, self.cell_size),
                            1,
                        )

                        # Nom de la salle (abrégé, au-dessus de l'image)
                        name_text = self.font_small.render(room.name[:4], True, WHITE)
                        # Fond pour rendre le texte lisible sur l'image
                        text_bg = pygame.Surface(
                            (name_text.get_width() + 4, name_text.get_height() + 2)
                        )
                        text_bg.set_alpha(180)
                        text_bg.fill(BLACK)
                        self.screen.blit(text_bg, (x + 1, y + 1))
                        self.screen.blit(name_text, (x + 3, y + 2))

                        # Dessiner les portes
                        self._render_doors(x, y, room)
                    else:
                        # Salle non explorée (gris foncé)
                        pygame.draw.rect(
                            self.screen,
                            DARK_GRAY,
                            (x, y, self.cell_size, self.cell_size),
                        )
                        pygame.draw.rect(
                            self.screen,
                            GRAY,
                            (x, y, self.cell_size, self.cell_size),
                            1,
                        )
                else:
                    # Case vide (noire)
                    pygame.draw.rect(
                        self.screen, BLACK, (x, y, self.cell_size, self.cell_size)
                    )
                    pygame.draw.rect(
                        self.screen,
                        DARK_GRAY,
                        (x, y, self.cell_size, self.cell_size),
                        1,
                    )

        # Marquer la position du joueur
        player_x = (
            self.grid_x + game.player.col * self.cell_size + self.cell_size // 2
        )
        player_y = (
            self.grid_y + game.player.row * self.cell_size + self.cell_size // 2
        )
        pygame.draw.circle(self.screen, WHITE, (player_x, player_y), 8)
        pygame.draw.circle(self.screen, RED, (player_x, player_y), 6)

    def _render_doors(self, x, y, room):
        """Dessiner les portes de la salle"""
        door_size = 8
        for direction in room.door_objects:
            door = room.door_objects[direction]
            if direction == "UP":
                door_x = x + self.cell_size // 2
                door_y = y
                color = GREEN if door.opened else RED
                pygame.draw.rect(
                    self.screen,
                    color,
                    (door_x - door_size // 2, door_y, door_size, 4),
                )
            elif direction == "DOWN":
                door_x = x + self.cell_size // 2
                door_y = y + self.cell_size - 4
                color = GREEN if door.opened else RED
                pygame.draw.rect(
                    self.screen,
                    color,
                    (door_x - door_size // 2, door_y, door_size, 4),
                )
            elif direction == "LEFT":
                door_x = x
                door_y = y + self.cell_size // 2
                color = GREEN if door.opened else RED
                pygame.draw.rect(
                    self.screen,
                    color,
                    (door_x, door_y - door_size // 2, 4, door_size),
                )
            elif direction == "RIGHT":
                door_x = x + self.cell_size - 4
                door_y = y + self.cell_size // 2
                color = GREEN if door.opened else RED
                pygame.draw.rect(
                    self.screen,
                    color,
                    (door_x, door_y - door_size // 2, 4, door_size),
                )

    def _render_inventory_panel(self, game):
        """Dessiner le panneau d'inventaire"""
        y = self.panel_y
        x = self.panel_x

        # Titre
        title = self.font_large.render("Inventaire", True, WHITE)
        self.screen.blit(title, (x, y))
        y += 40

        # Consommables
        subtitle = self.font_medium.render("Consommables :", True, CYAN)
        self.screen.blit(subtitle, (x, y))
        y += 30

        inventory = game.player.inventory
        consumables = [
            ("Pas", inventory.steps.amount),
            ("pièces", inventory.coins.amount),
            ("gemmes", inventory.gems.amount),
            ("clés", inventory.keys.amount),
            ("dés", inventory.dice.amount),
        ]

        for name, amount in consumables:
            text = self.font_small.render(f"{name} : {amount}", True, WHITE)
            self.screen.blit(text, (x + 20, y))
            y += 25

        y += 20

        # Articles permanents
        subtitle = self.font_medium.render("Articles permanents :", True, CYAN)
        self.screen.blit(subtitle, (x, y))
        y += 30

        permanent_items = [
            ("Pelle", inventory.shovel.get_count()),
            ("Marteau", inventory.hammer.get_count()),
            ("Kit de crochetage", inventory.lockpick.get_count()),
            ("Détecteur de métaux", inventory.metal_detector.get_count()),
            ("Patte de lapin", inventory.lucky_rabbit_foot.get_count()),
        ]

        for name, count in permanent_items:
            if count > 0:
                text = self.font_small.render(f"{name} : {count}", True, GREEN)
            else:
                text = self.font_small.render(f"{name} : {count}", True, GRAY)
            self.screen.blit(text, (x + 20, y))
            y += 25

        # Position actuelle
        y += 30
        pos_text = self.font_medium.render(
            f"Position : ({game.player.row}, {game.player.col})", True, WHITE
        )
        self.screen.blit(pos_text, (x, y))

        # Debug : position de rendu (pour vérifier les coordonnées)
        y += 20
        player_x = (
            self.grid_x + game.player.col * self.cell_size + self.cell_size // 2
        )
        player_y = (
            self.grid_y + game.player.row * self.cell_size + self.cell_size // 2
        )
        render_pos_text = self.font_small.render(
            f"Position de rendu : ({player_x}, {player_y})", True, GRAY
        )
        self.screen.blit(render_pos_text, (x, y))

        # Informations sur la salle actuelle
        current_room = game.get_current_room()
        if current_room:
            y += 30
            room_text = self.font_medium.render(
                f"Salle : {current_room.name}", True, WHITE
            )
            self.screen.blit(room_text, (x, y))

            # Debug : position réelle de la salle
            if hasattr(current_room, "row") and hasattr(current_room, "col"):
                y += 20
                room_pos_text = self.font_small.render(
                    f"Position de la salle : ({current_room.row}, {current_room.col})",
                    True,
                    GRAY,
                )
                self.screen.blit(room_pos_text, (x, y))

                # Vérifier une éventuelle incohérence de position
                if (
                    current_room.row != game.player.row
                    or current_room.col != game.player.col
                ):
                    y += 20
                    mismatch_text = self.font_small.render(
                        "⚠ Position incohérente !", True, RED
                    )
                    self.screen.blit(mismatch_text, (x, y))

    def _render_reset_button(self, game):
        """Dessiner le bouton de réinitialisation"""
        # Position du bouton : en bas du panneau d'inventaire
        button_x = self.panel_x
        button_y = self.height - 150
        button_width = 150
        button_height = 40

        # Position de la souris (pour effet de survol)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = (
            button_x <= mouse_pos[0] <= button_x + button_width
            and button_y <= mouse_pos[1] <= button_y + button_height
        )

        # Couleurs selon l'état de survol
        if is_hovered:
            button_color = GRAY
            border_color = YELLOW
            text_color = YELLOW
        else:
            button_color = DARK_GRAY
            border_color = WHITE
            text_color = WHITE

        # Dessiner le fond du bouton
        pygame.draw.rect(
            self.screen, button_color, (button_x, button_y, button_width, button_height)
        )
        pygame.draw.rect(
            self.screen,
            border_color,
            (button_x, button_y, button_width, button_height),
            2,
        )

        # Texte du bouton
        button_text = self.font_medium.render("Réinitialiser la partie", True, text_color)
        text_rect = button_text.get_rect(
            center=(button_x + button_width // 2, button_y + button_height // 2)
        )
        self.screen.blit(button_text, text_rect)

        # Mémoriser la position du bouton pour la détection de clic
        self.reset_button_rect = pygame.Rect(
            button_x, button_y, button_width, button_height
        )

    def _render_room_selection(self, game):
        """Rendu de l'écran de sélection de salle"""
        # Fond assombri
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Titre
        title = self.font_title.render("Choisir une salle", True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)

        # Liste des salles disponibles (peut être < 3)
        room_width = 300
        room_height = 400
        room_count = len(game.available_rooms)
        if room_count == 0:
            # Aucune salle disponible
            error_text = self.font_large.render("Aucune salle disponible", True, RED)
            error_rect = error_text.get_rect(
                center=(self.width // 2, self.height // 2)
            )
            self.screen.blit(error_text, error_rect)
            return

        # Mise en page selon le nombre de salles
        spacing = 20
        total_width = room_width * room_count + spacing * (room_count - 1)
        start_x = (self.width - total_width) // 2
        y = 150

        for i, room in enumerate(game.available_rooms):
            x = start_x + i * (room_width + spacing)

            # Surbrillance de la salle sélectionnée
            if i == game.selected_room_index:
                pygame.draw.rect(
                    self.screen,
                    HIGHLIGHT,
                    (x - 5, y - 5, room_width + 10, room_height + 10),
                    3,
                )

            # Cadre de la salle
            color = ROOM_COLOR_MAP.get(room.color, BLUE)
            pygame.draw.rect(self.screen, color, (x, y, room_width, room_height))
            pygame.draw.rect(
                self.screen, WHITE, (x, y, room_width, room_height), 2
            )

            # Informations de la salle
            info_y = y + 20
            name_text = self.font_large.render(room.name, True, WHITE)
            self.screen.blit(name_text, (x + 10, info_y))
            info_y += 40

            # Couleur (note : room.color est un code interne, ex. 'YELLOW')
            color_text = self.font_medium.render(
                f"Couleur : {room.color}", True, WHITE
            )
            self.screen.blit(color_text, (x + 10, info_y))
            info_y += 30

            # Rareté
            rarity_text = self.font_medium.render(
                f"Rareté : {room.rarity}", True, WHITE
            )
            self.screen.blit(rarity_text, (x + 10, info_y))
            info_y += 30

            # Coût en gemmes
            cost_text = self.font_medium.render(
                f"Coût en gemmes : {room.gem_cost}", True, YELLOW
            )
            self.screen.blit(cost_text, (x + 10, info_y))
            info_y += 30

            # Directions des portes (UP/DOWN/LEFT/RIGHT)
            doors_text = self.font_small.render(
                "Portes : " + ", ".join(room.doors), True, WHITE
            )
            self.screen.blit(doors_text, (x + 10, info_y))
            info_y += 30

            # Effets spéciaux
            if room.effects:
                effects_text = self.font_small.render(
                    "Effet spécial présent", True, GREEN
                )
                self.screen.blit(effects_text, (x + 10, info_y))

        # Aides de contrôle
        hint_y = y + room_height + 30
        hints = [
            "← → : choisir une salle",
            "Entrée/Espace : valider le choix",
            "R : relancer les salles (utilise un dé)",
            "Échap : annuler (retour au jeu)",
        ]
        for hint in hints:
            hint_text = self.font_medium.render(hint, True, WHITE)
            hint_rect = hint_text.get_rect(center=(self.width // 2, hint_y))
            self.screen.blit(hint_text, hint_rect)
            hint_y += 30

        # Afficher un message d'erreur/le message du jeu (si existant)
        if game.message:
            # On pourrait adapter la couleur selon certains mots-clés français si besoin
            error_text = self.font_medium.render(game.message, True, YELLOW)
            error_rect = error_text.get_rect(center=(self.width // 2, hint_y + 20))
            self.screen.blit(error_text, error_rect)

    def _render_game_over(self, game):
        """Rendu de l'écran de fin de partie"""
        # Fond assombri
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Déterminer victoire ou défaite
        is_victory = (
            "Félicitations" in game.game_over_message
            or "Victoire" in game.game_over_message
            or "🎉" in game.game_over_message
        )

        # Message de fin de partie
        message_color = GREEN if is_victory else RED
        message_text = self.font_title.render(
            game.game_over_message, True, message_color
        )
        message_rect = message_text.get_rect(
            center=(self.width // 2, self.height // 2)
        )
        self.screen.blit(message_text, message_rect)

        # Indication
        hint_text = self.font_medium.render(
            "Appuyez sur une touche pour recommencer", True, GRAY
        )
        hint_rect = hint_text.get_rect(
            center=(self.width // 2, self.height // 2 + 60)
        )
        self.screen.blit(hint_text, hint_rect)

    def _render_message(self, message):
        """Rendu du message temporaire"""
        if message:
            msg_text = self.font_medium.render(message, True, YELLOW)
            self.screen.blit(msg_text, (50, self.height - 100))

    def _render_controls(self):
        """Rendu des aides de contrôle"""
        import config

        if config.STRICT_MODE:
            move_hint = (
                "WASD/ZQSD/flèches directionnelles : choisir une direction  "
                "Espace : valider le déplacement"
            )
        else:
            move_hint = "WASD/ZQSD/flèches directionnelles : se déplacer"

        controls = [
            move_hint,
            "E : interagir avec les objets de la salle  B : boutique (salle jaune)",
            "R : relancer les salles (nécessite un dé)",
            "Échap : annuler/retour",
        ]
        y = self.height - 60
        for control in controls:
            control_text = self.font_small.render(control, True, GRAY)
            self.screen.blit(control_text, (50, y))
            y += 20

    def _render_item_picking(self, game):
        """Rendu de l'écran d'interaction avec les objets de la salle"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Objets de la salle", True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)

        room = game.get_current_room()
        items = room.items if room else []
        start_y = 150
        for i, it in enumerate(items):
            prefix = "▶ " if i == game.item_selection_index else "   "
            name = it if isinstance(it, str) else getattr(it, "name", None)
            if not name and isinstance(it, tuple):
                name = f"{it[0]} x{it[1]}"
            elif not name:
                name = str(it)
            text = self.font_large.render(
                prefix + name,
                True,
                WHITE if i == game.item_selection_index else GRAY,
            )
            self.screen.blit(text, (200, start_y + i * 40))

        hint = self.font_medium.render(
            "↑↓ : choisir  Entrée/Espace : interagir  Échap : retour", True, GRAY
        )
        hint_rect = hint.get_rect(center=(self.width // 2, self.height - 80))
        self.screen.blit(hint, hint_rect)

    def _render_shop(self, game):
        """Rendu de l'écran de boutique"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Boutique", True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)

        room = game.get_current_room()
        items = room.effects.get("items", []) if room and room.effects else []
        start_y = 150
        for i, spec in enumerate(items):
            name = spec.get("name", "Objet")
            price = spec.get("price", 0)
            prefix = "▶ " if i == game.shop_selection_index else "   "
            text = self.font_large.render(
                f"{prefix}{name} - {price} pièces",
                True,
                WHITE if i == game.shop_selection_index else GRAY,
            )
            self.screen.blit(text, (160, start_y + i * 40))

        hint = self.font_medium.render(
            "↑↓ : choisir  Entrée/Espace : acheter  Échap : retour", True, GRAY
        )
        hint_rect = hint.get_rect(center=(self.width // 2, self.height - 80))
        self.screen.blit(hint, hint_rect)

    def _get_room_image(self, room):
        """
        Obtenir l'image de la salle (avec mise en cache)

        Args:
            room: objet Room

        Returns:
            pygame.Surface ou None
        """
        # Si la salle n'a pas de chemin d'image, retourner None
        if not room.image_path:
            return None

        # Vérifier le cache
        if room.image_path in self.room_images:
            return self.room_images[room.image_path]

        # Essayer de charger l'image
        try:
            if os.path.exists(room.image_path):
                image = pygame.image.load(room.image_path)
                # Redimensionner l'image à la taille de la cellule
                image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
                # Mettre en cache
                self.room_images[room.image_path] = image
                return image
            else:
                print(f"Fichier d'image inexistant : {room.image_path}")
                return None
        except Exception as e:
            print(f"Impossible de charger l'image de salle {room.image_path} : {e}")
            return None
