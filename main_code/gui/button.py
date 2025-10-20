import pygame

class Button:
    def __init__(self, text, pos, assets, size=None, on_click=None):
        self.text = text
        self.assets = assets
        self.font = assets.fonts["main"]
        self.on_click = on_click

        w = size[0] if size else assets.sizes["button_w"]
        h = size[1] if size else assets.sizes["button_h"]
        x, y = pos
        self.rect = pygame.Rect(x, y, w, h)

        self.base_color = assets.colors["button"]
        self.hover_color = assets.colors["button_hover"] if "button_hover" in assets.colors else (60, 160, 100)
        self.text_color = assets.colors["white"]

        self.hovered = False
        self.pressed = False
        self._update_rendered_text()

    def _update_rendered_text(self):
        self.text_surface = self.font.render(self.text, True, self.text_color)
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
        pygame.draw.rect(surface, color, self.rect, border_radius=int(8 * self.assets.MSCALE))
        pygame.draw.rect(surface, self.assets.colors["outline"], self.rect, width=2, border_radius=int(8 * self.assets.MSCALE))
        surface.blit(self.text_surface, self.text_rect)

    def resize(self):
        w = self.assets.sizes["button_w"]
        h = self.assets.sizes["button_h"]
        self.rect.width = w
        self.rect.height = h
        self._update_rendered_text()
