import pygame
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider
from gui.player_gui import PlayerGUI

class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller):
        super().__init__(screen, assets)

        self.controller = controller

        self.state = controller.get_state()


    def update(self):
        self.controller.update()

    def draw(self):
        super().draw()
        self.screen.fill(self.assets.colours["background"])



