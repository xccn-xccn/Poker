import pygame

class Button:
    def __init__(self, text, pos, size, assets, on_click=None):
        self.text = text
        self.assets = assets
        self.on_click = on_click

        self.original_pos = pos
        self.original_size = size

        self.rect = pygame.Rect(pos, size)

        self._update_size_position()

        self.base_color = assets.colors["button"]
        self.hover_color = assets.colors["button_hover"] if "button_hover" in assets.colors else (60, 160, 100)
        self.text_color = assets.colors["white"]

        self.hovered = False
        self.pressed = False
        self._update_rendered_text()

    def _update_size_position(self):
        self.pos = self.assets.rescale_single(*self.original_pos)
        self.size = self.assets.rescale_single(*self.original_size)
        self.rect.width, self.rect.height = self.size

        self.rect = pygame.Rect(*self.pos, *self.size)
        
    def _update_rendered_text(self):
        self.text_surface = self.assets.fonts["main"].render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.hovered and self.pressed and self.on_click:
                self.on_click()
            self.pressed = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8 * self.assets.min_size_scale)
        pygame.draw.rect(surface, self.assets.colors["outline"], self.rect, width=2, border_radius=8 * self.assets.min_size_scale)
        surface.blit(self.text_surface, self.text_rect)

    def resize(self):
        self._update_size_position()
        self._update_rendered_text()


class ImageButton(Button):
    def __init__(self, image_key, pos, size, assets, on_click=None):
        super().__init__("", pos, size, assets, on_click)
        self.image_key = image_key
        self.image = self.assets.images["buttons"][image_key]
        self._scale_image()

    def _scale_image(self):
        w = max(1, self.rect.width)
        h = max(1, self.rect.height)
        self.scaled_image = pygame.transform.smoothscale(self.image, (w, h))

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8 * self.assets.min_size_scale)
        surface.blit(self.scaled_image, self.rect.topleft)
        pygame.draw.rect(surface, self.assets.colors["outline"], self.rect, width=2, border_radius=8 * self.assets.min_size_scale)

    def resize(self):
        super().resize()
        self._scale_image()