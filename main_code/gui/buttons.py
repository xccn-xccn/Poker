import pygame


class Button:
    def __init__(
        self,
        text,
        pos,
        size,
        assets,
        on_click=None,
        base_colour=None,
        hover_colour=None,
        text_colour=None,
        border_width=2,
    ):
        self.text = text
        self.assets = assets
        self.on_click = on_click
        self.border_width = border_width

        self.original_pos = pos
        self.original_size = size

        self.rect = pygame.Rect(pos, size)

        self._update_size_position()

        self.base_colour = base_colour if base_colour else assets.colours["button"]
        self.hover_colour = (
            hover_colour if hover_colour else assets.colours["button_hover"]
        )
        self.text_colour = text_colour if text_colour else assets.colours["white"]

        self.hovered = False
        self.pressed = False
        self._update_rendered_text()

    def _update_size_position(self):
        self.pos = self.assets.rescale_single(*self.original_pos)
        self.size = self.assets.rescale_single(*self.original_size)
        self.rect.width, self.rect.height = self.size

        self.rect = pygame.Rect(*self.pos, *self.size)

    def set_text(self, text):
        self.text = text
        self._update_rendered_text()

    def _update_rendered_text(self):
        self.text_surface = self.assets.fonts["main"].render(
            self.text, True, self.text_colour
        )
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
        colour = self.hover_colour if self.hovered else self.base_colour
        pygame.draw.rect(
            surface, colour, self.rect, border_radius=8 * self.assets.min_size_scale
        )
        pygame.draw.rect(
            surface,
            self.assets.colours["outline"],
            self.rect,
            width=self.border_width * self.assets.min_size_scale,
            border_radius=8 * self.assets.min_size_scale,
        )
        surface.blit(self.text_surface, self.text_rect)

    def resize(self):
        self._update_size_position()
        self._update_rendered_text()


class BetSlider(Button):
    def __init__(
        self,
        pos,
        size,
        assets,
        min_value,
        max_value,
        step,
        start_value=None,
        on_change=None,
    ):
        super().__init__("", pos, size, assets, on_click=None)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.value = start_value if start_value is not None else min_value
        self.on_change = on_change
        self.dragging = False
        self._update_handle_rect()

    def set_max_value(self, max_value):
        self.max_value = max_value
        self._update_handle_rect()
        # TODO hmm

    def _update_handle_rect(self):
        h = self.rect.height
        handle_x = self._value_to_x()
        self.handle_rect = pygame.Rect(handle_x - h // 2, self.rect.top, h, h)

    def _value_to_x(self):
        if self.max_value == self.min_value:
            return self.rect.left
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(self.rect.left + ratio * self.rect.width)

    def _x_to_value(self, x):
        ratio = (x - self.rect.left) / max(1, self.rect.width)
        raw = self.min_value + ratio * (self.max_value - self.min_value)
        stepped = int(round(raw / self.step) * self.step)
        return max(self.min_value, min(self.max_value, stepped))

    def set_range(self, min_value, max_value, step=None):
        self.min_value = min_value
        self.max_value = max_value
        if step:
            self.step = step
        self.value = max(min_value, min(self.value, max_value))
        self._update_handle_rect()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(
                event.pos
            ):
                self.dragging = True
                self.value = self._x_to_value(event.pos[0])
                self._update_handle_rect()
                if self.on_change:
                    self.on_change(self.value)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._x_to_value(event.pos[0])
            self._update_handle_rect()
            if self.on_change:
                self.on_change(self.value)

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.assets.colours["outline"],
            self.rect,
            border_radius=int(6 * self.assets.min_size_scale),
        )
        inner = self.rect.inflate(-4, -8)
        pygame.draw.rect(
            surface,
            (50, 50, 50),
            inner,
            border_radius=int(6 * self.assets.min_size_scale),
        )

        fill_ratio = (self.value - self.min_value) / max(
            1, (self.max_value - self.min_value)
        )
        fill_w = int(inner.width * fill_ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(inner.left, inner.top, fill_w, inner.height)
            pygame.draw.rect(
                surface,
                self.assets.colours["button"],
                fill_rect,
                border_radius=int(6 * self.assets.min_size_scale),
            )

        pygame.draw.ellipse(surface, (220, 220, 220), self.handle_rect)

        txt = self.assets.fonts["small"].render(
            str(self.value), True, self.assets.colours["white"]
        )
        surface.blit(
            txt, (self.rect.right + 8, self.rect.centery - txt.get_height() // 2)
        )

    def resize(self):
        super().resize()
        self._update_handle_rect()


class ImageButton(Button):
    def __init__(self, image_key, pos, size, assets, on_click=None, border_width=0):
        super().__init__("", pos, size, assets, on_click, border_width=border_width)
        self.image_key = image_key
        self.image = self.assets.images["buttons"][image_key]
        self._scale_image()

    def _scale_image(self):
        self.scaled_image = pygame.transform.smoothscale(
            self.image, (max(1, self.rect.width), max(1, self.rect.height))
        )

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.scaled_image, self.rect.topleft)

    def resize(self):
        super().resize()
        self._scale_image()
