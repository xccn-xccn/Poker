import pygame, threading
from main import start, Bot, Human

pygame.init()

# TODO Fix bets, show cards correctly
# TODO show hole cards by starting on current
# TODO clean up code
# TODO show other players actions, show winning hand in GUI
# TODO create profile picture for players, show button / position
# BUG cards randomly change to winners hand after showdown (only sometimes)


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


text_font = pygame.font.SysFont("Comic Sans", 35)


screen = pygame.display.set_mode([1200, 800])
SCREENSIZE = (1200, 800)

BUTTONW = 150
BUTTONH = 50
BUTTONBUFFER = 40

CARDW, CARDH, CARDB = 48, 71, 3.6
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

pygame.display.set_caption("pygame Test")

# clock is used to set a max fps
clock = pygame.time.Clock()

tableImage = pygame.image.load(
    r"C:\Users\Geyong Min\Documents\programming\Poker\PokerTable.png"
).convert_alpha()
TIS = 1.5
tableImageSize = (646 * TIS, 360 * TIS)
tableImage = pygame.transform.smoothscale(tableImage, tableImageSize)
TableX = (SCREENSIZE[0] / 2) - (tableImageSize[0] / 2)
TableY = (SCREENSIZE[1] / 2) - (tableImageSize[1] / 2)
TCard = pygame.transform.smoothscale(
    pygame.image.load(
        r"C:\Users\Geyong Min\Documents\programming\Poker\cards\card_back.png"
    ).convert_alpha(),
    (CARDW, CARDH),
)
TCard2 = pygame.transform.rotate(TCard, 90)

PROFILE_SIZE = (100, 100)


class Button:
    def __init__(self, x, y, colour, text):
        self.x = x
        self.y = y
        self.colour = colour
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, BUTTONW, BUTTONH))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, BUTTONW, BUTTONH), 3)

        screen.blit(self.text, (self.x, self.y))

    def add_table(self, table):
        self.table = table

    def add_window(self, window):
        self.window = window

    def check_press(self, bx, by):
        if self.x <= bx <= self.x + BUTTONW and self.y <= by <= self.y + BUTTONH:
            print("Button Pressed")

            self.pressed_action()


class DealButton(Button):
    pressed = False

    def pressed_action(self):
        DealButton.pressed = True
        self.table.start_hand()
        self.window.set_players()
        # TODO reset cards


class ActionButton(Button):
    def __init__(self, x, y, colour, text, action):
        super().__init__(x, y, colour, text)
        self.action = action

    def pressed_action(self):
        if isinstance(self.table.currentPlayer, Bot):
            return
        self.table.single_move(action=(self.action, 0))
        self.window.players[0].update()


class BetButton(ActionButton):
    pbet = 0

    def __init__(self, x, y, colour, text, action):
        super().__init__(x, y, colour, text, action)
        self.increase = CBetButton(
            SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 1,
            SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER) * 2,
            (34, 140, 34),
            text_font.render("    +", False, WHITE),
            1,
        )
        self.decrease = CBetButton(
            SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 2,
            SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER) * 2,
            (34, 140, 34),
            text_font.render("    -", False, WHITE),
            -1,
        )

    def pressed_action(self):
        self.table.single_move(action=(3, BetButton.pbet))
        BetButton.pbet = 0
        self.window.players[0].update()  # TODO Change?

    def draw(self):
        super().draw()
        draw_text(
            str(BetButton.pbet),
            text_font,
            BLACK,
            self.x,
            self.y - (BUTTONH + BUTTONBUFFER) * 2,
        )


class CBetButton(Button):
    def __init__(self, x, y, colour, text, co):
        super().__init__(x, y, colour, text)
        self.co = co

    def pressed_action(self):

        BetButton.pbet += 40 * self.co  # bad


