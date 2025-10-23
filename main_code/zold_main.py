import pygame, random, os, asyncio
import pygame.image
import sys
from poker import start, Bot, Human
from main_code.gui.chips import get_chips
from main_code.logic.backbone_misc import *
from datetime import datetime



# from main_misc import *
# python -m http.server 8000

# All players should have a player id - maybe just random number
# find where check of human player is 
# BUG cant go all in especially when big blind?
# BUG this happens because chips current round invested are not considered when betting 

# Check if winner.py bug fixed
# TODO scale once (black screen when scaling)
# line 578?, 744, 174
# TODO show cards used with winning hands and winner (maybe show winning hand name), darken players who have folded
# BUG when changing bet action text changed ?
# TODO speed button
# BUG slider doesnt allow all in
# BUG action text glitch when player is choosing bet and opp has done a large bet (only when player on right?)
# TODO make LHS buttons and RHS buttons
# TODO double blinds button
# BUG sometimes click cant close window button (maybe lag or because of event loop)

pygame.init()
t = datetime.now()
random.seed(t.microsecond * t.second * t.minute)

def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


dirname = os.path.dirname(__file__)

# SCREENSIZE = (1400, 900)
INTENDEDSIZE = (1700, 900)
# INTENDEDSIZE = (1400, 900)

# ENTIRESCREEN = (pygame.display.Info().current_w, pygame.display.Info().current_h)
TEMPSCALE = Scale(
    min(
        pygame.display.Info().current_w / INTENDEDSIZE[0],
        pygame.display.Info().current_h / INTENDEDSIZE[1],
        key=lambda x: abs(1 - x),
    )
)

print((pygame.display.Info().current_w, pygame.display.Info().current_h))
FULLSCREEN = (
    INTENDEDSIZE[0] * TEMPSCALE * 0.90,
    INTENDEDSIZE[1] * TEMPSCALE * 0.90,
)

SCREENSIZE = FULLSCREEN

valFilename = {}
suitFilename = {"C": "clubs", "D": "diamonds", "H": "hearts", "S": "spades"}
for k, v in zip(
    "23456789TJQKA",
    ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"],
):
    valFilename[k] = v

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
clock = pygame.time.Clock()

if "python" not in os.path.basename(sys.executable):
    SCREENSIZE = (1700 * 1.5, 900 * 1.5)

#figure out what this actually does
# screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
screen = pygame.display.set_mode(
    SCREENSIZE, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
)
pygame.display.set_caption("Poker Game")


def init_images():
    global WSCALE, HSCALE, MSCALE
    global tableImage, TableX, TableY, table_image_size
    global BUTTONW, BUTTONH, BUTTON_WDGE_BUFFER, BUTTON_HDGE_BUFFER, BUTTON_BUFFER_X, BUTTON_BUFFER_Y
    global CHIPW, CHIPH, CARDW, CARDH, CARDB, PROFILE_SIZE
    global player_coords
    global fonts

    WSCALE, HSCALE = Scale(screen.get_width() / INTENDEDSIZE[0]), Scale(
        screen.get_height() / INTENDEDSIZE[1]
    )
    MSCALE = min(WSCALE, HSCALE)

    BUTTONW = 150 * WSCALE
    BUTTONH = 50 * HSCALE
    BUTTON_WDGE_BUFFER = 4 / 5 * BUTTONW * WSCALE
    BUTTON_HDGE_BUFFER = 2 / 5 * BUTTONW * HSCALE
    BUTTON_BUFFER_X = 80 * WSCALE
    BUTTON_BUFFER_Y = 20 * HSCALE

    CHIPW, CHIPH = 40 * WSCALE, 20 * HSCALE

    tableImage = pygame.image.load(
        rf"{dirname}/images/misc/poker-table.png"
    ).convert_alpha()
    table_image_size = (868 * WSCALE, 423 * HSCALE)
    tableImage = pygame.transform.smoothscale(tableImage, table_image_size)
    TableX = (screen.get_width() / 2) - (table_image_size[0] / 2)
    TableY = (screen.get_height() / 2) - (table_image_size[1] / 2)

    CARDW, CARDH, CARDB = (
        59 / 1000 * table_image_size[0],
        173 / 1000 * table_image_size[1],
        7 / 1000 * table_image_size[1],
    )

    PROFILE_SIZE = (125 * MSCALE, 125 * MSCALE)
    X1 = TableX + 700 / 1000 * table_image_size[0]
    Y1 = TableY + table_image_size[1]

    X2 = screen.get_width() - X1
    Y2 = screen.get_height() - Y1

    X3 = TableX
    Y3 = screen.get_height() / 2

    X4 = screen.get_width() - X3

    player_coords = [
        (X1, Y1),
        (X2, Y1),
        (X3, Y3),
        (X2, Y2),
        (X1, Y2),
        (X4, Y3),
    ]

    fonts = Fonts()


