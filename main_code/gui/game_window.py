import pygame
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider
from gui.player_view import PlayerView
from gui.utility import centre_position

ROUND_END_EVENT = pygame.USEREVENT + 1


class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller):
        super().__init__(screen, assets)

        self.controller = controller

        self.player_views = []
        self._sync_state()
        self.possible_bet = 0
        self.player_views = []
        self.action_freeze = False

        self.widgets = {
            "Fold": Button(
                "Fold",
                (100, 820),
                (150, 50),
                assets,
                on_click=lambda: self._perform_action(1, 0),
            ),
            "Check": Button(
                "Check",
                (300, 820),
                (150, 50),
                assets,
                on_click=lambda: self._perform_action(2, 0),
            ),
            "Bet": Button(
                "Bet",
                *centre_position(1575, 820, 150, 50),
                assets,
                on_click=lambda: self._perform_action(3, self.possible_bet)
            ),
            "Deal": Button(
                "Deal",
                *centre_position(self.assets.base_resolution[0] // 2, 145, 150, 50),
                assets,
                on_click=self._on_deal
            ),
            "Back": ImageButton(
                "back_button",
                (20, 20),
                (70, 70),
                assets,
                on_click=lambda: self._set_window("Menu"),
            ),
            "Zoom": ImageButton(
                "zoom_in", (1600, 20), (70, 70), assets, on_click=self._on_zoom
            ),
            "Bet_slider": BetSlider(
                pos=(400, 760),
                size=(700, 40),
                assets=assets,
                min_value=0,
                max_value=1000,
                step=10,
                on_change=self._on_slider_change,
            ),
        }

        self.card_zoom = 1.0

    def _perform_action(self, action, amount=0):
        if self.action_freeze:
            return
        end_valid = self.controller.perform_action(action, amount)

        # TODO deal with invalid moves if end_valid = None
        if end_valid:
            self._pre_end_round()

        if end_valid != None:
            self._after_action()

    def _after_action(self):
        self.possible_bet = 0
        self.widgets["Bet_slider"].set_value(0)

    def _pre_end_round(self):
        pygame.time.set_timer(ROUND_END_EVENT, 500, loops=1)
        self.action_freeze = True

    def _on_deal(self):
        if self.state["running"]:
            return

        self.controller.start_hand()

    def _on_zoom(self):
        self.card_zoom = {1.0: 1.5, 1.5: 2.5, 2.5: 1.0}[self.card_zoom]

    def _on_slider_change(self, value):
        self.possible_bet = value

    def update(self):
        if self.action_freeze:
            # shouldn't need to call self._sync_state but check
            return

        end_round = self.controller.update()

        if end_round:
            self._pre_end_round()

        self._sync_state()
        self._update_buttons()

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == ROUND_END_EVENT:
            self._end_round()

    def _end_round(self):
        self.controller.end_round()
        self._sync_state()
        self.action_freeze = False

    def _update_buttons(self):
        for btn_name, action in zip(("Check", "Bet"), self.user_state["poss_actions"]):
            self.widgets[btn_name].set_text(action)

        self.widgets["Bet_slider"].set_max_value(self.user_state["chips"])

    def _draw_table(self):
        table_img = self.assets.get_table_image()
        pos = self.assets.sizes["table_pos"]
        self.screen.blit(table_img, pos)

    def _draw_community(self):
        x = self.screen.get_width() / 2 - (5 / 2 * self.assets.sizes["card_w"] + 2 * self.assets.sizes["card_buffer"]) * self.card_zoom
        y = self.screen.get_height() / 2 - 1 / 2 * self.assets.sizes["card_h"] * self.card_zoom

        for card in self.state["community"]:
            self.screen.blit(self.assets.get_card(card, self.card_zoom), (x, y))
            x += (
                self.assets.sizes["card_w"] * self.card_zoom
                + self.assets.sizes["card_buffer"]
            )


    def _draw_pot(self):
        pot_surf = self.assets.fonts["small"].render(
            str(self.state["pot"]), True, self.assets.colours["black"]
        )
        self.screen.blit(
            pot_surf,
            centre_position(
                self.assets.width // 2, 320, pot_surf.get_width(), pot_surf.get_height()
            )[0],
        )

    def draw(self):
        self.screen.fill(self.assets.colours["background"])

        self._draw_table()
        self._draw_community()
        self._draw_pot()

        for p in self.player_views:
            p.draw(self.screen, self.card_zoom)

        super().draw()

    def resize(self, new_size):
        super().resize(new_size)
        for p in self.player_views:
            p.resize()

    def _build_player_views(self):
        """Creates PlayerView objects for each seat."""
        self.state = self.controller.get_state()
        self.player_views = [
            PlayerView(p["seat"], p, self.assets) for p in self.state["players"]
        ]

    def _sync_state(self):
        """Refresh GUI objects with controller game state."""
        self.state = self.controller.get_state()

        self.user_state = self.state["players"][self.state["user_i"]]
        if self.state["new_player"] or len(self.player_views) != len(
            self.state["players"]
        ):
            self._build_player_views()
            return

        for player, p_data in zip(self.player_views, self.state["players"]):
            player.update_state(p_data)
