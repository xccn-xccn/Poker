import pygame
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider
from gui.player_view import PlayerView

#TODO keep adding stuff
class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller):
        super().__init__(screen, assets)

        self.controller = controller

        self._sync_state()
        self.possible_bet = 0
        self.player_views = []

        self.widgets = {
            "Fold": Button("Fold", (100, 820), (150, 50), assets, on_click=lambda :self.controller.perform_action(0, 0)),
            "Check": Button("Check", (300, 820), (150, 50), assets, on_click=lambda :self.controller.perform_action(1, 0)),
            "Bet": Button("Bet", (700, 820), (150, 50), assets, on_click=self._toggle_raise_ui),
            "Deal": Button("Deal", (900, 120), (150, 50), assets, on_click=self._on_deal),
            "Back": ImageButton("back_button", (20, 20), (70, 70), assets, on_click=self._on_back),
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

        self.widgets = list(self.buttons.values())  # needed by window_base for event dispatch

        self.player_views = []
        self._build_player_views()

        # zoom for rendering cards
        self.card_zoom_level = 1.0

    def update(self):
        self.controller.update()
        self._sync_state()

    def _update_buttons(self):
        for btn_name, action in zip(("Check", "Bet"), self.user_state.actions):
            self.widgets[btn_name].set_text(action)

        self.bet_slider.set_max_value(self.user_state.chips)

    def draw(self):
        super().draw()
        self.screen.fill(self.assets.colours["background"])

    def _sync_state(self):
        """Refresh GUI objects with controller game state."""
        self.state = self.controller.get_state()

        self.user_state = self.state["players"][self.state["user_i"]]
        if self.state.new_player or len(self.player_views) != len(
            self.state["players"]
        ):
            self._build_player_views()
            return

        for player, p_data in zip(self.player_views, self.state["players"]):
            player.update_state(p_data)
