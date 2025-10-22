import pygame
import random
import os
import sys

# Add the parent directory to path to import chips.py
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from gui.chips import get_chips
from gui.window_base import WindowBase
from main_code.gui.buttons import Button

class GameWindow(WindowBase):
    def __init__(self, screen, assets, controller):
        super().__init__(screen, assets)
        self.controller = controller
        self.state = None
        self.players = []
        self.community_cards = []
        self.pot_value = 0
        self.deal_pressed = False
        self.human_acted = False
        self.action_buttons = []
        self.bet_amount = 0
        self.current_bb = 20  # Default big blind value
        
        # Chip display variables
        self.player_bet_chips = {}  # Track chips for each player's current bet
        self.pot_chips = []  # Chips in the main pot
        
        # Initialize player positions and UI state
        self._init_player_positions()
        self._create_action_buttons()
        self._create_bet_controls()
        
    def _init_player_positions(self):
        """Initialize player positions around the table"""
        table_w, table_h = self.assets.sizes["table_size"]
        tx, ty = self.assets.sizes["table_pos"]
        
        # Calculate player positions around the table
        X1 = tx + 700 / 1000 * table_w
        Y1 = ty + table_h
        X2 = self.screen.get_width() - X1
        Y2 = self.screen.get_height() - Y1
        X3 = tx
        Y3 = self.screen.get_height() / 2
        X4 = self.screen.get_width() - X3
        
        self.player_coords = [
            (X1, Y1), (X2, Y1), (X3, Y3), 
            (X2, Y2), (X1, Y2), (X4, Y3)
        ]
        
    def _create_action_buttons(self):
        """Create fold, check/call, and bet/raise buttons"""
        screen_w, screen_h = self.screen.get_size()
        button_w = self.assets.sizes["button_w"]
        button_h = self.assets.sizes["button_h"]
        
        # Position buttons at bottom right
        fold_x = screen_w - (button_w + 80 * self.assets.WSCALE) * 2 - 4/5 * button_w * self.assets.WSCALE + 80 * self.assets.WSCALE
        fold_y = screen_h - (button_h + 20 * self.assets.HSCALE) * 2 - 2/5 * button_w * self.assets.HSCALE
        
        check_x = fold_x
        check_y = screen_h - button_h - 2/5 * button_w * self.assets.HSCALE
        
        bet_x = screen_w - button_w - 4/5 * button_w * self.assets.WSCALE
        bet_y = screen_h - button_h - 2/5 * button_w * self.assets.HSCALE
        
        # Create action buttons
        self.fold_button = Button(
            "Fold", (fold_x, fold_y), self.assets, 
            on_click=lambda: self._perform_action("fold")
        )
        
        self.check_button = Button(
            "Check", (check_x, check_y), self.assets,
            on_click=lambda: self._perform_action("call")
        )
        
        self.bet_button = Button(
            "Bet", (bet_x, bet_y), self.assets,
            on_click=lambda: self._perform_action("raise", self.bet_amount)
        )
        
        self.action_buttons = [self.fold_button, self.check_button, self.bet_button]
        
        # Deal button at top center
        deal_x = screen_w / 2 - button_w / 2
        deal_y = screen_h / 6 - button_h / 2
        self.deal_button = Button(
            "Deal", (deal_x, deal_y), self.assets,
            on_click=self._start_hand
        )
        
        self.widgets.extend([self.deal_button] + self.action_buttons)
    
    def _create_bet_controls(self):
        """Create bet amount controls"""
        screen_w, screen_h = self.screen.get_size()
        button_w = self.assets.sizes["button_w"]
        button_h = self.assets.sizes["button_h"]
        
        # Bet amount display position
        self.bet_display_x = screen_w - button_w - 4/5 * button_w * self.assets.WSCALE
        self.bet_display_y = screen_h - button_h * 2 - 2/5 * button_w * self.assets.HSCALE
        
        # Simple bet adjustment buttons
        inc_x = self.bet_display_x + button_w + 10
        inc_y = self.bet_display_y
        self.increase_bet = Button(
            "+", (inc_x, inc_y), self.assets, 
            size=(button_h, button_h),
            on_click=self._increase_bet
        )
        
        dec_x = self.bet_display_x - button_h - 10
        dec_y = self.bet_display_y
        self.decrease_bet = Button(
            "-", (dec_x, dec_y), self.assets,
            size=(button_h, button_h),
            on_click=self._decrease_bet
        )
        
        # Pre-set bet amount buttons
        self.bet_preset_buttons = []
        presets = [
            ("1/2 Pot", 0.5),
            ("2/3 Pot", 0.66),
            ("Pot", 1.0),
            ("All In", -1)
        ]
        
        for i, (label, multiplier) in enumerate(presets):
            preset_x = self.bet_display_x - button_w
            preset_y = self.bet_display_y - (i + 1) * (button_h + 5)
            button = Button(
                label, (preset_x, preset_y), self.assets,
                size=(button_w, button_h),
                on_click=lambda m=multiplier: self._set_preset_bet(m)
            )
            self.bet_preset_buttons.append(button)
        
        self.widgets.extend([self.increase_bet, self.decrease_bet] + self.bet_preset_buttons)
    
    def _increase_bet(self):
        """Increase bet amount"""
        if self.state and self.state.get("running", False):
            human_player = next((p for p in self.state["players"] if p["id"] == self.controller.human_player_id), None)
            if human_player:
                max_bet = human_player.get("chips", 0)
                min_raise = self.state.get("min_raise", self.current_bb)
                self.bet_amount = min(max_bet, self.bet_amount + min_raise)
    
    def _decrease_bet(self):
        """Decrease bet amount"""
        if self.state and self.state.get("running", False):
            min_raise = self.state.get("min_raise", self.current_bb)
            min_bet = self.state.get("last_bet", 0) + min_raise
            self.bet_amount = max(min_bet, self.bet_amount - min_raise)
    
    def _set_preset_bet(self, multiplier):
        """Set bet amount based on preset multiplier"""
        if not self.state or not self.state.get("running", False):
            return
            
        human_player = next((p for p in self.state["players"] if p["id"] == self.controller.human_player_id), None)
        if not human_player:
            return
            
        if multiplier == -1:  # All in
            self.bet_amount = human_player.get("chips", 0)
        else:
            pot = self.state.get("pot", 0)
            min_raise = self.state.get("min_raise", self.current_bb)
            base_bet = self.state.get("last_bet", 0) + min_raise
            preset_bet = max(base_bet, int(pot * multiplier))
            self.bet_amount = min(human_player.get("chips", 0), preset_bet)
    
    def _get_chip_images_for_amount(self, amount):
        """Get appropriate chip images for a given amount using chips.py"""
        if amount <= 0:
            return []
        
        # Get chip names from chips.py
        chip_names = get_chips(self.current_bb, amount)
        
        # Convert names to actual images from assets
        chip_images = []
        for chip_name in chip_names:
            if chip_name in self.assets.images["chips"]:
                chip_images.append(self.assets.images["chips"][chip_name])
            else:
                # Fallback: use first available chip image
                if self.assets.images["chips"]:
                    chip_images.append(list(self.assets.images["chips"].values())[0])
        
        return chip_images
    
    def _start_hand(self):
        """Start a new hand"""
        self.controller.start_hand()
        self.deal_pressed = True
        self.bet_amount = 0
        self.player_bet_chips = {}
        self.pot_chips = []
        self._update_state()
        
    def _perform_action(self, action, amount=0):
        """Perform a poker action (fold, call, raise)"""
        if not self.state or not self.state.get("running", False):
            return
            
        human_player = next((p for p in self.state["players"] if p["id"] == self.controller.human_player_id), None)
        if not human_player or human_player.get("folded", False):
            return
        
        # Store bet chips for display
        if action in ["call", "raise"] and amount > 0:
            player_id = self.controller.human_player_id
            self.player_bet_chips[player_id] = {
                'amount': amount,
                'chips': self._get_chip_images_for_amount(amount)
            }
        
        self.controller.perform_action(action, amount)
        self.human_acted = True
        self._update_state()
    
    def _update_state(self):
        """Update game state from controller"""
        self.state = self.controller.get_state()
        
        # Update current big blind from table state if available
        if hasattr(self.controller.table, 'blinds'):
            self.current_bb = self.controller.table.blinds[-1] if self.controller.table.blinds else 20
        
        # Update players
        self.players = []
        for i, player_data in enumerate(self.state["players"]):
            # Add chip information to player data
            player_invested = player_data.get("total_invested", 0)
            player_data["bet_chips"] = self._get_chip_images_for_amount(player_invested)
            
            player_gui = PlayerGUI(player_data, i, self.assets, self.player_coords)
            self.players.append(player_gui)
        
        # Update community cards
        self.community_cards = []
        for i, card in enumerate(self.state.get("community", [])):
            self.community_cards.append(CommunityCard(card, i, self.assets))
        
        # Update pot value and chips
        self.pot_value = self.state.get("pot", 0)
        self.pot_chips = self._get_chip_images_for_amount(self.pot_value)
        
        # Update button states based on game state
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button states based on current game state"""
        if not self.state or not self.state.get("running", False):
            # Show only deal button when no hand is active
            for button in self.action_buttons + self.bet_preset_buttons + [self.increase_bet, self.decrease_bet]:
                button.visible = False
            self.deal_button.visible = True
            return
        
        # Show action buttons during active hand
        self.deal_button.visible = False
        for button in self.action_buttons + self.bet_preset_buttons + [self.increase_bet, self.decrease_bet]:
            button.visible = True
        
        # Update check/call button text based on game state
        human_player = next((p for p in self.state["players"] if p["id"] == self.controller.human_player_id), None)
        if human_player:
            last_bet = self.state.get("last_bet", 0)
            player_invested = human_player.get("round_invested", 0)
            to_call = max(0, last_bet - player_invested)
            
            if to_call == 0:
                self.check_button.text = "Check"
            else:
                self.check_button.text = f"Call {to_call}"
            self.check_button._update_rendered_text()
            
            # Update bet button text
            if to_call > 0:
                self.bet_button.text = "Raise"
            else:
                self.bet_button.text = "Bet"
            self.bet_button._update_rendered_text()
    
    def handle_event(self, event):
        """Handle pygame events"""
        super().handle_event(event)
        
        # Handle additional events like bet amount adjustment
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d and not self.state.get("running", False):
                self._start_hand()
            elif event.key == pygame.K_f and self.state.get("running", False):
                self._perform_action("fold")
            elif event.key == pygame.K_c and self.state.get("running", False):
                self._perform_action("call")
            elif event.key == pygame.K_r and self.state.get("running", False):
                self._perform_action("raise", self.bet_amount)
            elif event.key == pygame.K_UP and self.state.get("running", False):
                self._increase_bet()
            elif event.key == pygame.K_DOWN and self.state.get("running", False):
                self._decrease_bet()
    
    def update(self, dt):
        """Update game state (called each frame)"""
        # Update from controller (for bot moves, etc.)
        if self.state and self.state.get("running", False) and not self.human_acted:
            self.controller.update()
            self._update_state()
        
        self.human_acted = False
    
    def draw(self):
        """Draw the entire game window"""
        # Draw background
        self.screen.fill(self.assets.colors["bg_table"])
        
        # Draw table
        table_img = self.assets.get_table_image()
        table_x, table_y = self.assets.sizes["table_pos"]
        self.screen.blit(table_img, (table_x, table_y))
        
        # Draw community cards
        for card in self.community_cards:
            card.draw(self.screen)
        
        # Draw pot and chips
        self._draw_pot()
        
        # Draw players
        for player in self.players:
            player.draw(self.screen)
        
        # Draw bet amount display
        if self.state and self.state.get("running", False):
            self._draw_bet_display()
        
        # Draw widgets (buttons)
        super().draw()
    
    def _draw_pot(self):
        """Draw the pot and chips in the center of the table"""
        if self.pot_value <= 0:
            return
            
        table_x, table_y = self.assets.sizes["table_pos"]
        table_w, table_h = self.assets.sizes["table_size"]
        
        pot_x = table_x + table_w / 2
        pot_y = table_y + table_h / 2 - self.assets.sizes["card_h"] / 4
        
        # Draw chips using assets chip images
        if self.pot_chips:
            chip_w, chip_h = self.assets.sizes["chip_w"], self.assets.sizes["chip_h"]
            chip_x = pot_x - chip_w / 2
            chip_y = pot_y - chip_h / 2
            
            # Draw chips in a realistic stack
            max_chips_to_draw = min(20, len(self.pot_chips))  # Limit for visibility
            for i in range(max_chips_to_draw):
                chip_img = self.pot_chips[i % len(self.pot_chips)]
                offset_y = i * 2  # Small vertical offset for stack effect
                offset_x = (i % 3 - 1) * 2  # Small horizontal spread
                self.screen.blit(chip_img, (chip_x + offset_x, chip_y - offset_y))
        
        # Draw pot value text
        pot_text = self.assets.fonts["main"].render(f"Pot: {self.pot_value}", True, (255, 255, 255))
        text_rect = pot_text.get_rect(center=(pot_x, pot_y + 40))
        self.screen.blit(pot_text, text_rect)
    
    def _draw_bet_display(self):
        """Display current bet amount"""
        bet_text = self.assets.fonts["main"].render(f"Bet: {self.bet_amount}", True, (255, 255, 255))
        text_rect = bet_text.get_rect(center=(self.bet_display_x + self.assets.sizes["button_w"] / 2, self.bet_display_y))
        self.screen.blit(bet_text, text_rect)
    
    def resize(self, new_size):
        """Handle window resize"""
        super().resize(new_size)
        self._init_player_positions()
        self._create_action_buttons()
        self._create_bet_controls()
        
        # Update player positions
        for i, player in enumerate(self.players):
            if i < len(self.player_coords):
                player.x, player.y = self.player_coords[i]
                player.resize()


class PlayerGUI:
    """Represents a player's GUI elements"""
    def __init__(self, player_data, position_index, assets, player_coords):
        self.player_data = player_data
        self.position_index = position_index
        self.assets = assets
        self.x, self.y = player_coords[position_index] if position_index < len(player_coords) else (0, 0)
        
        # Chip display for current bet
        self.bet_chips = player_data.get("bet_chips", [])
        
        # Calculate positions for profile, cards, chips
        self._calculate_positions()
        self._load_profile_image()
        self._create_cards()
        
    def _calculate_positions(self):
        """Calculate positions for player UI elements"""
        profile_w, profile_h = self.assets.sizes["profile"]
        card_w, card_h = self.assets.sizes["card_w"], self.assets.sizes["card_h"]
        chip_w, chip_h = self.assets.sizes["chip_w"], self.assets.sizes["chip_h"]
        
        # Profile picture position
        self.profile_x = self.x - profile_w / 2
        self.profile_y = self.y - profile_h / 2
        
        # Card positions (next to profile)
        self.card_x = self.profile_x + profile_w / 2 - card_w - 5
        self.card_y = self.profile_y + profile_h - card_h
        
        # Chip stack position for current bet
        self.chip_x = self.profile_x - chip_w
        self.chip_y = self.profile_y + profile_h / 2 - chip_h / 2
        
        # Player info position
        self.info_x = self.profile_x
        self.info_y = self.profile_y + profile_h + 5
        
    def _load_profile_image(self):
        """Load and scale profile image"""
        profile_name = self.player_data.get("name", "default")
        self.profile_img = self.assets.get_profile_image(profile_name)
        
        if not self.profile_img:
            # Create a default profile image
            profile_size = self.assets.sizes["profile"]
            self.profile_img = pygame.Surface(profile_size, pygame.SRCALPHA)
            color = (100, 100, 200) if not self.player_data.get("folded", False) else (100, 100, 100)
            pygame.draw.ellipse(self.profile_img, color, (0, 0, *profile_size))
            
            # Add initial letter
            font = self.assets.fonts["main"]
            text_color = (255, 255, 255) if not self.player_data.get("folded", False) else (150, 150, 150)
            text = font.render(self.player_data.get("name", "?")[0], True, text_color)
            text_rect = text.get_rect(center=(profile_size[0]//2, profile_size[1]//2))
            self.profile_img.blit(text, text_rect)
    
    def _create_cards(self):
        """Create card objects for this player"""
        self.cards = []
        hole_cards = self.player_data.get("hole_cards", [])
        is_folded = self.player_data.get("folded", False)
        
        for i, card_code in enumerate(hole_cards):
            card = HoleCard(card_code, i, is_folded, 
                           self.card_x, self.card_y, self.assets)
            self.cards.append(card)
    
    def draw(self, screen):
        """Draw player on screen"""
        # Draw profile picture
        screen.blit(self.profile_img, (self.profile_x, self.profile_y))
        
        # Draw player name and chips
        name = self.player_data.get("name", "Player")
        chips = self.player_data.get("chips", 0)
        folded = self.player_data.get("folded", False)
        
        text_color = (255, 215, 0) if not folded else (150, 150, 150)  # Gold for active, gray for folded
        name_text = self.assets.fonts["small"].render(
            f"{name}: {chips}", True, text_color
        )
        name_rect = name_text.get_rect(midtop=(self.x, self.info_y))
        screen.blit(name_text, name_rect)
        
        # Draw cards if not folded or if showing at showdown
        if not folded:
            for card in self.cards:
                card.draw(screen)
        
        # Draw current bet chips
        self._draw_bet_chips(screen)
        
        # Draw action text if available
        action = self.player_data.get("action", "")
        if action:
            action_color = (0, 0, 0) if not folded else (100, 100, 100)
            action_text = self.assets.fonts["small"].render(action, True, action_color)
            action_rect = action_text.get_rect(midtop=(self.x, self.info_y + 25))
            screen.blit(action_text, action_rect)
        
    def _draw_bet_chips(self, screen):
        """Draw chip stack for player's current bet"""
        if not self.bet_chips:
            return
            
        chip_w, chip_h = self.assets.sizes["chip_w"], self.assets.sizes["chip_h"]
        
        # Draw chips in a stack next to the player
        max_chips_to_draw = min(10, len(self.bet_chips))
        for i in range(max_chips_to_draw):
            chip_img = self.bet_chips[i]
            offset_y = i * 2  # Small vertical offset for stack effect
            offset_x = (i % 2) * 3  # Small horizontal spread
            screen.blit(chip_img, (self.chip_x + offset_x, self.chip_y - offset_y))
    
    def resize(self):
        """Handle resize"""
        self._calculate_positions()
        self._load_profile_image()
        self._create_cards()


class Card:
    """Base class for cards"""
    def __init__(self, card_code, position, assets, showing=True):
        self.card_code = card_code
        self.position = position
        self.assets = assets
        self.showing = showing
        self._load_image()
    
    def _load_image(self):
        """Load card image"""
        if self.showing and self.card_code:
            self.image = self.assets.get_card_image(self.card_code)
        else:
            self.image = self.assets.get_card_back()
    
    def draw(self, screen):
        """Draw card on screen"""
        screen.blit(self.image, (self.x, self.y))


class HoleCard(Card):
    """Player's hole cards"""
    def __init__(self, card_code, position, folded, x, y, assets):
        super().__init__(card_code, position, assets, showing=not folded)
        self.x = x + position * (self.assets.sizes["card_w"] - (0 if self.showing else 0.5))
        self.y = y


class CommunityCard(Card):
    """Community cards in the middle of the table"""
    def __init__(self, card_code, position, assets):
        super().__init__(card_code, position, assets, showing=True)
        screen_w, screen_h = assets.current_resolution
        card_w, card_h = assets.sizes["card_w"], assets.sizes["card_h"]
        card_backpad = assets.sizes["card_backpad"]
        
        self.x = screen_w / 2 - 2.5 * card_w - 2 * card_backpad + position * (card_w + card_backpad)
        self.y = screen_h / 2 - card_h / 2