class Card:

    def __init__(self, value, order, showing=True, rotate=False):
        self.value = value
        self.order = order
        self.showing = showing
        self.rotate = rotate
        self.set_image()

    def set_image(self):
        card_path = (
            "card_back"
            if self.value == None
            else f"{valFilename[self.value[0]]}_of_{suitFilename[self.value[1]]}"
        )
        imagePath = (
            rf"C:\Users\Geyong Min\Documents\programming\Poker\cards\{card_path}.png"
        )

        self.image = pygame.transform.smoothscale(
            pygame.image.load(imagePath).convert_alpha(), (CARDW, CARDH)
        )

        self.card_back = pygame.transform.smoothscale(
        pygame.image.load(
            r"C:\Users\Geyong Min\Documents\programming\Poker\cards\card_back.png"
        ).convert_alpha(),
        (CARDW, CARDH),
    )

        if self.rotate:
            self.image = pygame.transform.rotate(self.image, 90)
            self.card_back = pygame.transform.rotate(self.card_back, 90)

    def draw(self):
        difference = (CARDW + CARDB) * (self.order - 1)

        image = self.image if self.showing else self.card_back
        
        if not self.rotate:
            screen.blit(
                image,
                (
                    self.STARTING_X + difference,
                    self.STARTING_Y,
                ),
            )
        else:
            screen.blit(
                image,
                (
                    self.STARTING_X,
                    self.STARTING_Y + difference,
                ),
            )


class HoleCard(Card):
    STARTINGX = SCREENSIZE[0] / 2 - CARDW / 2
    STARTINGY = 19 / 30 * SCREENSIZE[1] - 10

    def get_coords(self, x, y):
        return [
            (x - CARDW - CARDB / 2, y - CARDH),
            (x - CARDW - CARDB / 2, y - CARDH),
            (x, y - CARDW - CARDB / 2),
            (x - CARDW - CARDB / 2, y),
            (x - CARDW - CARDB / 2, y),
            (X4 - B2 - CARDH, Y3 - CARDW - CARDB / 2),
        ][self.r_i]

    def __init__(self, value, order, r_i, showing, rotate=False):
        super().__init__(value, order, showing=showing, rotate=rotate)
        x, y = player_coords[r_i]
        self.r_i = r_i
        self.STARTING_X, self.STARTING_Y = self.get_coords(x, y)
        

    def show(self):
        self.showing = True
        self.set_image()


class CommunityCard(Card):
    STARTING_X = 473
    STARTING_Y = 365.5


X1 = 645 / 1000 * SCREENSIZE[0]
Y1 = TableY + tableImageSize[1]
B1 = 125 / 1000 * SCREENSIZE[1]

X2 = SCREENSIZE[0] - X1
Y2 = SCREENSIZE[1] - Y1

X3 = TableX
Y3 = SCREENSIZE[1] / 2
B2 = 89 / 1000 * SCREENSIZE[0]

X4 = SCREENSIZE[0] - X3

player_coords = [
    (X1, Y1 - B1),
    (X2, Y1 - B1),
    (X3 + B2, Y3),
    (X2, Y2 + B1),
    (X1, Y2 + B1),
    (X4 - B2, Y3),
]


dealButton = DealButton(
    SCREENSIZE[0] / 2 - (BUTTONW / 2),
    SCREENSIZE[1] / 6 - BUTTONH / 2,
    (169, 169, 169),
    text_font.render("   Deal", False, WHITE),
)
foldButton = ActionButton(
    SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 3,
    SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER),
    (255, 0, 0),
    text_font.render("    Fold", False, WHITE),
    1,
)
checkButton = ActionButton(
    SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 2,
    SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER),
    (169, 169, 169),
    text_font.render("  Check", False, WHITE),
    2,
)
betButton = BetButton(
    SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 1,
    SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER),
    (34, 140, 34),
    text_font.render("    Bet ", False, WHITE),
    3,
)


buttons = [
    dealButton,
    foldButton,
    checkButton,
    betButton,
    betButton.increase,
    betButton.decrease,
]

# create a window
screen = pygame.display.set_mode(SCREENSIZE)


def get_r_i(player, table):
    return (len(table.players) + player.position - table.human_player.position) % len(
        table.players
    )


