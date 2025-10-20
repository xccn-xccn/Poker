import pygame

class WindowBase:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.new_window = None
        self.widgets = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.new_window = "Menu"
        for w in self.widgets:
            w.handle_event(event)

    def update(self, dt):
        pass

    def draw(self):
        for w in self.widgets:
            w.draw(self.screen)

    def resize(self, new_size):
        self.assets.rescale(new_size)
        for w in self.widgets:
            w.resize()

    def get_new_window(self):
        return self.new_window

    def clear_new_window(self):
        self.new_window = None
