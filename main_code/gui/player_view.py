import pygame
from gui.utility import get_chip_buff, get_chips
from copy import deepcopy


class PlayerView:
    def __init__(self, seat_index: int, state: dict, assets, window):
        self.assets = assets
        self.seat = seat_index
        self.state = deepcopy(state)
        self.window = window
        self.chip_names: list[str] = []

        # the possible bet of the user
        self.possible_bet: int = 0

        self.chip_buff = get_chip_buff()
        self._layout_from_assets()
        self._load_profile_image()

    def _layout_from_assets(self):
        """Sets layout using assets, depending on self.seat"""
        coords = self.assets.player_coords
        idx = self.seat % len(coords)

        cx, cy = coords[idx]
        self.centre = (int(cx), int(cy))

        w, h = self.assets.sizes["profile"]
        self.profile_rect = pygame.Rect(
            self.centre[0] - w // 2, self.centre[1] - h // 2, w, h
        )

        self.button_coords = self.assets.button_coords[idx]

    def _load_profile_image(self):
        """Loads the profile picture, cuts it to become circular and adds a border"""
        img = self.assets.get_profile_image(self.state["profile_picture"])
        size = self.profile_rect.size

        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(
            surf, (255, 255, 255), (0, 0, *size), border_radius=size[0] // 2
        )

        pygame.draw.rect(
            surf,
            self.assets.colours["black"],
            (0, 0, *size),
            border_radius=size[0] // 2,
            width=3 * self.assets.min_size_scale,
        )

        img.blit(surf, (0, 0), None, pygame.BLEND_RGBA_MIN)
        if img is None:
            surf = pygame.Surface(self.profile_rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (180, 180, 180), surf.get_rect())
            img = surf
        self.profile_image = img

    def update_state(self, new_state: dict, bb: int, new_round: bool = False):
        self.state = new_state.copy()
        self.set_chips_names(bb)
        if new_round:
            self.chip_buff = get_chip_buff()

    def resize(self):
        self._layout_from_assets()
        self._load_profile_image()

    def set_chips_names(self, bb):
        """Sets the chips names using round invested or the possible bet if this PlayerView is the user's"""
        self.chip_names = get_chips(
            bb, max(self.state["round_invested"], self.possible_bet)
        )

    def _draw_hole(self, hole_cards, surface, card_zoom):
        x = (
            self.centre[0]
            - len(hole_cards)
            * (
                +self.assets.sizes["card_w"] * card_zoom
                + self.assets.sizes["card_buffer"] // 2
            )
            // 2
        )
        y = self.profile_rect.bottomright[1] - self.assets.sizes["card_h"] * card_zoom
        for card in hole_cards:
            surface.blit(self.assets.get_card(card, card_zoom), (x, y))
            x += (
                self.assets.sizes["card_w"] * card_zoom
                + self.assets.sizes["card_buffer"]
            )

    def _draw_button(self, surface):
        btn = self.assets.images["dealer_button"]
        surface.blit(btn, self.button_coords)

    def _draw_centered(self, surface, text_surf, height):
        """Blits a surface to the screen at the given height and centered horizontally"""
        surface.blit(text_surf, self._centered_xcoords(text_surf.get_width(), height))

    def _centered_xcoords(self, surf_width: int, height: int):
        """Returns the coordinates to centre a surface to the screen at the given"""
        px, py = self.profile_rect.midtop
        return px - surf_width // 2, py + height

    def _draw_chips(self):
        self.window.draw_chips(self.chip_buff, self.chip_names, self.seat)

    def draw(self, surface, card_zoom=1.0):
        px, py = self.profile_rect.topleft
        surface.blit(self.profile_image, (px, py))

        chips = self.state["chips"]
        action = self.state["action"]
        hole = self.state["hole_cards"]
        chips_text_surf = self.assets.fonts["small"].render(
            str(chips), True, (255, 215, 0)
        )

        self._draw_centered(
            surface,
            chips_text_surf,
            self.profile_rect.height + 5 * self.assets.height_scale,
        )
        self._draw_hole(hole, surface, card_zoom)
        self._draw_chips()
        if self.state["position_name"] == "Button":
            self._draw_button(surface)

        if action:
            act_surf = self.assets.fonts["small"].render(
                str(action), True, (255, 50, 50)
            )

            self._draw_centered(
                surface,
                act_surf,
                min(
                    self.profile_rect.height - self.assets.sizes["card_h"] * card_zoom,
                    -5 * self.assets.height_scale,
                )
                - act_surf.get_height(),
            )