class PlayerGUI:
    def __init__(self, player, table, profile="nature") -> None:
        self.r_i = get_r_i(player, table)
        self.x, self.y = player_coords[self.r_i]
        self.rotate = False
        self.player = player
        self.showing = isinstance(self.player, Human)
        self.action = None
        self.acted = True
        if self.r_i in [2, 5]:
            self.rotate = True

        self.add_cards()
        self.profile = pygame.transform.smoothscale(
            pygame.image.load(
                rf"C:\Users\Geyong Min\Documents\programming\Poker\profile_pictures\{profile}.png"
            ).convert_alpha(),
            PROFILE_SIZE,
        )

    def direction(
        self, x, y, distance, ix=0, iy=0
    ):  # TODO account if profile is not square
        return [
            (x - ix / 2, y + distance),
            (x - ix / 2, y + distance),
            (x - distance - ix, y - iy / 2),
            (x - ix / 2, y - distance - iy),
            (x - ix / 2, y - distance - iy),
            (x + distance, y - iy / 2),
        ][self.r_i]

    def add_cards(self):
        self.cards = (
            HoleCard(
                self.player.holeCards[0],
                1,
                self.r_i,
                self.showing,
                self.rotate,
            ),
            HoleCard(
                self.player.holeCards[1],
                2,
                self.r_i,
                self.showing,
                self.rotate,

            ),
        )

    def show_cards(self):
        for c in self.cards:
            c.show()

    def update(self):
        self.action = self.player.actionText

    def showdown(self, table):
        self.showing = (self.showing or not self.player.fold) and table.players_remaining > 1

        for c in self.cards:
            c.showing = self.showing

    def draw(self):
        if self.player.fold == False:
            for c in self.cards:
                c.draw()

        PX, PY = self.direction(
            self.x, self.y, 56 / 1000 * SCREENSIZE[1], *PROFILE_SIZE
        )
        screen.blit(self.profile, (PX, PY))

        draw_text(
            str(self.player.chips),
            text_font,
            (255, 215, 0),
            PX,
            PY + 3 / 4 * PROFILE_SIZE[1],
        )

        if self.action:
            draw_text(
                self.action,
                text_font,
                BLACK,
                *self.direction(PX, PY, PROFILE_SIZE[1]),
            )


class Main:
    def __init__(self) -> None:
        self.running = True
        self.table = start()
        self.community_cards = []

        self.dealButton = DealButton(
            SCREENSIZE[0] / 2 - (BUTTONW / 2),
            SCREENSIZE[1] / 6 - BUTTONH / 2,
            (169, 169, 169),
            text_font.render("   Deal", False, WHITE),
        )
        self.foldButton = ActionButton(
            SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 3,
            SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER),
            (255, 0, 0),
            text_font.render("    Fold", False, WHITE),
            1,
        )
        self.checkButton = ActionButton(
            SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 2,
            SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER),
            (169, 169, 169),
            text_font.render("  Check", False, WHITE),
            2,
        )
        self.betButton = BetButton(
            SCREENSIZE[0] - (BUTTONW + BUTTONBUFFER) * 1,
            SCREENSIZE[1] - (BUTTONH + BUTTONBUFFER),
            (34, 140, 34),
            text_font.render("    Bet ", False, WHITE),
            3,
        )

        self.buttons = [
            dealButton,
            foldButton,
            checkButton,
            betButton,
            betButton.increase,
            betButton.decrease,
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    b.check_press(*self.mouse)

        screen.fill((0, 119, 8))
        screen.blit(tableImage, (TableX, TableY))

        if self.table.running:

            cont = self.table.start_move()

            r_i = get_r_i(self.table.currentPlayer, self.table)
            if cont and isinstance(self.table.currentPlayer, Bot):
                self.table.single_move(
                    action=(self.table.currentPlayer.get_action(self.table.roundTotal))
                )

                self.players[r_i].update()

                if self.table.human_player.fold == True:
                    pygame.time.wait(100)
                else:
                    pygame.time.wait(500)

            if len(self.community_cards) < len(self.table.community):
                print("In card image making")

                for i, c in enumerate(self.table.community):
                    if i + 1 > len(self.community_cards):
                        self.community_cards.append(CommunityCard(c, i + 1))

            elif len(self.community_cards) > len(self.table.community):
                self.community_cards = []

        if self.buttons[0].pressed:

            for p in self.players:
                p.draw()

            if self.table.running == False:
                for p in self.players:
                    p.showdown(self.table)

        for CCard in self.community_cards:
            CCard.draw()

        for b in buttons:
            b.draw()

        self.mouse = pygame.mouse.get_pos()
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
