import pygame
from abc import ABC


class WindowBase(ABC):
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.new_window = None
        self.widgets = {}

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.new_window = "Menu"
        for w in self.widgets.values():
            w.handle_event(event)

    def _set_window(self, name):
        self.new_window = name

    def update(self):
        pass

    def draw(self):
        for w in self.widgets.values():
            w.draw(self.screen)

    def resize(self, new_size):
        self.assets.rescale(new_size)
        for w in self.widgets.values():
            w.resize()

    def get_new_window(self):
        return self.new_window

    def clear_new_window(self):
        self.new_window = None