class Fonts:
    def __init__(self):
        self.small_font = pygame.font.Font(
            rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 30 * WSCALE
        )
        self.main_font = pygame.font.Font(
            rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 40 * WSCALE
        )
        self.large_font = pygame.font.Font(
            rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 80 * WSCALE
        )
        self.title_font = pygame.font.Font(
            rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 120 * WSCALE
        )


init_images()


class Button:
    def __init__(
        self,
        x,
        y,
        colour,
        label,
        BW=None,
        BH=None,
        image=None,
        border=True,
        font_attr="main_font",
        text_colour=WHITE,
        square=False,
    ):
        self.original_x = x / WSCALE
        self.original_y = y / HSCALE
        self.original_BW = (BW if BW else BUTTONW) / WSCALE
        self.original_BH = (BH if BH else BUTTONH) / HSCALE

        self.colour = colour
        self.label = label
        self.font_attr = font_attr
        self.text_colour = text_colour
        self.image = image
        self.border = border
        self.square = square
        self.resize()

    def update_font(self):
        self.font = getattr(fonts, self.font_attr)
        self.text = self.font.render(self.label, True, self.text_colour)
        self.set_text_rect()

    def resize(self):
        self.x = self.original_x * WSCALE
        self.y = self.original_y * HSCALE
        self.BW = self.original_BW * WSCALE

        self.BH = self.BW if self.square else self.original_BH * HSCALE

        if not isinstance(self, Zoom):
            if self.image == None:
                self.background = pygame.Surface((self.BW, self.BH))
                self.background.fill(self.colour)
            else:
                self.background = pygame.transform.smoothscale(
                    self.image, (self.BW, self.BH)
                )

            if self.border:
                pygame.draw.rect(
                    self.background, BLACK, (0, 0, self.BW, self.BH), 3 * MSCALE
                )

            self.update_font()

    def set_text_rect(self):
        self.text_rect = self.text.get_rect(
            center=(self.x + self.BW / 2, self.y + self.BH / 2)
        )

    def draw(self):
        screen.blit(self.background, (self.x, self.y))
        screen.blit(self.text, self.text_rect)

    def add_table(self, table):
        self.table = table

    def add_window(self, window):
        self.window = window

    def check_press(self, mx, my):
        if self.x <= mx <= self.x + self.BW and self.y <= my <= self.y + self.BH:
            self.pressed_action()


class Menu_Button(Button):
    def __init__(
        self,
        x,
        y,
        colour,
        text,
        w_change,
        BW=None,
        BH=None,
        image=None,
        border=True,
        see=True,
        font_attr="main_font",
        text_colour=WHITE,
        square=False,
    ):
        super().__init__(
            x,
            y,
            colour,
            text,
            BW,
            BH,
            image,
            border,
            font_attr=font_attr,
            text_colour=text_colour,
            square=square,
        )

        if see:
            self.background.set_alpha(128)

        self.w_change = w_change

    def pressed_action(self):
        self.window.set_current_window(self.w_change)


class Zoom(Button):
    def __init__(self, x, y, width):
        self.original_x = x / WSCALE
        self.original_y = y / HSCALE
        self.original_BW = (width if width else BUTTONW) / WSCALE
        self.original_BH = (width if width else BUTTONH) / HSCALE
        self.current = 0
        self.initial = True
        self.square = True
        # self.BW = self.BH = width

        self.resize()

    def draw(self):
        image = self.zoom_in if self.current < 2 else self.zoom_out
        screen.blit(image, (self.x, self.y))

    def resize(self):
        super().resize()

        self.zoom_in = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/misc/zoom-in.png").convert_alpha(),
            (self.BW, self.BW),
        )

        self.zoom_out = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/misc/zoom-out.png").convert_alpha(),
            (self.BW, self.BW),
        )

        if not self.initial:
            # c = self.current
            # self.current = 0
            # for r in range(c):
            #     self.pressed_action()
            self.set_current(0)

        self.initial = False

    def set_current(self, current):
        while self.current != current:
            self.pressed_action()

    def change_card_size(self):
        global CARDW, CARDH, CARDB
        CARDW = [1.5, 2 / 1.5, 1 / 2][self.current] * CARDW
        CARDH = [1.5, 2 / 1.5, 1 / 2][self.current] * CARDH
        # CARDB = [0, 0, 7 / 1000 * table_image_size[1]][self.current]

    def pressed_action(self):

        self.change_card_size()
        self.current = (self.current + 1) % 3

        self.window.reset_cards()


class DealButton(Button):
    pressed = False

    def __init__(
        self,
        x,
        y,
        colour,
        text,
        BW=None,
        BH=None,
        image=None,
        border=True,
        font_attr="main_font",
        text_colour=WHITE,
    ):
        super().__init__(
            x,
            y,
            colour,
            text,
            BW,
            BH,
            image,
            border,
            font_attr=font_attr,
            text_colour=text_colour,
        )

        self.pressed = False

    def pressed_action(self):
        self.pressed = True

        if self.table.running == True:
            return

        self.table.start_hand()
        self.window.start_hand()


