import pygame

from gui.window_base import WindowBase
from main_code.gui.buttons import Button

class MenuWindow(WindowBase):
    def __init__(self, screen, assets):
        super().__init__(screen, assets)
        self.widgets = [
            Button("Play Offline", (800, 400), assets, on_click=lambda: self._set_window("Offline Poker")),
            Button("Quit", (800, 500), assets, on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))),
        ]

    def _set_window(self, name):
        self.new_window = name

    def draw(self):
        self.screen.blit(self.assets.images["black_background1"], (0, 0))
        super().draw()
