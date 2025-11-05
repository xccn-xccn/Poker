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
        img = self.assets.get_profile_image(self.state['profile_picture'])
        # img = None
        size = self.profile_rect.size
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(
            surf, (255, 255, 255), (0, 0, *size), border_radius=size[0] // 2
        )

        pygame.draw.rect(
            surf,
            self.assets.colours['black'],
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
        # reload profile image if name/profile changed
        if self.state.get("profile_picture") or self.state.get("name"):
            self._load_profile_image()

    def resize(self):
        self._layout_from_assets()
        self._load_profile_image()

    def _draw_hole(self, hole_cards, surface):
        x = self.centre[0] - self.assets.sizes["card_w"] - self.assets.sizes["card_buffer"] // 2
        y = self.profile_rect.bottomright[1] - self.assets.sizes["card_h"]
        for card in hole_cards:
            surface.blit(self.assets.images["cards"][card], (x, y))
            x += self.assets.sizes["card_w"] + self.assets.sizes["card_buffer"]

    def draw(self, surface, card_zoom: float = 1.0, show_hole_for_others: bool = False):
        px, py = self.profile_rect.topleft
        surface.blit(self.profile_image, (px, py))

        # name = str(self.state.get("name", ""))
        chips = self.state["chips"]
        action = self.state.get("action")  # could be None or descriptive string
        hole = self.state["hole_cards"]
        chips_surf = self.assets.fonts["small"].render(str(chips), True, (255, 215, 0))
        # surface.blit(name_surf, (px, py + self.profile_rect.height + 2))
        surface.blit(
            chips_surf, (px, py + self.profile_rect.height + 4)
        )

        if action:
            act_surf = self.assets.fonts["small"].render(
                str(action), True, (255, 50, 50)
            )
            surface.blit(act_surf, (px, py - act_surf.get_height() - 4))

        self._draw_hole(hole, surface)