class ActionButton(Button):
    def __init__(
        self,
        x,
        y,
        colour,
        text,
        action,
        BW=None,
        BH=None,
        border=True,
        font_attr="main_font",
        text_colour=WHITE,
    ):
        super().__init__(
            x,
            y,
            colour,
            text,
            BW,
            BH,
            border=border,
            font_attr=font_attr,
            text_colour=text_colour,
        )
        self.action = action

    def pressed_action(self):
        if isinstance(self.table.current_player, Bot):
            return

        bet = 0
        if isinstance(self, BetButton):
            bet = self.pbet - self.table.human_player.round_invested
            # bet = self.pbet

        self.window.human_acted = self.window.acted = True  # TODO change
        self.window.end = self.table.single_move(action=(self.action, bet))
        self.window.players[0].update(self.table.blinds[-1])
        self.window.betButton.pbet = 0
        self.window.betButton.slider.update_slider()


class CheckButton(ActionButton):
    def set_text(self):

        self.text = fonts.main_font.render(
            (
                "Check"
                if self.table.human_player.round_invested == self.table.last_bet
                else "Call"
            ),
            True,
            WHITE,
        )

    def draw(self):
        self.text_rect = self.text.get_rect(
            center=(self.x + self.BW / 2, self.y + self.BH / 2)
        )
        super().draw()


