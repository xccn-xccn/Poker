import pygame
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider
from gui.player_view import PlayerView

#TODO Decide how card zoom will work 
class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller):
        super().__init__(screen, assets)

        self.controller = controller

        self.player_views = []
        self._sync_state()
        self.possible_bet = 0
        self.player_views = []

        self.widgets = {
            "Fold": Button("Fold", (100, 820), (150, 50), assets, on_click=lambda :self.controller.perform_action(0, 0)),
            "Check": Button("Check", (300, 820), (150, 50), assets, on_click=lambda :self.controller.perform_action(1, 0)),
            "Bet": Button("Bet", (700, 820), (150, 50), assets, on_click=self._on_bet),
            "Deal": Button("Deal", (900, 120), (150, 50), assets, on_click=self._on_deal),
            "Back": ImageButton("back_button", (20, 20), (70, 70), assets, on_click=lambda: self._set_window("Menu")),
            "Zoom": ImageButton("zoom_in", (1600, 20), (70, 70), assets, on_click=self._on_zoom),
        }

        # betting slider (hidden until user clicks "Raise")
        self.bet_slider_visible = False
        self.bet_slider = BetSlider(
            pos=(400, 760),
            size=(700, 40),
            assets=assets,
            min_value=0,
            max_value=1000,
            step=10,
            on_change=self._on_slider_change
        )


        # zoom for rendering cards
        self.card_zoom = 1.0

    def _on_bet(self):
        self.controller.perform_action(3, self.possible_bet)

    def _on_deal(self):
        #TODO ensure table is running find where this should be checked
        self.controller.start_hand()

    def _on_zoom(self):
        self.card_zoom = {1.0: 1.5, 1.5: 2.5, 2.5: 1.0}[self.card_zoom]  

    def _on_slider_change(self, value):
        # self.possible_bet_value = value   # <— store temp UI state here
        #TODO
        pass
            
    def update(self):
        self.controller.update()
        self._sync_state()

    def _update_buttons(self):
        for btn_name, action in zip(("Check", "Bet"), self.user_state["poss_actions"]):
            self.widgets[btn_name].set_text(action)

        self.bet_slider.set_max_value(self.user_state.chips)

    def draw(self):
        self.screen.fill(self.assets.colours["background"])
        for p in self.player_views:
            p.draw(self.screen, self.card_zoom)
        super().draw()

    def _build_player_views(self):
        """Creates PlayerView objects for each seat."""
        self.state = self.controller.get_state()
        self.player_views = [
            PlayerView(p["seat"], p, self.assets)
            for p in self.state["players"]
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
