import pygame

from gui.window_base import WindowBase
from gui.buttons import Button
from gui.utility import centre

class MenuWindow(WindowBase):
    def __init__(self, screen, assets):
        super().__init__(screen, assets)
        self.widgets = {
            "0": Button("Play Offline", *centre(self.assets.centrex, 250, 200, 150),  assets, on_click=lambda: self._set_window("Offline Poker")),
            "1": Button("Play Online", *centre(self.assets.centrex, 450, 200, 150), assets, on_click=lambda: self._set_window("Online Poker")),
            "2": Button("Quit", *centre(self.assets.centrex, 650, 200, 150), assets, on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))),
        }

    def draw(self):
        self.screen.blit(self.assets.images["black_background1"], (0, 0))
        super().draw()