class BetButton(ActionButton):

    def __init__(
        self,
        x,
        y,
        colour,
        text,
        action,
        s_buttons=None,
        font_attr="main_font",
        text_colour=WHITE,
    ):
        super().__init__(
            x, y, colour, text, action, font_attr=font_attr, text_colour=text_colour
        )

        if s_buttons == None:
            s_buttons = [
                [(2.5, "bb"), (8, "bb"), (2.5, "p"), (-1, "all")],
                [(0.5, "p"), (1, "p"), (2, "p"), (-1, "all")],
            ]
        self.increase = CBetButton(
            x + self.BW,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_HDGE_BUFFER,
            (34, 140, 34),
            "+",
            1,
            self,
        )
        self.decrease = CBetButton(
            x - BUTTONW / 4,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_HDGE_BUFFER,
            (34, 140, 34),
            "-",
            -1,
            self,
        )
        self.slider = Slider(
            x,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_HDGE_BUFFER,
            (169, 169, 169),
            "",
            self,
        )

        self.set_buttons = []

        sb_count = len(s_buttons[0])
        e = 1.2
        TW = (self.increase.x - self.decrease.x + self.decrease.BW) * e
        # TW = (screen.get_width() - self.decrease.x) * e
        sb_buffer = TW // 30
        SW = (TW - sb_buffer * (sb_count - 1)) // sb_count

        for i in range(sb_count):
            self.set_buttons.append(
                SetBetButton(
                    # screen.get_width() - TW + (SW + sb_buffer) * i,
                    round(self.decrease.x - (TW - TW / e) / 2 + (SW + sb_buffer) * i),
                    round(self.decrease.y - BUTTONH - 5),
                    (14, 74, 146),
                    "",
                    self,
                    [x[i] for x in s_buttons],
                    BW=round(SW),
                    font_attr="small_font",
                )
            )

        self.buttons = [self.increase, self.decrease, self.slider] + self.set_buttons
        self.pbet = 0

    def draw(self):
        super().draw()
        text = fonts.main_font.render(str(self.pbet), True, BLACK)
        text_rect = text.get_rect(
            center=(self.x + self.BW / 2, self.set_buttons[0].y - BUTTONH // 2)
        )
        screen.blit(text, text_rect)

    def add_table(self, table):
        super().add_table(table)


class CBetButton(Button):
    def __init__(
        self,
        x,
        y,
        colour,
        text,
        co,
        bet_button,
        border=True,
        font_attr="main_font",
        text_colour=WHITE,
    ):
        super().__init__(
            x,
            y,
            colour,
            text,
            BW=BUTTONW // 4,
            font_attr=font_attr,
            text_colour=text_colour,
        )
        self.co = co
        self.bet_button = bet_button

    def pressed_action(self):  # TODO improve

        val = int(self.bet_button.pbet + self.table.blinds[-1] * self.co * 0.5)  # bad

        val = 0 if val < 0 else min(self.table.human_player.chips, val)
        self.bet_button.pbet = val
        self.window.players[0].update(self.table.blinds[-1], extra=self.bet_button.pbet)
        self.bet_button.slider.update_slider()


class SetBetButton(Button):
    def __init__(
        self,
        x,
        y,
        colour,
        text,
        bet_button,
        set_action,
        BW=None,
        BH=None,
        image=None,
        border=True,
        font_attr="small_font",
        text_colour=WHITE,
    ):
        super().__init__(
            x,
            y,
            colour,
            text,
            BW,
            BH,
            image,
            border,
            font_attr=font_attr,
            text_colour=text_colour,
        )

        self.bet_button = bet_button
        self.set_action = set_action

    def pressed_action(self):
        r_action = self.get_r_action()
        if r_action[0] == -1:
            val = self.table.human_player.chips
        elif r_action[1] == "bb":
            val = self.table.blinds[-1] * r_action[0]
        else:
            val = self.table.get_pot() * r_action[0]

        self.bet_button.pbet = round(min(val, self.table.human_player.chips))
        self.window.players[0].update(self.table.blinds[-1], extra=self.bet_button.pbet)
        self.bet_button.slider.update_slider()

    def get_r_action(self):
        return self.set_action[0 if self.table.r == 0 else 1]

    def update_text(self):
        r_action = self.get_r_action()
        if r_action[0] == -1:
            text = "All"
        elif r_action[1] == "bb":
            text = str(round(self.table.blinds[-1] * r_action[0]))
        else:
            text = str(r_action[0]) + "x"

        self.text = fonts.small_font.render(text, True, WHITE)
        self.set_text_rect()

    def draw(self):
        self.update_text()

        # print((self.x, self.y, self.BW, self.BH))
        pygame.draw.rect(
            screen,
            self.colour,
            (self.x, self.y, self.BW, self.BH),
            border_radius=min(self.BW, self.BH) // 3,
        )
        pygame.draw.rect(
            screen,
            BLACK,
            (self.x, self.y, self.BW, self.BH),
            border_radius=min(self.BW, self.BH) // 3,
            width=3,
        )

        screen.blit(self.text, self.text_rect)


class Slider(Button):
    def __init__(
        self,
        x,
        y,
        colour,
        text,
        bet_button,
        l_colour=BLACK,
        l_height=10,
        SW=BUTTONW / 6,
    ):
        self.l_colour = l_colour
        self.l_height = l_height
        self.bet_button = bet_button
        self.s_x = x
        self.original_SW = SW / WSCALE

        super().__init__(x, y, colour, text)

    def draw(self):
        pygame.draw.rect(
            screen,
            self.l_colour,
            (self.x, self.y + (self.BH - self.l_height) / 2, self.BW, self.l_height),
        )

        pygame.draw.rect(screen, self.colour, (self.s_x, self.y, self.SW, self.BH))

    def resize(self):
        self.SW = self.original_SW * WSCALE
        super().resize()

        if hasattr(self, "table"):
            self.update_slider()

    def check_press(self, mx, my):
        if (
            self.x - self.BW / 20 <= mx <= self.x + self.BW
            and self.y <= my <= self.y + self.BH
        ):
            self.pressed_action(mx)

    def update_slider(self):
        extra_p = (
            0
            if not self.table.human_player.chips
            else min(1, self.bet_button.pbet / self.table.human_player.chips)
        )
        self.s_x = self.x + extra_p * (self.BW - self.SW)

    def pressed_action(self, mx):
        self.s_x = self.x if mx < self.x else min(mx, self.x + self.BW - self.SW)
        percentage = 0 if mx < self.x else min((mx - self.x) / (self.BW - self.SW), 1)
        self.bet_button.pbet = int(percentage * self.table.human_player.chips)
        self.window.players[0].update(self.table.blinds[-1], extra=self.bet_button.pbet)


class Card:

    def __init__(self, value, order, showing=True):
        self.value = value
        self.order = order
        self.showing = showing
        self.set_image()

    def set_image(self):
        card_path = f"{valFilename[self.value[0]]}_of_{suitFilename[self.value[1]]}"
        card_path = card_path + "2" if self.value[0] in "JQK" else card_path
        imagePath = rf"{dirname}/images/cards/{card_path}.png"
        # imagePath = rf"{dirname}/images/cards/SVG/{card_path}.svg"

        self.image = pygame.transform.smoothscale(
            pygame.image.load(imagePath).convert_alpha(), (CARDW, CARDH)
        )

        self.card_back = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/cards/card_back.png").convert_alpha(),
            (CARDW, CARDH),
        )

    def draw(self):
        difference = self.get_difference()

        image = self.image if self.showing else self.card_back
        screen.blit(
            image,
            (
                self.STARTING_X + difference,
                self.STARTING_Y,
            ),
        )

    def get_difference(self):
        return (CARDW + CARDB) * (self.order - 1)


class HoleCard(Card):

    def get_coords(self, x, y):
        return (
            x + PROFILE_SIZE[0] / 2 - CARDW - CARDB / 2,
            y + PROFILE_SIZE[1] - CARDH,
        )

    def __init__(self, value, order, r_i, showing, x, y):
        super().__init__(value, order, showing=showing)
        self.r_i = r_i
        self.STARTING_X, self.STARTING_Y = self.get_coords(x, y)

    def get_difference(self):
        return (CARDW - (0 if self.showing else 0.5)) * (self.order - 1)


