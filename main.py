import pygame, random, os
import pygame.image
from backbone import start, Bot, Human
from chips import get_chips


# TODO show cards used with winning hands and winner (maybe show winning hand name), darken players who have folded
# BUG when changing bet action text changed ?
# TODO scale window, all in button, speed button
# BUG slider doesnt allow all in
# BUG action text glitch when player is choosing bet and opp has done a large bet (only when player on right?)
# TODO make LHS buttons and RHS buttons
# BUG cant go all in

pygame.init()


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


dirname = os.path.dirname(__file__)
SCREENSIZE = (1400, 900)
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)

# text_font = pygame.font.SysFont("Comic Sans", 35)
small_font = pygame.font.Font(rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 30)
main_font = pygame.font.Font(rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 35)
large_font = pygame.font.Font(rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 80)
title_font = pygame.font.Font(rf"{dirname}/misc/JqkasWild-w1YD6.ttf", 120)


BUTTONW = 150
BUTTONH = 50
BUTTON_EDGE_BUFFER = 2 / 5 * BUTTONW
BUTTON_BUFFER_X = 80
BUTTON_BUFFER_Y = 20

CS = 20
CHIPW, CHIPH = (2 * CS, 1 * CS)

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

pygame.display.set_caption("Poker Game")

clock = pygame.time.Clock()

tableImage = pygame.image.load(
    rf"{dirname}/images/misc/poker-table.png"
).convert_alpha()
TIS = 1
table_image_size = (868 * TIS, 423 * TIS)
tableImage = pygame.transform.smoothscale(tableImage, table_image_size)
TableX = (screen.get_width() / 2) - (table_image_size[0] / 2)
TableY = (screen.get_height() / 2) - (table_image_size[1] / 2)

CARD_S = 1
BUFFER_S = 1
CARDW, CARDH, CARDB = (
    59 / 1000 * table_image_size[0] * CARD_S,
    173 / 1000 * table_image_size[1] * CARD_S,
    7 / 1000 * table_image_size[1] * BUFFER_S,
)

chip = pygame.transform.smoothscale(
    pygame.image.load(rf"{dirname}/images/chips/green_chip.png").convert_alpha(),
    (CHIPW, CHIPH),
)

chip2 = pygame.transform.smoothscale(
    pygame.image.load(rf"{dirname}/images/chips/black_chip.png").convert_alpha(),
    (CHIPW, CHIPH),
)

TCard = pygame.transform.smoothscale(
    pygame.image.load(rf"{dirname}/images/cards/card_back.png").convert_alpha(),
    (CARDW, CARDH),
)

TCard2 = pygame.transform.rotate(TCard, 90)

PROFILE_SIZE = (125, 125)
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


class Button:
    def __init__(
        self, x, y, colour, text, BW=BUTTONW, BH=BUTTONH, image=None, border=True
    ):
        self.x = x
        self.y = y
        self.colour = colour
        self.text = text
        self.BW = BW
        self.BH = BH

        self.set_text_rect()

        if image == None:
            self.background = pygame.Surface((self.BW, self.BH))
            self.background.fill(colour)
        else:
            self.background = pygame.transform.smoothscale(image, (self.BW, self.BH))

        if border:
            pygame.draw.rect(self.background, BLACK, (0, 0, self.BW, self.BH), 3)

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
        BW=BUTTONW,
        BH=BUTTONH,
        image=None,
        border=True,
        see=True,
    ):
        super().__init__(x, y, colour, text, BW, BH, image, border)

        if see:
            self.background.set_alpha(128)
        self.w_change = w_change

    def pressed_action(self):
        self.window.current_window = self.w_change


class Zoom(Button):
    def __init__(self, x, y, width):

        self.x = x
        self.y = y
        self.current = 0

        self.BW = self.BH = width
        self.zoom_in = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/misc/zoom-in.png").convert_alpha(),
            (width, width),
        )

        self.zoom_out = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/misc/zoom-out.png").convert_alpha(),
            (width, width),
        )

    def draw(self):
        image = self.zoom_in if self.current < 2 else self.zoom_out
        screen.blit(image, (self.x, self.y))

    def pressed_action(self):
        global CARDW, CARDH, CARDB  # bad?

        CARDW = [1.5, 2 / 1.5, 1 / 2][self.current] * CARDW
        CARDH = [1.5, 2 / 1.5, 1 / 2][self.current] * CARDH
        CARDB = [0, 0, 7 / 1000 * table_image_size[1]][self.current]
        self.current = (self.current + 1) % 3

        self.window.reset_cards()


class DealButton(Button):
    pressed = False

    def __init__(
        self, x, y, colour, text, BW=BUTTONW, BH=BUTTONH, image=None, border=True
    ):
        super().__init__(x, y, colour, text, BW, BH, image, border)

        self.pressed = False

    def pressed_action(self):
        self.pressed = True

        if self.table.running == True:
            return

        self.table.start_hand()
        self.window.start_hand()


