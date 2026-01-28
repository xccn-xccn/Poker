import sys
import pygame
from gui.assets import Assets
from gui.menu_window import MenuWindow
from gui.game_window import GameWindow
from core.controller import OfflineController, OnlineController

# BASE_RESOLUTION = (1700, 900)
BASE_RESOLUTION = (1600, 900)
FPS = 60


class PokerApp:
    def __init__(self, testing=False):
        pygame.init()
        pygame.display.set_caption("Poker")
        self.__clock = pygame.time.Clock()
        self.set_initial_size()
        self.assets = Assets(self.screen, BASE_RESOLUTION)
        self.__controller = None
        self.testing = testing
        self.set_menu_window()

    def set_initial_size(self):
        scale = (
            min(
                pygame.display.Info().current_w / BASE_RESOLUTION[0],
                pygame.display.Info().current_h / BASE_RESOLUTION[1],
            )
            * 0.9
        )

        width = scale * BASE_RESOLUTION[0]
        height = scale * BASE_RESOLUTION[1]

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.screen = pygame.display.set_mode(BASE_RESOLUTION, pygame.RESIZABLE)

    def set_menu_window(self):
        self.current_window = MenuWindow(
            screen=self.screen,
            assets=self.assets,
        )

    def start_game(self, online=False, host=False, host_ip=None):
        self.__controller = (
            OnlineController(is_host=host, host_ip=host_ip)
            if online
            else OfflineController(testing=self.testing)
        )
        self.current_window = GameWindow(
            screen=self.screen,
            assets=self.assets,
            controller=self.__controller,
            testing=self.testing,
        )

    def quit_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def resize(self, event):
        new_size = (event.w, event.h)
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.assets.rescale(new_size)
        self.current_window.resize(new_size)

    def check_window_change(self):
        new_window = self.current_window.new_window

        if new_window:
            if new_window == "Offline Poker":
                self.start_game()
            elif new_window == "Online Poker":
                self.start_game(online=True, host=None)  # Add host here
            elif new_window == "Menu":
                self.set_menu_window()

    def run(self):
        running = True
        while running:
            dt = self.__clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event)
                else:
                    self.current_window.handle_event(event)

            self.check_window_change()
            self.current_window.update()
            self.current_window.draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    arg = sys.argv
    app = PokerApp(testing=arg[1] if len(arg) > 1 and arg[1][0] == "t" else False)
    app.run()