class CommunityCard(Card):
    def __init__(self, value, order, showing=True):
        super().__init__(value, order, showing)
        self.STARTING_X = screen.get_width() / 2 - 5 / 2 * CARDW - 2 * CARDB
        self.STARTING_Y = screen.get_height() / 2 - 1 / 2 * CARDH


def get_r_i(player, table):
    return (
        len(table.players) + player.table_position - table.human_player.table_position
    ) % len(table.players)


class PlayerGUI:
    def __init__(self, player, table) -> None:
        self.r_i = get_r_i(player, table)
        self.table = table
        self.x, self.y = player_coords[self.r_i]
        self.player = player
        self.showing = isinstance(self.player, Human)
        self.action_text = None
        self.extra = 0
        self.resize()
        self.CXB = PlayerGUI.get_CXB()

    def resize(self):
        self.x, self.y = player_coords[self.r_i]
        self.PX, self.PY = self.get_profile_pos(
            6 / 100 * table_image_size[0], PROFILE_SIZE[0]
        )

        DBUTTONW = 30 * MSCALE
        self.button_image = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/misc/Button.png").convert_alpha(),
            (DBUTTONW, DBUTTONW),
        )

        self.BX, self.BY = self.get_button_pos(PROFILE_SIZE[0], DBUTTONW)
        self.CX, self.CY = self.get_chip_pos(
            10 / 100 * table_image_size[0], CHIPW, CHIPH
        )

        self.set_cards()
        self.profile = pygame.transform.smoothscale(
            pygame.image.load(
                rf"{dirname}/images/profile_pictures/{self.player.profile_picture}.png"
            ).convert_alpha(),
            PROFILE_SIZE,
        )

        rect_image = pygame.Surface(self.profile.get_size(), pygame.SRCALPHA)
        size = rect_image.get_size()
        pygame.draw.rect(
            rect_image, (255, 255, 255), (0, 0, *size), border_radius=size[0] // 2
        )
        pygame.draw.rect(
            rect_image,
            BLACK,
            (0, 0, *size),
            border_radius=size[0] // 2,
            width=3,
        )

        self.profile.blit(rect_image, (0, 0), None, pygame.BLEND_RGBA_MIN)
        self.set_chip_images(self.table.blinds[-1], extra=self.extra)

    @staticmethod
    def get_CXB():
        l = [0]

        for _ in range(29):
            l.append(l[-1] + random.randint(-1, 1))

        return l

    @staticmethod
    def move_position(pos, x, y, distance, direction):
        """Moves a co-ordinate in a direction relative to the seat position 1: left, 2: right, 3:towards centre, 4: away"""

        i = int(bool(pos % 3))
        co = -1 if pos <= 3 else 1

        if direction in [1, 2]:
            i = int(not (i))
        elif not pos % 3:
            co *= -1

        if direction in [2, 4]:
            co *= -1

        coords = [x, y]
        coords[i] += distance * co

        return coords

    def get_button_pos(self, p_width, b_width):
        buffer = (13 / 100 if self.r_i != 5 else 12 / 100) * table_image_size[0]
        ws = 77 / 100 if self.r_i != 5 else 55 / 100
        x, y = self.move_position(
            self.r_i + 1, self.x, self.y, (1.3 if self.r_i in [2, 5] else 1) * buffer, 3
        )
        x, y = self.move_position(self.r_i + 1, x, y, ws * p_width, 1)
        return self.fix_pos(x, y, b_width)

    def get_chip_pos(self, buffer, width, height):
        x, y = self.move_position(self.r_i + 1, self.x, self.y, buffer, 3)
        if self.r_i in [2, 5]:
            y += height * 1.3
        return self.fix_pos(x, y, width, height)

    def get_profile_pos(self, buffer, p_width):
        x, y = self.move_position(self.r_i + 1, self.x, self.y, buffer, 4)
        return self.fix_pos(x, y, p_width)

    def fix_pos(self, x, y, width, height=None):
        """Fixes the co-ordinates of images because images are blitted with the top left being the given co-ordinate"""

        if height == None:
            height = width
        pos = self.r_i + 1
        if pos in [3, 4, 5]:
            x, y = self.move_position(pos, x, y, height, 4)

        x, y = self.move_position(pos, x, y, width / 2, 1 if pos <= 3 else 2)
        return x, y

    def set_cards(self):
        card_info = [
            self.player.hole_cards[0],
            1,
            self.r_i,
            self.showing,
            self.PX,
            self.PY,
        ]

        self.cards = []
        for r in range(2):  # TODO account for more than 2 cards?
            self.cards.append(HoleCard(*card_info))
            card_info[0] = self.player.hole_cards[1]
            card_info[1] += 1

    def get_action(self):
        # BUG when action is reset such as through button press
        # the new action is the last players action
        action = self.player.action

        if action == None:
            return None
        if action == 1:
            return "Fold"
        if action == 2:
            return "Call" if self.player.extra else "Check"
        else:
            word = (
                "All In"
                if self.player.chips == 0
                else "Bet" if self.table.bet_count < 2 else "Raise"
            )
            return f"{word} {self.table.last_bet}"

    def update(self, bb=None, extra=0):
        if bb == None:
            bb = self.table.blinds[-1]
        self.set_chip_images(bb, extra=extra)
        self.action_text = self.get_action()

    def set_chip_images(self, bb, extra=0):
        self.extra = extra
        chips = max(self.player.round_invested, extra)
        self.chip_images = self.get_chip_images(chips, bb)

    @staticmethod
    def get_chip_images(value, bb, extra=0):
        return [
            pygame.transform.smoothscale(
                pygame.image.load(
                    rf"{dirname}/images/chips/{c}_chip.png"
                ).convert_alpha(),
                (CHIPW, CHIPH),
            )
            for c in get_chips(bb, value + extra)
        ]

    def set_show(self, table):
        self.showing = not self.player.fold and (table.players_remaining > 1 and table.running == False or table.r >= table.skip_round or isinstance(self.player, Human))

        #This only works for main player because if self.showing == False the cards are never updated but this is probably bad
        if self.showing:
            self.show_cards()

    def show_cards(self):
        for c in self.cards:
            c.showing = self.showing

    @staticmethod
    def s_chip_pos(x, y, buffer, i):
        return x + buffer[i], y - ((i % 10) * 36 / 100 * CHIPH)

    @staticmethod
    def draw_chips(x, y, buffer, images, pos=1):

        # images[:10], images[10:20] = images[10:20], images[:10]
        # images = [chip] * 30 test
        p = -1
        if len(images) > 10:
            p = -2

        for i, c_image in enumerate(images):  # account for more than 30?
            if i % 10 == 0:
                p += 1

            cx, cy = PlayerGUI.move_position(
                pos,
                *PlayerGUI.s_chip_pos(x, y, buffer, i),
                ((CHIPW if pos not in [3, 6] else CHIPH) * 1.3 * p),
                2 if pos <= 3 else 1,
            )

            screen.blit(c_image, (cx, cy))

    def draw(self):
        # self.resize()

        screen.blit(self.profile, (self.PX, self.PY))

        text = fonts.main_font.render(str(self.player.chips), True, (255, 215, 0))
        text_rect = text.get_rect(
            center=(self.PX + PROFILE_SIZE[0] / 2, self.PY + 1 * PROFILE_SIZE[1])
        )
        screen.blit(text, (text_rect[0], self.PY + PROFILE_SIZE[1]))

        if self.player.inactive:
            return

        chips = self.chip_images[:30]

        PlayerGUI.draw_chips(
            self.CX,
            self.CY,
            self.CXB,
            chips,
            self.r_i + 1,
        )

        if self.player.fold == False:
            for c in self.cards:
                c.draw()

        if self.player.position_name == "Button":
            screen.blit(self.button_image, (self.BX, self.BY))

        if self.action_text:
            text = fonts.main_font.render(self.action_text, True, BLACK)
            text_rect = text.get_rect()
            screen.blit(
                text,
                (
                    self.PX + (PROFILE_SIZE[1] - text_rect.width) / 2,
                    self.PY - text_rect.height,
                ),
            )


