import pygame, threading
from main import start
pygame.init()

def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))

text_font = pygame.font.SysFont("Comic Sans", 35)

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
    def pressed_action(self):
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
        self.increase = CBetButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 1, screen_size[1]- (BUTTONH + BUTTONBUFFER) * 2, (34, 140, 34), text_font.render("    +", False, WHITE), 1)
        self.decrease = CBetButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 2, screen_size[1]- (BUTTONH + BUTTONBUFFER) * 2, (34, 140, 34), text_font.render("    -", False, WHITE), -1)

    def pressed_action(self):
        if self.table.currentPlayer.action != 3:
            return super().pressed_action()
        else:
            print(self.pbet)
            self.table.currentPlayer.extra = BetButton.pbet #TODO bad
            BetButton.pbet = 0  #bad

    def draw(self):
        super().draw()
        draw_text(str(BetButton.pbet), text_font, BLACK, self.x, self.y - (BUTTONH + BUTTONBUFFER) * 3)

class CBetButton(Button):
    def __init__(self, x, y, colour, text, co):
        super().__init__(x, y, colour, text)
        self.co = co


    def pressed_action(self):
        if self.table.currentPlayer.action != 3:
            return

        BetButton.pbet += 40*self.co #bad

        print(BetButton.pbet)

        
screen = pygame.display.set_mode([1200, 800])
screen_size = (1280, 800)

BUTTONW = 150
BUTTONH = 50
BUTTONBUFFER = 40


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

dealButton =  DealButton(screen_size[0] / 2 - (BUTTONW / 2), screen_size[1] / 6 - BUTTONH / 2, (169, 169, 169), text_font.render("   Deal", False, WHITE))
foldButton = ActionButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 3, screen_size[1]- (BUTTONH + BUTTONBUFFER), (255, 0, 0), text_font.render("    Fold", False, WHITE), 1)
checkButton = ActionButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 2, screen_size[1]- (BUTTONH + BUTTONBUFFER), (169, 169, 169), text_font.render("  Check", False, WHITE), 2)
betButton = BetButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 1, screen_size[1]- (BUTTONH + BUTTONBUFFER), (34, 140, 34), text_font.render("    Bet ", False, WHITE), 3)

# decreaseButton = CBetButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 2, screen_size[1]- (BUTTONH + BUTTONBUFFER) * 2, (34, 140, 34), text_font.render("    -", False, WHITE), -1)
# increaseButton = CBetButton(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 1, screen_size[1]- (BUTTONH + BUTTONBUFFER) * 2, (34, 140, 34), text_font.render("    +", False, WHITE), 1)


buttons = [dealButton, foldButton, checkButton, betButton, betButton.increase, betButton.decrease]

# create a window
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("pygame Test")
 
# clock is used to set a max fps
clock = pygame.time.Clock()
 
# pygame.draw.aaline(test_surface, RED, (0, surface_size[1]), (surface_size[0], 0))
tableImage = pygame.image.load(r"C:\Users\Geyong Min\Documents\programming\Poker\PokerTable.png").convert_alpha()
TIS = 1.5
tableImage = pygame.transform.scale(tableImage, (640*TIS, 360*TIS))
tableImageSize = (646*TIS, 360*TIS)



def main():
    running = True
    table1 = start()

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
        
        # draw to the screen
        # YOUR CODE HERE
        x = (screen_size[0]/2) - (tableImageSize[0]/2)
        y = (screen_size[1]/2) - (tableImageSize[1]/2)
        screen.blit(tableImage, (x, y))
        
        for b in buttons:
            b.draw()
        # flip() updates the screen to make our changes visible

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