class ActionButton(Button):
    def __init__(self, x, y, colour, text, action, BW=BUTTONW, BH=BUTTONH, border=True):
        super().__init__(x, y, colour, text, BW, BH, border=border)
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

        self.text = main_font.render(
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

    def __init__(self, x, y, colour, text, action, s_buttons=None):
        super().__init__(x, y, colour, text, action)

        if s_buttons == None:
            s_buttons = [
                [(2.5, "bb"), (8, "bb"), (2.5, "p"), (-1, "all")],
                [(0.5, "p"), (1, "p"), (2, "p"), (-1, "all")],
            ]
        self.increase = CBetButton(
            x + self.BW,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_EDGE_BUFFER,
            (34, 140, 34),
            main_font.render("+", True, WHITE),
            1,
            self,
        )
        self.decrease = CBetButton(
            x - BUTTONW / 4,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_EDGE_BUFFER,
            (34, 140, 34),
            main_font.render("-", True, WHITE),
            -1,
            self,
        )
        self.slider = Slider(
            x,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_EDGE_BUFFER,
            (169, 169, 169),
            main_font.render("", True, WHITE),
            self,
        )

        self.set_buttons = []

        sb_count = len(s_buttons[0])
        e = 1.2
        TW = (self.increase.x - self.decrease.x + self.decrease.BW) * e
        # TW = (screen.get_width() - self.decrease.x) * e
        sb_buffer = TW / 30
        SW = (TW - sb_buffer * (sb_count - 1)) / sb_count

        for i in range(sb_count):
            self.set_buttons.append(
                SetBetButton(
                    # screen.get_width() - TW + (SW + sb_buffer) * i,
                    self.decrease.x - (TW - TW / e) / 2 + (SW + sb_buffer) * i,
                    self.decrease.y - BUTTONH - 5,
                    (14, 74, 146),
                    main_font.render("", True, WHITE),
                    self,
                    [x[i] for x in s_buttons],
                    BW=SW,
                )
            )

        self.buttons = [self.increase, self.decrease, self.slider] + self.set_buttons
        self.pbet = 0

    def draw(self):
        super().draw()
        text = main_font.render(str(self.pbet), True, BLACK)
        text_rect = text.get_rect(
            center=(self.x + self.BW / 2, self.slider.y - BUTTONW / 2)
        )
        screen.blit(text, text_rect)

    def add_table(self, table):
        super().add_table(table)


class CBetButton(Button):
    def __init__(self, x, y, colour, text, co, bet_button, border=True):
        super().__init__(x, y, colour, text, BW=BUTTONW / 4)
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
        BW=BUTTONW,
        BH=BUTTONH,
        image=None,
        border=True,
    ):
        super().__init__(x, y, colour, text, BW, BH, image, border)

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

        self.text = small_font.render(text, True, WHITE)
        self.set_text_rect()

    def draw(self):
        self.update_text()
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
        super().__init__(x, y, colour, text)
        self.l_colour = l_colour
        self.l_height = l_height
        self.bet_button = bet_button
        self.s_x = x
        self.SW = SW

    def draw(self):
        pygame.draw.rect(
            screen,
            self.l_colour,
            (self.x, self.y + (self.BH - self.l_height) / 2, self.BW, self.l_height),
        )
        pygame.draw.rect(screen, self.colour, (self.s_x, self.y, self.SW, self.BH))

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
        imagePath = rf"{dirname}/images/cards/{card_path}.png"

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

    def show(self):
        self.showing = True
        self.set_image()


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
        self.set_chip_images(table.blinds[-1])

        self.PX, self.PY = self.get_profile_pos(
            6 / 100 * table_image_size[0], PROFILE_SIZE[0]
        )

        DBUTTONW = 30
        self.button_image = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}/images/misc/Button.png").convert_alpha(),
            (DBUTTONW, DBUTTONW),
        )

        self.BX, self.BY = self.get_button_pos(PROFILE_SIZE[0], DBUTTONW)
        self.CX, self.CY = self.get_chip_pos(
            10 / 100 * table_image_size[0], CHIPW, CHIPH
        )
        self.CXB = PlayerGUI.get_CXB()

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

    def show_cards(self):
        for c in self.cards:
            c.show()

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

    def update(self, bb, extra=0):

        self.set_chip_images(bb, extra=extra)
        self.action_text = self.get_action()

    def set_chip_images(self, bb, extra=0):
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

    def showdown(self, table):
        self.showing = not self.player.fold and table.players_remaining > 1

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

        screen.blit(self.profile, (self.PX, self.PY))

        text = main_font.render(str(self.player.chips), True, (255, 215, 0))
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
            text = main_font.render(self.action_text, True, BLACK)
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

    def beg_frame(self):
        self.mouse = pygame.mouse.get_pos()
        for b in self.buttons:
            b.draw()

    def mid_frame(self):
        global screen

        for event in self.events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    b.check_press(*self.mouse)

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)


