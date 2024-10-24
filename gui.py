import pygame
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

    def check_press(self, bx, by):
        if self.x <= bx <= self.x + BUTTONW and self.y <= by <= self.y + BUTTONH:
            print("Button Pressed")

screen = pygame.display.set_mode([1200, 800])
screen_size = (1280, 800)

BUTTONW = 150
BUTTONH = 50
BUTTONBUFFER = 40


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
 
FoldButton = Button(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 3, screen_size[1]- (BUTTONH + BUTTONBUFFER), (255, 0, 0), text_font.render("    Fold", False, WHITE))
CheckButton = Button(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 2, screen_size[1]- (BUTTONH + BUTTONBUFFER), (169, 169, 169), text_font.render("  Check", False, WHITE))
BetButton = Button(screen_size[0]- (BUTTONW + BUTTONBUFFER) * 1, screen_size[1]- (BUTTONH + BUTTONBUFFER), (34, 140, 34), text_font.render("    Bet ", False, WHITE))

buttons = [FoldButton, CheckButton, BetButton]

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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
     
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                b.check_press(*mouse)
    #clear the screen
    screen.fill((0, 119, 8))
     
    # draw to the screen
    # YOUR CODE HERE
    x = (screen_size[0]/2) - (tableImageSize[0]/2)
    y = (screen_size[1]/2) - (tableImageSize[1]/2)
    # screen.blit(test_surface, (x, y))
    screen.blit(tableImage, (x, y))
    
    for b in buttons:
        b.draw()
    # flip() updates the screen to make our changes visible

    mouse = pygame.mouse.get_pos() 
    pygame.display.flip()
     
    # how many updates per second
    clock.tick(60)
 
pygame.quit()