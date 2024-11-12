import pygame, random, os
from main import start, Bot, Human
from chips import get_chips

pygame.init()

# TODO Reset chips after each round
# TODO clean up code (168) EVERTHING IS SO MESSY
# BUG double clicking bet breaks


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


dirname = os.path.dirname(__file__)
SCREENSIZE = (1400, 900)
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)

text_font = pygame.font.SysFont("Comic Sans", 35)
text_font = pygame.font.Font(rf"{dirname}\misc\JqkasWild-w1YD6.ttf", 35)
BUTTONW = 150
BUTTONH = 50
BUTTONBUFFER = 40

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

tableImage = pygame.image.load(rf"{dirname}\images\misc\PokerTable.png").convert_alpha()
TIS = 1
table_image_size = (868 * TIS, 423 * TIS)
tableImage = pygame.transform.smoothscale(tableImage, table_image_size)
TableX = (screen.get_width() / 2) - (table_image_size[0] / 2)
TableY = (screen.get_height() / 2) - (table_image_size[1] / 2)

CARDW, CARDH, CARDB = (
    59 / 1000 * table_image_size[0],
    173 / 1000 * table_image_size[1],
    7 / 1000 * table_image_size[1],
)
TCard = pygame.transform.smoothscale(
    pygame.image.load(rf"{dirname}\images\cards\card_back.png").convert_alpha(),
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
    def __init__(self, x, y, colour, text):
        self.x = x
        self.y = y
        self.colour = colour
        self.text = text
        self.BW = BUTTONW
        self.BH = BUTTONH

    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.BW, self.BH))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.BW, self.BH), 3)
        text_rect = self.text.get_rect(
            center=(self.x + self.BW / 2, self.y + self.BH / 2)
        )
        screen.blit(self.text, text_rect)

    def add_table(self, table):
        self.table = table

    def add_window(self, window):
        self.window = window

    def check_press(self, bx, by):
        if self.x <= bx <= self.x + self.BW and self.y <= by <= self.y + self.BH:
            self.pressed_action()

    def set_text(self):
        self.text = text_font.render(
            (
                "Check"
                if self.table.human_player.roundInvested == self.table.bets[-1]
                else "Call"
            ),
            True,
            WHITE,
        )


class DealButton(Button):
    pressed = False

    def pressed_action(self):
        DealButton.pressed = True
        self.table.start_hand()
        self.window.set_players()


class ActionButton(Button):
    def __init__(self, x, y, colour, text, action):
        super().__init__(x, y, colour, text)
        self.action = action

    def pressed_action(self):
        if isinstance(self.table.currentPlayer, Bot):
            return
        self.table.single_move(action=(self.action, 0))
        self.window.players[0].update(self.table.blinds[-1])


class BetButton(ActionButton):

    def __init__(self, x, y, colour, text, action):
        super().__init__(x, y, colour, text, action)
        self.increase = CBetButton(
            x + self.BW - screen.get_width() / 40,  # TODO Bad
            screen.get_height() - (BUTTONH + BUTTONBUFFER) * 2,
            (34, 140, 34),
            text_font.render("+", True, WHITE),
            1,
            self
        )
        self.decrease = CBetButton(
            x,
            screen.get_height() - (BUTTONH + BUTTONBUFFER) * 2,
            (34, 140, 34),
            text_font.render("-", True, WHITE),
            -1,
            self
        )
        self.pbet = 0

    def pressed_action(self):
        self.table.single_move(action=(3, self.pbet))
        self.pbet = 0
        self.window.players[0].update(self.table.blinds[-1])  # TODO Change?

    def draw(self):
        super().draw()
        draw_text(
            str(self.pbet),
            text_font,
            BLACK,
            self.x,
            self.y - (BUTTONH + BUTTONBUFFER) * 2,
        )


class CBetButton(Button):
    def __init__(self, x, y, colour, text, co, bet_button):
        super().__init__(x, y, colour, text)
        self.co = co
        self.BW = BUTTONW / 4
        self.bet_button = bet_button

    def pressed_action(self):  # TODO improve

        self.bet_button.pbet += self.table.blinds[-1] * self.co  # bad
        self.window.players[0].update(self.table.blinds[-1], extra = self.bet_button.pbet)


