import pygame
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider

# place in game_window.py or gui/player_gui.py

import pygame

class PlayerGUI:
    def __init__(self, seat_index: int, state: dict, assets):
        self.assets = assets
        self.seat = seat_index
        self.state = state.copy()  # local copy
        self._layout_from_assets()
        self._load_profile_image()

    def _layout_from_assets(self):
        coords = self.assets.player_coords
        idx = self.seat % len(coords)
        cx, cy = coords[idx]
        self.center = (int(cx), int(cy))
        w, h = self.assets.sizes["profile"]
        self.profile_rect = pygame.Rect(self.center[0] - w//2, self.center[1] - h//2, w, h)

    def _load_profile_image(self):
        name = self.state.get("profile_picture") or self.state.get("name", "")
        img = self.assets.get_profile_image(name)
        if img is None:
            surf = pygame.Surface(self.profile_rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (180, 180, 180), surf.get_rect())
            img = surf
        self.profile_image = img

    def update_state(self, new_state: dict):
        # replace or merge depending on your preference
        self.state = new_state.copy()
        # reload profile image if name/profile changed
        if self.state.get("profile_picture") or self.state.get("name"):
            self._load_profile_image()

    def resize(self):
        self._layout_from_assets()
        self._load_profile_image()

    def draw(self, surface, card_zoom: float = 1.0, show_hole_for_others: bool = False):
        px, py = self.profile_rect.topleft
        surface.blit(self.profile_image, (px, py))

        name = str(self.state.get("name", ""))
        chips = self.state.get("chips", 0)
        folded = bool(self.state.get("folded", False))
        action = self.state.get("action")  # could be None or descriptive string
        hole = list(self.state.get("hole_cards", []))

        name_surf = self.assets.fonts["small"].render(name, True, self.assets.colors["white"])
        chips_surf = self.assets.fonts["small"].render(str(chips), True, (255, 215, 0))
        surface.blit(name_surf, (px, py + self.profile_rect.height + 2))
        surface.blit(chips_surf, (px, py + self.profile_rect.height + 4 + name_surf.get_height()))

        if action:
            act_surf = self.assets.fonts["small"].render(str(action), True, (255, 50, 50))
            surface.blit(act_surf, (px, py - act_surf.get_height() - 4))

        # dealer marker / turn highlight can be drawn by GameWindow (it has dealer_index)
        # draw hole cards if allowed: either local player or show_hole_for_others True
        local = bool(self.state.get("is_local", False))
        show_hole = local or show_hole_for_others
        if hole and show_hole and not folded:
            cw = int(self.assets.sizes["card_w"] * card_zoom)
            ch = int(self.assets.sizes["card_h"] * card_zoom)
            spacing = int(cw * 0.2)
            startx = px + self.profile_rect.width + 8
            y = py + self.profile_rect.height - ch
            for i, code in enumerate(hole[:2]):
                img = self.assets.get_card_image(code)
                img = pygame.transform.smoothscale(img, (cw, ch))
                surface.blit(img, (startx + i * (cw + spacing), y))

        # folded overlay
        if folded:
            overlay = self.assets.fonts["small"].render("FOLDED", True, (255, 0, 0))
            surface.blit(overlay, (px, py - overlay.get_height() - 4))
