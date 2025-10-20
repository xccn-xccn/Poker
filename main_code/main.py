import sys
import pygame
from gui.assets import Assets
from gui.menu_window import MenuWindow
from gui.game_window import GameWindow
from controller import GameController, OnlineController

BASE_RESOLUTION = (1700, 900)
FPS = 60


class PokerApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Poker")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(BASE_RESOLUTION, pygame.RESIZABLE)
        self.assets = Assets(self.screen)
        self.controller = None
        self.set_menu_window()

    def set_menu_window(self):
        self.current_window = MenuWindow(
            screen=self.screen,
            assets=self.assets,
        )

    def start_game(self, online=False, host=False, host_ip=None):
        self.controller = OnlineController(is_host=host, host_ip=host_ip) if online else GameController()
        self.current_window = GameWindow(
            screen=self.screen,
            assets=self.assets,
            controller=self.controller,
        )

    def quit_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def resize(self, event):
        new_size = (event.w, event.h)
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.assets.rescale(new_size)
        self.current_window.resize(new_size)

    def check_window_change(self):
        new_window = self.current_window.new_window()

        if new_window:
            if new_window == "Offline Poker":
                self.start_game()
            elif new_window == "Menu":
                self.set_menu_window()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event)
                else:
                    self.current_window.handle_event(event)

            if self.controller:
                self.controller.update()

            self.current_window.draw()
            self.check_window_change()

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    PokerApp().run()
