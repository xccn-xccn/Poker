import pygame

from gui.window_base import WindowBase
from gui.buttons import Button
from gui.utility import centre

class MenuWindow(WindowBase):
    def __init__(self, screen, assets):
        super().__init__(screen, assets)
        self.widgets = {
            "0": Button("Play Offline", *centre(self.assets.base_centrex, 150, 250, 150),  assets, on_click=lambda: self.set_window("Offline Poker")),
            "1": Button("Play Online", *centre(self.assets.base_centrex, 350, 250, 150), assets, on_click=lambda: self.set_window("Online Poker")),
            "2": Button("Play Kuhn", *centre(self.assets.base_centrex, 550, 250, 150), assets, on_click=lambda: self.set_window("Kuhn Poker")),
            "3": Button("Quit", *centre(self.assets.base_centrex, 750, 250, 150), assets, on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))),
        }

    def draw(self):
        self.screen.blit(self.assets.images["black_background1"], (0, 0))
        super().draw()