class Card:

    def __init__(self, value, order, showing=True):
        self.value = value
        self.order = order
        self.showing = showing
        self.set_image()

    def set_image(self):
        card_path = f"{valFilename[self.value[0]]}_of_{suitFilename[self.value[1]]}"
        imagePath = rf"{dirname}\images\cards\{card_path}.png"

        self.image = pygame.transform.smoothscale(
            pygame.image.load(imagePath).convert_alpha(), (CARDW, CARDH)
        )

        self.card_back = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}\images\cards\card_back.png").convert_alpha(),
            (CARDW, CARDH),
        )

        # self.card_back = pygame.transform.smoothscale(
        #     pygame.image.load(rf"{dirname}\images\cards\layered_cardback.png").convert_alpha(),
        #     (CARDW/3, CARDH/3),
        # )

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
    STARTING_X = screen.get_width() / 2 - 5 / 2 * CARDW - 2 * CARDB
    STARTING_Y = screen.get_height() / 2 - 1 / 2 * CARDH


def get_r_i(player, table):
    return (len(table.players) + player.position - table.human_player.position) % len(
        table.players
    )


class PlayerGUI:
    def __init__(self, player, table) -> None:
        self.r_i = get_r_i(player, table)
        self.x, self.y = player_coords[self.r_i]
        self.player = player
        self.showing = isinstance(self.player, Human)
        self.action = None
        self.acted = True
        self.set_chip_images(table.blinds[-1])

        self.PX, self.PY = self.get_profile_pos(
            6 / 100 * table_image_size[0], PROFILE_SIZE[0]
        )

        DBUTTONW = 30
        self.button_image = pygame.transform.smoothscale(
            pygame.image.load(rf"{dirname}\images\misc\Button.png").convert_alpha(),
            (DBUTTONW, DBUTTONW),
        )

        self.BX, self.BY = self.get_button_pos(PROFILE_SIZE[0], DBUTTONW)
        self.CX, self.CY = self.get_chip_pos(
            10 / 100 * table_image_size[0], CHIPW, CHIPH
        )
        self.CXB = [0]
        for _ in range(30):
            self.CXB.append(self.CXB[-1] + random.randint(-1, 1))

        self.add_cards()
        self.profile = pygame.transform.smoothscale(
            pygame.image.load(
                rf"{dirname}\images\profile_pictures\{self.player.profile_picture}.png"
            ).convert_alpha(),
            PROFILE_SIZE,
        )

    def move_position(self, x, y, distance, direction):
        """Moves a co-ordinate in a direction relative to the seat position 1: left, 2: right, 3:towards centre, 4: away"""

        pos = self.r_i + 1

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
        ws = 74 / 100 if self.r_i != 5 else 55 / 100
        x, y = self.move_position(
            self.x, self.y, (1.3 if self.r_i in [2, 5] else 1) * buffer, 3
        )
        x, y = self.move_position(x, y, ws * p_width, 1)
        return self.fix_pos(x, y, b_width)

    def get_chip_pos(self, buffer, width, height):
        x, y = self.move_position(self.x, self.y, buffer, 3)
        # if self.r_i not in [2, 5]:
        #     x -= width * 1.2
        return self.fix_pos(x, y, width, height)

    def get_profile_pos(self, buffer, p_width):
        x, y = self.move_position(self.x, self.y, buffer, 4)
        return self.fix_pos(x, y, p_width)

    def fix_pos(self, x, y, width, height=None):
        """Fixes the co-ordinates of images because images are blitted with the top left being the given co-ordinate"""

        if height == None:
            height = width
        pos = self.r_i + 1
        if pos in [3, 4, 5]:
            x, y = self.move_position(x, y, height, 4)

        x, y = self.move_position(x, y, width / 2, 1 if pos <= 3 else 2)
        return x, y

    def add_cards(self):
        card_info = [
            self.player.holeCards[0],
            1,
            self.r_i,
            self.showing,
            self.PX,
            self.PY,
        ]

        self.cards = []
        for r in range(2):
            self.cards.append(HoleCard(*card_info))
            card_info[0] = self.player.holeCards[1]
            card_info[1] += 1

    def show_cards(self):
        for c in self.cards:
            c.show()

    def update(self, bb, extra=0):
        self.action = self.player.actionText

        self.set_chip_images(bb, extra=extra)

    def set_chip_images(self, bb, extra=0):
        self.chip_images = [
            pygame.transform.smoothscale(
                pygame.image.load(
                    rf"{dirname}\images\chips\{c}_chip.png"
                ).convert_alpha(),
                (CHIPW, CHIPH),
            )
            for c in get_chips(bb, self.player.roundInvested + extra)
        ]

    def showdown(self, table):
        self.showing = (
            self.showing or not self.player.fold
        ) and table.players_remaining > 1

        for c in self.cards:
            c.showing = self.showing

    def draw(self):

        screen.blit(self.profile, (self.PX, self.PY))

        text = text_font.render(str(self.player.chips), True, (255, 215, 0))
        text_rect = text.get_rect(
            center=(self.PX + PROFILE_SIZE[0] / 2, self.PY + 1 * PROFILE_SIZE[1])
        )


        for i, c_image in enumerate(self.chip_images[:30]):
            p = i // 10
            p = -1 if p == 1 else 1 if p == 2 else 0

            screen.blit(
                c_image,
                self.move_position(
                    self.CX + self.CXB[i],
                    self.CY - i % 10 * 36 / 100 * CHIPH,
                    ((CHIPW if self.r_i not in [2, 5] else CHIPH) * 1.3 * (i // 10)),
                    2 if self.r_i <= 2 else 1,
                ),
            )

        screen.blit(text, (text_rect[0], self.PY + PROFILE_SIZE[1]))

        if self.player.positionName == "Button":
            screen.blit(self.button_image, (self.BX, self.BY))
        if self.action:
            draw_text(
                self.action,
                text_font,
                BLACK,
                *self.move_position(self.PX, self.PY, PROFILE_SIZE[0] / 2, 4),
            )

        if self.player.fold == False:
            for c in self.cards:
                c.draw()


class Main:
    def __init__(self) -> None:
        self.running = True
        self.table = start()
        self.community_cards = []

        self.dealButton = DealButton(
            screen.get_width() / 2 - (BUTTONW / 2),
            screen.get_height() / 6 - BUTTONH / 2,
            (169, 169, 169),
            text_font.render("Deal", True, WHITE),
        )
        self.foldButton = ActionButton(
            screen.get_width() - (BUTTONW + BUTTONBUFFER) * 2,
            screen.get_height() - (BUTTONH + BUTTONBUFFER) * 2,
            (255, 0, 0),
            text_font.render("Fold", True, WHITE),
            1,
        )
        self.checkButton = ActionButton(
            screen.get_width() - (BUTTONW + BUTTONBUFFER) * 2,
            screen.get_height() - (BUTTONH + BUTTONBUFFER),
            (169, 169, 169),
            text_font.render("Check", True, WHITE),
            2,
        )
        self.betButton = BetButton(
            screen.get_width() - (BUTTONW + BUTTONBUFFER) * 1,
            screen.get_height() - (BUTTONH + BUTTONBUFFER),
            (34, 140, 34),
            text_font.render("Bet ", True, WHITE),
            3,
        )

        self.buttons = [
            self.dealButton,
            self.foldButton,
            self.checkButton,
            self.betButton,
            self.betButton.increase,
            self.betButton.decrease,
        ]

        for b in self.buttons:
            b.add_table(self.table)
            b.add_window(self)

    def set_players(self):
        self.players = sorted(
            [PlayerGUI(p, self.table) for p in self.table.players],
            key=lambda x: get_r_i(x.player, self.table),
        )

    def single_frame(self):
        global screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    b.check_press(*self.mouse)
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pass

        screen.fill((0, 119, 8))
        screen.blit(tableImage, (TableX, TableY))

        if self.table.running:

            cont = self.table.start_move()

            r_i = get_r_i(self.table.currentPlayer, self.table)
            acted = False
            if cont and isinstance(self.table.currentPlayer, Bot):
                acted = True
                self.table.single_move(
                    action=(self.table.currentPlayer.get_action(self.table))
                )

                self.checkButton.set_text()

                self.players[r_i].update(self.table.blinds[-1]) #reset chips at the end of each round

            if acted:
                if self.table.human_player.fold == True:
                    pygame.time.wait(100)
                else:
                    pygame.time.wait(500)

            if len(self.community_cards) < len(self.table.community):
                for i, c in enumerate(self.table.community):
                    if i + 1 > len(self.community_cards):
                        self.community_cards.append(CommunityCard(c, i + 1))

            elif len(self.community_cards) > len(self.table.community):
                self.community_cards = []

        if self.dealButton.pressed:

            for p in self.players:
                p.draw()

            if self.table.running == False:
                for p in self.players:
                    p.showdown(self.table)

        for CCard in self.community_cards:
            CCard.draw()

        for b in self.buttons:
            b.draw()

        self.mouse = pygame.mouse.get_pos()
        # pygame.draw.rect(
        #     screen, (255, 0, 0), (screen.get_width() / 2, screen.get_height() / 2, 4, 4)
        # )

        pygame.display.flip()

        return True


def main():
    running = True

    window = Main()
    while running:
        running = window.single_frame()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
