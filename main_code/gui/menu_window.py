import pygame

from gui.window_base import WindowBase
from gui.buttons import Button

class MenuWindow(WindowBase):
    def __init__(self, screen, assets):
        super().__init__(screen, assets)
        self.widgets = {
            "0": Button("Play Offline", (800, 400), (200, 150), assets, on_click=lambda: self._set_window("Offline Poker")),
            "1": Button("Quit", (800, 600), (200, 150), assets, on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))),
        }

    def draw(self):
        self.screen.blit(self.assets.images["black_background1"], (0, 0))
        super().draw()
