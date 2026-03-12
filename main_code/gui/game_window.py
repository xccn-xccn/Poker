import pygame
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider, VerticalSlider
from gui.player_view import PlayerView
from gui.utility import centre, get_chips, get_chip_buff
from math import floor


class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller, testing):
        super().__init__(screen, assets)

        self.testing = testing
        self.player_views = []
        self.possible_bet = 0
        self.action_freeze = False

        set_bet_width = 70
        set_bet_buffer = 10
        self.widgets = {
            "Fold": Button(
                "Fold",
                *centre(1250, 750, 150, 50),
                assets,
                on_click=lambda: self._perform_action(1, 0),
                base_colour=self.assets.colours["red"],
                hover_colour=self.assets.colours["red2"],
            ),
            "Check": Button(
                "Check",
                *centre(1250, 820, 150, 50),
                assets,
                on_click=lambda: self._perform_action(2, 0),
                base_colour=self.assets.colours["grey"],
                hover_colour=self.assets.colours["grey2"],
            ),
            "Bet": Button(
                "Bet",
                *centre(1485, 820, 150, 50),
                assets,
                on_click=lambda: self._perform_action(3, self.possible_bet),
            ),
            "Deal": Button(
                "Deal",
                *centre(self.assets.base_resolution[0] // 2, 145, 150, 50),
                assets,
                on_click=self._on_deal,
            ),
            "Back": ImageButton(
                "back_button",
                (20, 20),
                (70, 70),
                assets,
                on_click=lambda: self.set_window("Menu"),
            ),
            "Zoom": ImageButton(
                "zoom_in", (20, 90 + 20), (70, 70), assets, on_click=self._on_zoom
            ),
            "Set_Bet1": Button(
                "x0.5",
                *centre(1400, 760, set_bet_width, 50),
                assets,
                on_click=lambda: self._set_bet(0),
            ),
            "Set_Bet2": Button(
                "x1",
                *centre(1400 + set_bet_width + set_bet_buffer, 760, set_bet_width, 50),
                assets,
                on_click=lambda: self._set_bet(1),
            ),
            "Set_Bet3": Button(
                "ALL",
                *centre(
                    1400 + (set_bet_width + set_bet_buffer) * 2, 760, set_bet_width, 50
                ),
                assets,
                on_click=lambda: self._set_bet(2),
            ),
            "Bet_slider": VerticalSlider(
                (self.assets.base_resolution[0] - 160, 20),
                (140, 675),
                assets,
                0,
                max_value=1000,
                step=10,
                on_change=self._on_slider_change,
            ),
        }

        self.controller = controller
        self.state_update = False
        self.controller.set_state_callback(self.update_state)
        self.chip_buff = get_chip_buff()
        self.chips = []
        self.card_zoom = 1.0

    def _set_bet(self, button_index):

        max_bet = self.user_state["chips"] + self.user_state["round_invested"]
        p_bet = 0
        if self.state["round"] == 0:
            bb = self.state["bb"]
            p_bet = [bb * 3, bb * 6, bb * 12][button_index]
        else:
            pot = self.state["pot"]
            p_bet = [pot * 0.5, pot * 1, max_bet][button_index]

        self.possible_bet = floor(min(max_bet, p_bet))
        self._after_pbet_change()

    def _after_pbet_change(self):
        self.user_view.possible_bet = self.possible_bet
        self.user_view.set_chips_names(self.state["bb"])
        self._update_slider()

    def _perform_action(self, action, amount=0):
        self.controller.perform_action(action, amount)
        self._after_action()

    def _after_action(self):
        self.possible_bet = 0
        self._after_pbet_change()

    def _update_slider(self):
        self.widgets["Bet_slider"].set_value(self.possible_bet)

    def _on_deal(self):
        if self.state["running"]:
            return

        self.controller.start_hand()

    def _on_zoom(self):

        self.card_zoom = {1.0: 1.5, 1.5: 1.9, 1.9: 1.0}[self.card_zoom]
        # self.controller.table.add_new_player(10000)

    def _on_slider_change(self, value):
        self.possible_bet = value
        self._after_pbet_change()

    def update(self):
        """Updates that are needed for frame"""
        if self.state_update:
            self._apply_state()
            self.state_update = False

        if (
            self.testing
            and self.state["running"] == False
            and len(self.testing) >= 2
            and self.testing[1] in "0248"
        ):
            self.controller.start_hand()

    def handle_event(self, event):
        super().handle_event(event)

    def _draw_table(self):
        table_img = self.assets.get_table_image()
        pos = self.assets.sizes["table_pos"]
        self.screen.blit(table_img, pos)

    def _draw_community(self):
        """Draws community cards depending on self.card_zoom"""

        x = (
            self.screen.get_width() / 2
            - (
                5 / 2 * self.assets.sizes["card_w"]
                + 2 * self.assets.sizes["card_buffer"]
            )
            * self.card_zoom
        )
        y = (
            self.screen.get_height() / 2
            - 1 / 2 * self.assets.sizes["card_h"] * self.card_zoom
        )

        for card in self.state["community"]:
            self.screen.blit(self.assets.get_card(card, self.card_zoom), (x, y))
            x += (
                self.assets.sizes["card_w"] * self.card_zoom
                + self.assets.sizes["card_buffer"]
            )

    def _draw_pot(self):
        # Because self.card_zoom cannot be taken into account in assets.py
        # Any offset to do with card_zoom must be calculated here

        pot_surf = self.assets.fonts["small"].render(
            str(self.state["pot"]), True, self.assets.colours["black"]
        )
        self.screen.blit(
            pot_surf,
            centre(
                self.assets.width // 2,
                self.assets.height // 2
                - (
                    self.assets.sizes["card_w"] * self.card_zoom
                    + 8 * self.assets.height_scale
                ),
                pot_surf.get_width(),
                pot_surf.get_height(),
            )[0],
        )

        self.draw_chips(
            self.chip_buff,
            self.chips,
            offset=(0, -self.assets.sizes["card_w"] * self.card_zoom),
        )

    def draw_chips(
        self,
        chip_buffer: list[int],
        chips: list,
        seat_i: int = -1,
        offset: tuple[int, int] = (0, 0),
    ):
        """Draws the chips for a player depending on seat_i 
        or the pot if no seat_i provided"""


        chips_coords = (
            self.assets.dealer_chips_coords
            if seat_i == -1
            else self.assets.chips_coords[seat_i]
        )

        p = 0
        if len(chips) > 10:
            p = -1

        for i, chip in enumerate(chips[:30]):
            if i % 10 == 0:
                p += 1

            cx, cy = chips_coords[p]
            cx += chip_buffer[i] + offset[0]
            cy += offset[1] - (0.35 * self.assets.sizes["chip_h"]) * (i % 10)
            c_image = self.assets.images["chips"][chip]
            self.screen.blit(c_image, (cx, cy))

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
            PlayerView(p["seat"], p, self.assets, self) for p in self.state["players"]
        ]
        self.user_view = self.player_views[self.state["user_i"]]

    def _update_buttons(self):
        for btn_name, action in zip(("Check", "Bet"), self.user_state["poss_actions"]):
            self.widgets[btn_name].set_text(action)

        bb = self.state["bb"]
        for btn_name, action in zip(
            ("Set_Bet1", "Set_Bet2", "Set_Bet3"),
            [(str(bb * 3), "x0.5"), (str(bb * 6), "x1"), (str(bb * 12), "ALL")],
        ):
            self.widgets[btn_name].set_text(action[int(self.state["round"] != 0)])

        self.widgets["Bet_slider"].set_max_value(
            self.user_state["chips"] + self.user_state["round_invested"]
        )

    def update_state(self, state):
        """Stores the new game state
            Does not update UI"""
        self.state_update = True
        self.state = state
        # no changes made straight away for thread safety

    def _apply_state(self):
        """Updates GUI with game state."""

        self.user_state = self.state["players"][self.state["user_i"]]
        self._update_buttons()

        if self.state["running"] == False:
            self.chip_buff = get_chip_buff()

        if self.state["new_round"]:
            self.chips = get_chips(self.state["bb"], self.state["pot"])

        if self.state["new_player"] or len(self.player_views) != len(
            self.state["players"]
        ):
            self._build_player_views()
            return

        for player, p_data in zip(self.player_views, self.state["players"]):
            player.update_state(
                p_data, self.state["bb"], new_round=self.state["new_round"]
            )
