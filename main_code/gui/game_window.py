import pygame
import math
from gui.window_base import WindowBase
from gui.buttons import Button, ImageButton, BetSlider

CARD_ZOOM_STEPS = (1.5, 1.0, 0.66)

class PlayerArea:
    def __init__(self, idx, player_obj, table, assets):
        self.idx = idx
        self.player = player_obj
        self.table = table
        self.assets = assets
        self.update_layout()
        self._make_profile_image()

    def update_layout(self):
        coords = self.assets.player_coords
        idx = self.idx % len(coords)
        x, y = coords[idx]
        self.cx = int(x)
        self.cy = int(y)
        pw, ph = self.assets.sizes["profile"]
        self.profile_rect = pygame.Rect(self.cx - pw // 2, self.cy - ph // 2, pw, ph)

    def _make_profile_image(self):
        name = getattr(self.player, "position_name", "") or getattr(self.player, "name", "")
        # img = self.assets.get_profile_image(name)
        img = None
        if img:
            self.profile_image = img
        else:
            surf = pygame.Surface(self.profile_rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (200, 200, 200), surf.get_rect())
            self.profile_image = surf

    def update(self):
        pass

    def draw(self, surface, card_zoom=1.0, show_hole=False):
        px, py = self.profile_rect.topleft
        surface.blit(self.profile_image, (px, py))
        # name + chips
        name = getattr(self.player, "position_name", "") or getattr(self.player, "name", "")
        chips = getattr(self.player, "chips", 0)
        name_surf = self.assets.fonts["small"].render(str(name), True, self.assets.colors["white"])
        chips_surf = self.assets.fonts["small"].render(str(chips), True, (255, 215, 0))
        surface.blit(name_surf, (px, py + self.profile_rect.height + 2))
        surface.blit(chips_surf, (px, py + self.profile_rect.height + 2 + name_surf.get_height()))
        # action indicator
        action = getattr(self.player, "action", None)
        if action:
            if action == 1:
                t = "Fold"
            elif action == 2:
                t = "Call"
            else:
                t = "Bet"
            a_surf = self.assets.fonts["small"].render(t, True, (255, 0, 0))
            surface.blit(a_surf, (px, py - a_surf.get_height() - 4))
        # hole cards if allowed
        hole = getattr(self.player, "hole_cards", []) or []
        draw_cards = hole and (getattr(self.player, "is_local_player", False) or show_hole)
        if draw_cards:
            cw = int(self.assets.sizes["card_w"] * card_zoom)
            ch = int(self.assets.sizes["card_h"] * card_zoom)
            spacing = int(cw * 0.2)
            startx = px + self.profile_rect.width + 8
            y = py + self.profile_rect.height - ch
            for i, code in enumerate(hole[:2]):
                card_img = self.assets.get_card_image(code)
                card_img = pygame.transform.smoothscale(card_img, (cw, ch))
                surface.blit(card_img, (startx + i * (cw + spacing), y))


class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller):
        super().__init__(screen, assets)
        self.controller = controller
        btn_w, btn_h = 150, 50
        # bottom y is provided as base-res coords (1700x900 base)
        bottom_y = 820
        # Buttons (positions are base resolution coords)
        self.fold_btn = Button("Fold", (100, bottom_y), (btn_w, btn_h), assets, on_click=lambda: self._player_action("fold", 0))
        self.check_btn = Button("Check", (300, bottom_y), (btn_w, btn_h), assets, on_click=lambda: self._player_action("call", 0))
        self.call_btn = Button("Call", (500, bottom_y), (btn_w, btn_h), assets, on_click=lambda: self._player_action("call", 0))
        self.raise_btn = Button("Raise", (700, bottom_y), (btn_w, btn_h), assets, on_click=self._open_raise_slider)
        self.deal_btn = Button("Deal", (900, 120), (btn_w, btn_h), assets, on_click=self._on_deal)
        self.back_btn = ImageButton("back_button", (20, 20), (70, 70), assets, on_click=self._on_back)
        self.zoom_btn = ImageButton("zoom_in", (1600, 20), (70, 70), assets, on_click=self._on_zoom)
        self.widgets = [self.fold_btn, self.check_btn, self.call_btn, self.raise_btn, self.deal_btn, self.back_btn, self.zoom_btn]
        # slider for bets (hidden by default)
        self.bet_slider = BetSlider(assets, (400, 760), (700, 40), min_value=0, max_value=1000, step=10)
        self.show_slider = False
        # state mirrors (kept for drawing)
        self.community = []
        self.pot = 0
        self.player_areas = []
        self.card_zoom_index = 1
        self.card_zoom = CARD_ZOOM_STEPS[self.card_zoom_index]
        # build players from controller.table
        self._rebuild_players()
        # some UI state
        self.last_action_text = ""
        self.dealer_index = getattr(self.controller.table, "dealer_index", 0) if getattr(self.controller, "table", None) else 0

    def _rebuild_players(self):
        table = self.controller.table
        self.player_areas = []
        for i, p in enumerate(table.players):
            pa = PlayerArea(i, p, table, self.assets)
            self.player_areas.append(pa)

    def _on_back(self):
        self.new_window = "Menu"

    def _on_deal(self):
        self.controller.start_hand()
        self._rebuild_players()
        self._sync_from_controller()

    def _open_raise_slider(self):
        # set slider range according to player's chips and table limits
        table = self.controller.table
        human = table.human_player
        min_bet = getattr(table, "last_bet", 0) or (table.blinds[-1] if getattr(table, "blinds", None) else 1)
        max_bet = human.chips
        step = max(1, min(10, max_bet // 100))
        self.bet_slider.set_range(min_bet, max_bet, step)
        self.bet_slider.value = min_bet
        self.show_slider = True

    def _on_zoom(self):
        self.card_zoom_index = (self.card_zoom_index + 1) % len(CARD_ZOOM_STEPS)
        self.card_zoom = CARD_ZOOM_STEPS[self.card_zoom_index]
        # swap zoom icon logically
        key = "zoom_out" if self.card_zoom_index == 2 else "zoom_in"
        self.zoom_btn.image = self.assets.images["buttons"][key]
        self.zoom_btn._scale_image()

    def _player_action(self, action, amount=0):
        action_map = {"check": "call"}
        action = action_map.get(action, action)
        # controller performs validation/logic; it should not crash for invalid moves
        self.controller.perform_action(action, amount)
        self._sync_from_controller()

    def _sync_from_controller(self):
        state = self.controller.get_state()
        self.community = state.get("community", [])
        self.pot = state.get("pot", 0)
        # update player areas from table
        table = self.controller.table
        if len(self.player_areas) != len(table.players):
            self._rebuild_players()
        for i, pa in enumerate(self.player_areas):
            pa.player = table.players[i]
            pa._make_profile_image()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.VIDEORESIZE:
            # ensure all widgets recalc size+position and player areas update
            for w in self.widgets:
                w.resize()
            self.bet_slider.resize()
            for pa in self.player_areas:
                pa.update_layout()
                pa._make_profile_image()
            return

        if self.show_slider:
            self.bet_slider.handle_event(event)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # commit slider on mouse up if it was active
                if not self.bet_slider.dragging:
                    # if handle clicked and released outside, ignore
                    pass

        # Buttons are processed by WindowBase via widgets; but we reroute additional clicks:
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # if slider visible and click on confirm area (right of slider), place bet
            mx, my = event.pos
            if self.show_slider:
                # define confirm rect to the right of slider
                sx, sy = self.bet_slider.rect.topleft
                sw, sh = self.bet_slider.rect.size
                confirm_rect = pygame.Rect(sx + sw + 12, sy, 80, sh)
                if confirm_rect.collidepoint((mx, my)):
                    val = self.bet_slider.value
                    self.controller.perform_action("raise", val)
                    self.show_slider = False
                    self._sync_from_controller()

    def update(self, dt=None):
        self.controller.update()
        self._sync_from_controller()
        for pa in self.player_areas:
            pa.update()

    def resize(self, new_size):
        self.assets.rescale(new_size)
        for w in self.widgets:
            w.resize()
        self.bet_slider.resize()
        for pa in self.player_areas:
            pa.update_layout()
            pa._make_profile_image()

    def _draw_dealer_button(self, surface):
        table_pos = self.assets.sizes["table_pos"]
        tw, th = self.assets.sizes["table_size"]
        # place dealer indicator near the appropriate player
        d_idx = getattr(self.controller.table, "dealer_index", 0)
        coords = self.assets.player_coords
        if not coords:
            return
        cx, cy = coords[d_idx % len(coords)]
        r = int(18 * self.assets.min_size_scale)
        pygame.draw.circle(surface, (255, 215, 0), (int(cx + r), int(cy - r)), r)

    def _draw_pot(self):
        txt = self.assets.fonts["large"].render(f"POT: {self.pot}", True, self.assets.colors["white"])
        x = (self.screen.get_width() - txt.get_width()) // 2
        y = int(self.assets.sizes["table_pos"][1] + 12)
        self.screen.blit(txt, (x, y))

    def _draw_community(self):
        if not self.community:
            return
        cw_base = int(self.assets.sizes["card_w"])
        ch_base = int(self.assets.sizes["card_h"])
        cw = int(cw_base * self.card_zoom)
        ch = int(ch_base * self.card_zoom)
        spacing = int(cw * 0.15)
        total_w = len(self.community) * (cw + spacing) - spacing
        start_x = (self.screen.get_width() - total_w) // 2
        y = int(self.assets.sizes["table_pos"][1] + self.assets.sizes["table_size"][1] // 2 - ch // 2)
        for i, code in enumerate(self.community):
            img = self.assets.get_card_image(code)
            img = pygame.transform.smoothscale(img, (cw, ch))
            self.screen.blit(img, (start_x + i * (cw + spacing), y))

    def draw(self):
        self.screen.fill(self.assets.colors["bg_table"])
        table_img = self.assets.get_table_image()
        table_pos = self.assets.sizes["table_pos"]
        if table_img:
            self.screen.blit(table_img, (int(table_pos[0]), int(table_pos[1])))
        self._draw_community()
        self._draw_pot()
        # draw players
        for pa in self.player_areas:
            pa.draw(self.screen, card_zoom=self.card_zoom, show_hole=False)
        self._draw_dealer_button(self.screen)
        # draw slider if visible
        if self.show_slider:
            self.bet_slider.draw(self.screen)
            # draw confirm text/button
            confirm_rect = pygame.Rect(self.bet_slider.rect.right + 12, self.bet_slider.rect.top, 80, self.bet_slider.rect.height)
            pygame.draw.rect(self.screen, (30, 120, 60), confirm_rect, border_radius=int(6 * self.assets.min_size_scale))
            txt = self.assets.fonts["main"].render("Bet", True, self.assets.colors["white"])
            self.screen.blit(txt, (confirm_rect.centerx - txt.get_width() // 2, confirm_rect.centery - txt.get_height() // 2))
        # draw widgets
        super().draw()