class Window:
    def __init__(self, frame_rate, cw):
        self.frame_rate = frame_rate
        self.current_window = cw
        self.buttons = []

    def end_init(self):
        for b in self.buttons:
            b.add_window(self)

    def random(self):
        if pygame.time.get_ticks() % 200 == 0:
            random.random()

    def beg_frame(self):
        self.mouse = pygame.mouse.get_pos()

        for b in self.buttons:
            b.draw()

        # self.random()

    def resize(self):
        for b in self.buttons:
            b.resize()

    def mid_frame(self):
        global screen

        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    b.check_press(*self.mouse)

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

                init_images()
                self.resize()

    def set_current_window(self, w_change):
        self.current_window = w_change


class PlayWindow(Window):
    def __init__(self, frame_rate, cw):
        super().__init__(frame_rate, cw)
        size = screen.get_height() / 16
        self.back_button = Menu_Button(
            size / 4,
            size / 4,
            (99, 99, 99),
            "",
            0,
            size,
            size,
            pygame.image.load(
                rf"{dirname}/images/misc/Back_button.png"
            ).convert_alpha(),
            border=False,
            see=False,
            square=True,
        )

        self.buttons.extend([self.back_button])


class Menu(Window):
    def __init__(self, frame_rate, cw=0):
        super().__init__(frame_rate, cw)

        background = pygame.image.load(
            rf"{dirname}/images/misc/black_background1.jpg"
        ).convert_alpha()

        self.background = pygame.transform.smoothscale(
            background, (screen.get_width(), screen.get_height())
        )
        self.button_size = (screen.get_width() / 4, screen.get_height() / 8)
        self.play_button = Menu_Button(
            (screen.get_width() - self.button_size[0]) / 2,
            screen.get_height() / 4 - self.button_size[1] / 2,
            (99, 99, 99),
            "Play",
            1,
            *self.button_size,
            font_attr="large_font",
        )

        self.explorer = Menu_Button(
            (screen.get_width() - self.button_size[0]) / 2,
            screen.get_height() / 2 - self.button_size[1] / 2,
            (99, 99, 99),
            "Explorer",
            2,
            *self.button_size,
            font_attr="large_font",
        )

        self.trainer = Menu_Button(
            (screen.get_width() - self.button_size[0]) / 2,
            screen.get_height() * 3 / 4 - self.button_size[1] / 2,
            (99, 99, 99),
            "Trainer",
            3,
            *self.button_size,
            font_attr="large_font",
        )
        self.buttons.extend([self.play_button, self.explorer, self.trainer])

        super().end_init()

    def single_frame(self):
        global screen

        screen.blit(self.background, (0, 0))
        super().beg_frame()

        pygame.display.flip()

        end = super().mid_frame()
        if end == False:
            return False
        return True

    def random(self):
        random.random()


