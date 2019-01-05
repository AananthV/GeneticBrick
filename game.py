import pygame
import random

#DEFINE COlORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER = (255, 0, 0)

class Player(pygame.sprite.Sprite):
    '''Represents the player'''
    def __init__(self, x, y, side):
        '''Pass the xy co-ordinates and the side-length'''
        super().__init__()  #Call Base Class Constructor

        self.alive = True

        '''Construct the player and fill color'''
        self.image = pygame.Surface((side, side))
        self.image.fill(PLAYER)
        self.image.set_colorkey(WHITE)

        '''Fetch the Rectangle encompassing our player'''
        self.rect = self.image.get_rect()

        '''Set X and Y Positions'''
        self.rect.x = x
        self.rect.y = y

        '''Set X and Y Velocities'''
        self.x_velocity = 0
        self.y_velocity = 0

        '''Set Accelerations'''
        self.gravity = side

    def update(self):
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity

    def isPlayerOut(self):
        if self.alive == False:
            return False
        if self.rect.y > screenh:
            return True
        if self.rect.x < 0:
            return True
        if self.rect.x > screenw:
            return True
        return False

class Block(pygame.sprite.Sprite):
    '''Represents the sectional blocks'''
    def __init__(self, x, y, side):
        '''Pass the xy coordinate and size'''
        super().__init__()  #Call base class Constructor

        '''Construct the player and fill color'''
        self.image = pygame.Surface((side, side))
        self.image.fill(BLACK)
        self.image.set_colorkey(WHITE)

        '''Fetch the Rectangle encompassing our player'''
        self.rect = self.image.get_rect()

        '''Set X and Y Positions'''
        self.rect.x = x
        self.rect.y = y

        '''Set X and Y Velocities'''
        #self.y_velocity = screenh//200
        self.y_velocity = 20

    def isBlockOut(self):
        if self.rect.y > screenh:
            return True
        return False

    def update(self):
        self.rect.y += self.y_velocity

class Slab(pygame.sprite.Sprite):
    '''Represents the sectional blocks'''
    def __init__(self, x, y, width, height):
        '''Pass the xy coordinate and size'''
        super().__init__()  #Call base class Constructor

        '''Construct the player and fill color'''
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.image.set_colorkey(WHITE)

        '''Fetch the Rectangle encompassing our player'''
        self.rect = self.image.get_rect()

        '''Set X and Y Positions'''
        self.rect.x = x
        self.rect.y = y

        '''Set X and Y Velocities'''
        #self.y_velocity = screenh//200
        self.y_velocity = 20

    def isSlabOut(self):
        if self.rect.y > screenh:
            return True
        return False

    def update(self):
        self.rect.y += self.y_velocity

class Section:
    '''Contains one Slab and two Blocks'''
    def __init__(self, y, width, height):
        self.x = random.randrange(width*0.66)
        self.slabs = [Slab(0, y, self.x, height//12), Slab(self.x+width//3, y, width*0.66 - self.x, height//12)]
        self.blocks = [Block(self.x + random.randrange(width//2) - width//8, y - height//3, height//15), Block(self.x + random.randrange(width//2) - width//8, y - 3*height//4, height//15)]


    def returnAll(self):
        return [self.slabs[0], self.slabs[1], self.blocks[0], self.blocks[1]]

    def isCreateNew(self):
        if self.slabs[0].rect.y >= screenh:
            return True
        return False

    def isSectionOut(self):
        if self.blocks[1].rect.y > screenh:
            return True
        return False

class Game:
    def __init__(self):
        self.maxscore = 0
        self.score = 0
        self.gen = []
        self.player = 0
        self.sections = []
        self.block_list = pygame.sprite.Group()
        self.numalive = 0
        self.generation = 0

        '''Get Global Variables'''
        global screen
        global screenw
        global screenh
        global population

        self.startGame()


    def startGame(self):
        self.generation += 1
        self.block_list = pygame.sprite.Group()
        self.score = 0
        '''Initialise Generation'''

        '''Initialise Blocks and Slabs'''
        self.sections = [Section(screenh//2, screenw, screenh//2), Section(0, screenw, screenh//2)]

        for i in self.sections:
            for j in i.returnAll():
                self.block_list.add(j)

        '''Initialise Players'''
        self.player = Player(screenw//2, screenh//2 + screenh//3, screenh//40)

        '''Run Game'''
        self.runGame()

    def runGame(self):
        while self.player.alive:
            #self.player.y_velocity += screenh//100 #GRAVITY
            pygame.event.get()
            self.player.x_velocity = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                #self.player.x_velocity = screenw//100
                self.player.x_velocity = 10
            #elif keys[pygame.K_a]:
            else:
                #self.player.x_velocity = -screenw//100
                self.player.x_velocity = -10

            '''Update Positions'''
            self.player.update()

            '''Check if player died'''

            if self.player.isPlayerOut():
                self.player.alive = False

            blocks_hit = pygame.sprite.spritecollide(self.player, self.block_list, False)
            if len(blocks_hit) > 0:
                self.player.alive = False

            '''Check if new section needs to be created'''
            if len(self.sections) == 2 and self.sections[0].isCreateNew():
                self.score += 1
                self.sections.append(Section(0, screenw, screenh//2))
                for i in self.sections[2].returnAll():
                    self.block_list.add(i)

            '''Check if Section is out'''
            if self.sections[0].isSectionOut():
                self.block_list.remove(i for i in self.sections[0].returnAll())
                self.sections = self.sections[1:]

            self.block_list.update()

            screen.fill(WHITE)
            self.block_list.draw(screen)
            screen.blit(self.player.image, self.player.rect)

            pygame.time.Clock().tick(120)
            pygame.display.flip()

        if self.score > self.maxscore:
            self.maxscore = self.score

        print(self.score)

        if(self.generation < 50):
            self.startGame()

pygame.init()
pygame.display.set_caption("Brick Jump")
screenw = 500
screenh = 900
screen = pygame.display.set_mode((screenw, screenh))
screen.fill(WHITE)


game = Game()
game.startGame()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