class PlayWindow(Window):
    def __init__(self, frame_rate, cw):
        super().__init__(frame_rate, cw)
        size = screen.get_height() / 16
        self.back_button = Menu_Button(
            size / 4,
            size / 4,
            (99, 99, 99),
            large_font.render("", True, WHITE),
            0,
            size,
            size,
            pygame.image.load(
                rf"{dirname}/images/misc/Back_button.png"
            ).convert_alpha(),
            border=False,
            see=False,
        )

        self.buttons.extend([self.back_button])


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
            main_font.render("Deal", True, WHITE),
        )
        self.foldButton = ActionButton(
            screen.get_width()
            - (BUTTONW + BUTTON_BUFFER_X) * 2
            - BUTTON_EDGE_BUFFER
            + BUTTON_BUFFER_X,
            screen.get_height() - (BUTTONH + BUTTON_BUFFER_Y) * 2 - BUTTON_EDGE_BUFFER,
            (255, 0, 0),
            main_font.render("Fold", True, WHITE),
            1,
        )
        self.checkButton = CheckButton(
            screen.get_width()
            - (BUTTONW + BUTTON_BUFFER_X) * 2
            - BUTTON_EDGE_BUFFER
            + BUTTON_BUFFER_X,
            screen.get_height() - (BUTTONH) * 1 - BUTTON_EDGE_BUFFER,
            (169, 169, 169),
            main_font.render("Check", True, WHITE),
            2,
        )
        self.betButton = BetButton(
            screen.get_width() - (BUTTONW) - BUTTON_EDGE_BUFFER,
            screen.get_height() - (BUTTONH) - BUTTON_EDGE_BUFFER,
            (34, 140, 34),
            main_font.render("Bet", True, WHITE),
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

    def set_test(self):
        self.deal_c = 0
        self.testing = True

    def start_hand(self):
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
        text = main_font.render(str(self.pot), True, BLACK)
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
        global screen

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

                if self.table.running == False:
                    for p in self.players:
                        p.showdown(self.table)

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

        self.events = pygame.event.get()

        end = super().mid_frame()
        if end == False:
            return False

        # print(pygame.event.get())
        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.dealButton.pressed_action()

                if event.key == pygame.K_q:  # TODO
                    print("q", self.table.blinds)
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
                        1 if not self.table.human_player.inactive else 0.2
                    )

        if self.human_acted == True:
            self.human_acted = False

        if self.dealButton.pressed == False:
            self.dealButton.pressed_action()

        return True and self.table.no_players != 1


class Menu(Window):
    def __init__(self, frame_rate, cw=0):
        super().__init__(frame_rate, cw)

        background = pygame.image.load(
            rf"{dirname}/images/misc/black_poker_background.jpg"
        ).convert_alpha()

        self.background = pygame.transform.smoothscale(
            background, (screen.get_width(), screen.get_height())
        )
        self.button_size = (screen.get_width() / 4, screen.get_height() / 8)
        self.play_button = Menu_Button(
            (screen.get_width() - self.button_size[0]) / 2,
            screen.get_height() / 4 - self.button_size[1] / 2,
            (99, 99, 99),
            large_font.render("Play", True, WHITE),
            1,
            *self.button_size,
        )

        self.explorer = Menu_Button(
            (screen.get_width() - self.button_size[0]) / 2,
            screen.get_height() / 2 - self.button_size[1] / 2,
            (99, 99, 99),
            large_font.render("Explorer", True, WHITE),
            2,
            *self.button_size,
        )
        self.buttons.extend([self.play_button, self.explorer])

        super().end_init()

    def single_frame(self):
        global screen

        screen.blit(self.background, (0, 0))
        super().beg_frame()

        pygame.display.flip()

        self.events = pygame.event.get()
        end = super().mid_frame()
        if end == False:
            return False
        return True


class Explorer(PlayWindow):
    def __init__(self, frame_rate, cw):
        super().__init__(frame_rate, cw)

        self.buttons.extend([])
        self.text = title_font.render("Coming Soon!", True, WHITE)
        self.text_rect = self.text.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 3)
        )
        super().end_init()

    def single_frame(self):
        screen.fill((0, 119, 8))
        super().beg_frame()

        screen.blit(self.text, self.text_rect)
        pygame.display.flip()

        self.events = pygame.event.get()

        end = super().mid_frame()
        if end == False:
            return False

        return True


def main():
    running = True
    FRAME_RATE = 30
    # window = Poker_game(FRAME_RATE)
    # window.set_test()
    window = Menu(FRAME_RATE)
    states = [Menu, PokerGame, Explorer]
    while running:
        old_state = window.current_window
        running = window.single_frame()

        if old_state != window.current_window:
            window = states[window.current_window](FRAME_RATE, window.current_window)
        clock.tick(FRAME_RATE)

    pygame.quit()


if __name__ == "__main__":
    main()