class PokerGame(PlayWindow):
    def __init__(self, frame_rate, cw) -> None:
        super().__init__(frame_rate, cw)
        self.table = start()
        self.community_cards = []

        self.deal_c = 75
        self.w_for_deal = False
        self.testing = False
        self.acted = False
        self.human_acted = False
        # self.current_window = 1

        self.dealButton = DealButton(
            screen.get_width() / 2 - (BUTTONW / 2),
            screen.get_height() / 6 - BUTTONH / 2,
            (169, 169, 169),
            "Deal",
        )
        self.foldButton = ActionButton(
            screen.get_width()
            - (BUTTONW + BUTTON_BUFFER_X) * 2
            - BUTTON_WDGE_BUFFER
            + BUTTON_BUFFER_X,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_HDGE_BUFFER,
            (255, 0, 0),
            "Fold",
            1,
        )
        self.checkButton = CheckButton(
            screen.get_width()
            - (BUTTONW + BUTTON_BUFFER_X) * 2
            - BUTTON_WDGE_BUFFER
            + BUTTON_BUFFER_X,
            screen.get_height() - (BUTTONH) * 1 - BUTTON_HDGE_BUFFER,
            (169, 169, 169),
            "Check",
            2,
        )
        self.betButton = BetButton(
            screen.get_width() - (BUTTONW) - BUTTON_WDGE_BUFFER,
            screen.get_height() - (BUTTONH) - BUTTON_HDGE_BUFFER,
            (34, 140, 34),
            "Bet",
            3,
        )

        zbw = screen.get_height() / 16
        self.zoom = Zoom(screen.get_width() - zbw * 5 / 4, zbw / 4, zbw)
        self.buttons.extend(
            [
                self.dealButton,
                self.foldButton,
                self.checkButton,
                self.betButton,
                self.zoom,
            ]
            + self.betButton.buttons
        )

        self.deal_tick = 0
        self.e_j = pygame.transform.scale(
            pygame.image.load(rf"{dirname}/images/misc/e-j.jpg").convert_alpha(),
            (screen.get_width(), screen.get_height()),
        )
        for b in self.buttons:
            b.add_table(self.table)

        super().end_init()
        self.count = 0

    def set_current_window(self, w_change):
        self.zoom.set_current(0)
        return super().set_current_window(w_change)

    def resize(self):
        for p in self.players:
            p.resize()

        self.set_community_cards()
        return super().resize()

    def set_test(self):
        self.deal_c = 0
        self.testing = True

    def start_hand(self):  # TODO
        self.players = sorted(
            [PlayerGUI(p, self.table) for p in self.table.players],
            key=lambda x: get_r_i(x.player, self.table),
        )

        self.r = 0
        self.chip_images = []
        self.community_cards = []
        self.pot = 0
        self.CXB = PlayerGUI.get_CXB()
        self.w_for_deal = False

    def draw_pot(self):
        x, y = screen.get_width() / 2, screen.get_height() / 2 - CARDH
        # self.chip_images = [chip] * 30 #testing
        PlayerGUI.draw_chips(x - CHIPW / 2, y - CARDH / 4, self.CXB, self.chip_images)
        text = fonts.main_font.render(str(self.pot), True, BLACK)
        text_rect = text.get_rect()
        screen.blit(text, (x - text_rect.width / 2, y))

    def set_community_cards(self):
        self.community_cards = [
            CommunityCard(c, i + 1) for i, c in enumerate(self.table.community)
        ]

    def reset_cards(self):
        for p in self.players:
            p.set_cards()

        self.set_community_cards()

    def single_frame(self):
        # global screen

        screen.fill((0, 119, 8))
        screen.blit(tableImage, (TableX, TableY))
        super().beg_frame()
        current_tick = pygame.time.get_ticks()
        skip = False

        if self.dealButton.pressed:

            for p in self.players:
                p.draw()

            for card in self.community_cards:
                card.draw()
            self.draw_pot()
            if self.r != self.table.r:
                self.r += 1

                self.set_community_cards()

                self.pot = self.table.get_pot()
                self.chip_images = PlayerGUI.get_chip_images(
                    self.table.get_pot(), self.table.blinds[-1]
                )

                for p in self.players:
                    p.update(self.table.blinds[-1])

                skip = True

                for p in self.players:
                    p.set_show(self.table)

        pygame.display.flip()

        if self.acted:
            if not self.testing:
                if self.table.human_player.fold == True:
                    pygame.time.wait(100)
                else:
                    pygame.time.wait(500)

            self.acted = False

        if skip:
            return True

        end = super().mid_frame()
        if end == False:
            return False

        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.dealButton.pressed_action()

                if event.key == pygame.K_q:  # TODO
                    print("q", self.table.blinds)

                    if self.table.blinds < sum(p.chips for p in self.players) / 10:
                        self.table.blinds = [n * 2 for n in self.table.blinds]

                    print(self.table.blinds)

                if event.key == pygame.K_j:
                    screen.blit(self.e_j, (0, 0))
                    pygame.display.flip()
                    pygame.time.wait(500)

                if event.key == pygame.K_t:
                    for p in self.table.players:
                        if p.chips:
                            p.chips = 0
                            break

        self.count += 1
        if pygame.mouse.get_pressed()[0]:
            self.betButton.slider.check_press(*self.mouse)

        if self.table.running:

            #TODO
            if not self.human_acted:
                self.checkButton.set_text()
                cont, self.end = self.table.start_move()

                r_i = get_r_i(self.table.current_player, self.table)
                if cont == True and isinstance(self.table.current_player, Bot):
                    self.acted = True
                    self.end = self.table.single_move(
                        action=(self.table.current_player.get_action(self.table))
                    )

                    self.players[r_i].update(self.table.blinds[-1])

                elif (
                    cont
                    and isinstance(self.table.current_player, Human)
                    and self.testing
                ):
                    self.end = self.table.single_move(action=(1, 0))

            if self.end:
                self.table.end_round()

        if not self.table.running and self.dealButton.pressed:

            if current_tick >= self.deal_tick:
                if self.w_for_deal:
                    self.dealButton.pressed_action()
                else:
                    self.w_for_deal = True
                    self.deal_tick = current_tick + self.frame_rate * self.deal_c * (
                        5 if not self.table.human_player.inactive else 0.2
                    )

        if self.human_acted == True:
            self.human_acted = False

        if self.dealButton.pressed == False:
            self.dealButton.pressed_action()

        return True and self.table.no_players != 1


