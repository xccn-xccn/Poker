import pygame, threading
from main import start

pygame.init()

#TODO clean up code
#TODO show other players actions, show winning hand in GUI
#TODO create profile picture for players, show button / position


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


text_font = pygame.font.SysFont("Comic Sans", 35)


screen = pygame.display.set_mode([1200, 800])
SCREENSIZE = (1200, 800)

BUTTONW = 150
BUTTONH = 50
BUTTONBUFFER = 40

CARDW, CARDH, CARDB = 47, 71, 3.75
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

    def check_press(self, bx, by):
        if self.x <= bx <= self.x + BUTTONW and self.y <= by <= self.y + BUTTONH:
            print("Button Pressed")

            self.pressed_action()


class DealButton(Button):
    pressed = False

    def pressed_action(self):
        DealButton.pressed = True
        threading.Thread(target=self.table.hand).start()
        # self.table.hand()


class ActionButton(Button):
    def __init__(self, x, y, colour, text, action):
        super().__init__(x, y, colour, text)
        self.action = action

    def pressed_action(self):
        self.table.currentPlayer.paction = self.action


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
        if self.table.currentPlayer.action != 3:
            return super().pressed_action()
        else:
            print(self.pbet)
            self.table.currentPlayer.extra = BetButton.pbet  # TODO bad
            BetButton.pbet = 0  # bad

    def draw(self):
        super().draw()
        draw_text(
            str(BetButton.pbet),
            text_font,
            BLACK,
            self.x,
            self.y - (BUTTONH + BUTTONBUFFER) * 3,
        )


class CBetButton(Button):
    def __init__(self, x, y, colour, text, co):
        super().__init__(x, y, colour, text)
        self.co = co

    def pressed_action(self):
        if self.table.currentPlayer.action != 3:
            return

        BetButton.pbet += 40 * self.co  # bad

        print(BetButton.pbet)


class Card:
    def __init__(self, value, order):
        self.value = value
        self.order = order

        imagePath = rf"C:\Users\Geyong Min\Documents\programming\Poker\cards\{valFilename[self.value[0]]}_of_{suitFilename[value[1]]}.png"
        self.image = pygame.transform.scale(
            pygame.image.load(imagePath).convert_alpha(), (CARDW, CARDH)
        )

    def draw(self):
        screen.blit(
            self.image,
            (
                self.STARTINGX + (CARDW + CARDB) * (self.order - 1),
                self.STARTINGY,
            ),
        )


class HoleCard(Card):
    STARTINGX = SCREENSIZE[0] / 2 - CARDW / 2
    STARTINGY = 19 / 30 * SCREENSIZE[1] - 10


class CommunityCard(Card):
    STARTINGX = 474.5
    STARTINGY = 365.5
    CARDW, CARDH, CARDB = 47, 71, 3.75

    def __init__(self, value, order):
        super().__init__(value, order)


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
pygame.display.set_caption("pygame Test")

# clock is used to set a max fps
clock = pygame.time.Clock()

tableImage = pygame.image.load(
    r"C:\Users\Geyong Min\Documents\programming\Poker\PokerTable.png"
).convert_alpha()
TIS = 1.5
tableImageSize = (646 * TIS, 360 * TIS)
tableImage = pygame.transform.scale(tableImage, tableImageSize)


def main():
    running = True
    table1 = start()
    cards = []

    for b in buttons:
        b.add_table(table1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    b.check_press(*mouse)

        screen.fill((0, 119, 8))

        x = (SCREENSIZE[0] / 2) - (tableImageSize[0] / 2)
        y = (SCREENSIZE[1] / 2) - (tableImageSize[1] / 2)
        screen.blit(tableImage, (x, y))

        if table1.running:
            pygame.time.wait(100)  # TODO not great
            if len(cards) < len(table1.community) + len(
                table1.currentPlayer.holeCards
            ):  # worried current player holecards may be a bot - shouldnt be an issue though
                print("In card image making")
                for i, c in enumerate(table1.currentPlayer.holeCards):
                    if i + 1 > len(cards):
                        cards.append(HoleCard(c, i + 1))

                for i, c in enumerate(table1.community):
                    if i + 3 > len(cards):
                        cards.append(CommunityCard(c, i + 1))

            elif len(cards) > len(table1.community) + len(
                table1.currentPlayer.holeCards
            ):
                cards = []

        for CCard in cards:
            CCard.draw()

        for b in buttons:
            b.draw()

        mouse = pygame.mouse.get_pos()
        pygame.display.flip()

        # how many updates per second
        clock.tick(60)

    pygame.quit()

    # table1 = start()
    # running = True
    # sb_i = 5
    # while running:
    #     table1.hand(sb_i)
    #     sb_i = (sb_i - 1) % 6

    #     input("Click Enter for next hand: \n")


if __name__ == "__main__":
    main()
