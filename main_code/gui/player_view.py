import pygame


class PlayerView:
    def __init__(self, seat_index: int, state: dict, assets):
        self.assets = assets
        self.seat = seat_index
        self.state = state.copy()
        self._layout_from_assets()
        self._load_profile_image()

    def _layout_from_assets(self):
        coords = self.assets.player_coords
        idx = self.seat % len(coords)

        cx, cy = coords[idx]
        self.centre = (int(cx), int(cy))

        w, h = self.assets.sizes["profile"]
        self.profile_rect = pygame.Rect(
            self.centre[0] - w // 2, self.centre[1] - h // 2, w, h
        )

    def _load_profile_image(self):
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

    def update_state(self, new_state: dict):
        self.state = new_state.copy()

    def resize(self):
        self._layout_from_assets()
        self._load_profile_image()

    def _draw_hole(self, hole_cards, surface, card_zoom):
        x = (
            self.centre[0]
            - self.assets.sizes["card_w"] * card_zoom
            - self.assets.sizes["card_buffer"] // 2
        )
        y = self.profile_rect.bottomright[1] - self.assets.sizes["card_h"] * card_zoom
        for card in hole_cards:
            surface.blit(self.assets.get_card(card, card_zoom), (x, y))
            x += (
                self.assets.sizes["card_w"] * card_zoom
                + self.assets.sizes["card_buffer"]
            )

    def _draw_button(self, surface):  # TODO
        btn = self.assets.images["dealer_button"]
        surface.blit(btn, self._centered_xcoords(btn.get_height(), 50))

    def _draw_centered(self, surface, text_surf, height):
        surface.blit(text_surf, self._centered_xcoords(text_surf.get_width(), height))

    def _centered_xcoords(self, surf_width: int, height: int):
        px, py = self.profile_rect.midtop
        return px - surf_width // 2, py + height

    def draw(self, surface, card_zoom=1.0):
        px, py = self.profile_rect.topleft
        surface.blit(self.profile_image, (px, py))

        chips = self.state["chips"]
        action = self.state["action"]
        hole = self.state["hole_cards"]
        chips_surf = self.assets.fonts["small"].render(str(chips), True, (255, 215, 0))

        surface.blit(chips_surf, (px, py + self.profile_rect.height + 4))

        self._draw_hole(hole, surface, card_zoom)

        if self.state["position_name"] == "Button":
            self._draw_button(surface)

        if action:
            act_surf = self.assets.fonts["small"].render(
                str(action), True, (255, 50, 50)
            )
            self._draw_centered(
                surface, act_surf, -5 * self.assets.height_scale - act_surf.get_height()
            )