class Explorer(PlayWindow):
    def __init__(self, frame_rate, cw):
        super().__init__(frame_rate, cw)

        self.buttons.extend([])
        self.resize()
        super().end_init()

    def resize(self):
        self.text = fonts.title_font.render("Coming Soon!", True, WHITE)
        self.text_rect = self.text.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 3)
        )
        self.back = fonts.large_font.render(
            "Click the top left button to exit", True, WHITE
        )
        self.back_rect = self.back.get_rect(
            center=(screen.get_width() / 2, screen.get_height() * 2 / 3)
        )
        return super().resize()

    def single_frame(self):
        screen.fill((0, 119, 8))
        super().beg_frame()

        screen.blit(self.text, self.text_rect)
        screen.blit(self.back, self.back_rect)
        pygame.display.flip()

        end = super().mid_frame()
        if end == False:
            return False

        return True


class Trainer(PlayWindow):
    def __init__(self, frame_rate, cw):
        super().__init__(frame_rate, cw)

        self.buttons.extend([])
        self.resize()
        super().end_init()

    def resize(self):
        self.text = fonts.title_font.render("Coming Soon!", True, WHITE)
        self.text_rect = self.text.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 3)
        )
        self.back = fonts.large_font.render(
            "Click the top left button to exit", True, WHITE
        )
        self.back_rect = self.back.get_rect(
            center=(screen.get_width() / 2, screen.get_height() * 2 / 3)
        )
        return super().resize()

    def single_frame(self):
        screen.fill((0, 119, 8))
        super().beg_frame()

        screen.blit(self.text, self.text_rect)
        screen.blit(self.back, self.back_rect)
        pygame.display.flip()

        end = super().mid_frame()
        if end == False:
            return False

        return True


async def main():
    running = True
    FRAME_RATE = 30
    window = Menu(FRAME_RATE)
    states = [Menu, PokerGame, Explorer, Trainer]
    while running:
        old_state = window.current_window
        running = window.single_frame()

        # if isinstance(window, PokerGame) and window.table.human_player.chips == 0:
        #     window.set_test()

        if old_state != window.current_window:
            window = states[window.current_window](FRAME_RATE, window.current_window)
        clock.tick(FRAME_RATE)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    # main()
    asyncio.run(main())
