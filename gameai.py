import pygame
import random
from neuroevolution import Neuvol

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
        self.y_velocity = screenh//300

    def isBlockOut(self):
        if self.rect.y > screenh//2 + screenh//3 + screenh//35:
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
        self.y_velocity = screenh//300

        '''For returning'''
        self.width = width
        self.height = height

    def isSlabOut(self):
        if self.rect.y > screenh//2 + screenh//3 + screenh//35:
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

    def returnSlab(self):
        return self.slabs

    def returnBlocks(self):
        return self.blocks

    def returnAll(self):
        return [self.slabs[0], self.slabs[1], self.blocks[0], self.blocks[1]]

    def returnInputs(self):
        return [self.slabs[0].rect.y/screenh, self.x/screenw, self.blocks[0].rect.y/screenh, self.blocks[0].rect.x/screenw, self.blocks[1].rect.y/screenh, self.blocks[1].rect.x/screenw]

    def isCreateNew(self):
        if self.slabs[0].rect.y >= screenh:
            return True
        return False

    def isSectionOut(self):
        if self.blocks[1].rect.y >= screenh:
            return True
        return False

class Game:
    def __init__(self, neuvol, population, maxscore, generation):
        self.maxscore = maxscore
        self.score = 0
        self.gen = []
        self.players = []
        self.sections = []
        self.slabs = []
        self.blocks = []
        self.block_list = pygame.sprite.Group()
        self.player_list = pygame.sprite.Group()
        self.numalive = 0
        self.generation = generation
        self.neuvol = neuvol
        self.population = population
        self.font = pygame.font.Font(None, 100)
        self.font2 = pygame.font.Font(None, 50)
        self.actualscore = 0

        '''Get Global Variables'''
        global screen
        global screenw
        global screenh


    def startGame(self):
        self.generation += 1
        #if self.generation > 50:
        #    return

        self.block_list.empty()
        self.player_list.empty()
        self.numalive = 0
        self.score = 0
        self.players = []
        self.sections = []

        '''Initialise Generation'''
        self.gen = self.neuvol.nextGeneration()

        '''Initialise Blocks and Slabs'''
        self.sections = [Section(screenh//2, screenw, screenh//2), Section(0, screenw, screenh//2)]

        for i in self.sections:
            for j in i.returnAll():
                self.block_list.add(j)
            self.slabs.append(i.returnSlab()[0])
            for j in i.returnBlocks():
                self.blocks.append(j)

        '''Initialise Players'''
        for i in range(self.population):
            self.players.append(Player(screenw//2, screenh//2 + screenh//3, screenh//35))
            self.numalive += 1
            self.player_list.add(self.players[i])

        '''Run Game'''
        return self.runGame()

    def runGame(self):
        while self.numalive != 0:
            #self.player.y_velocity += screenh//100 #GRAVITY
            pygame.event.get()

            for i in range(self.population):
                if self.players[i].alive == False:
                    continue
                self.players[i].x_velocity = 0
                inputs = [self.players[i].rect.x/screenw, self.slabs[0].width/screenw, self.blocks[0].rect.x/screenw, self.blocks[1].rect.x/screenw]
                outputs = self.gen[i].compute(inputs)
                if outputs[0] > 0.5:
                    self.players[i].x_velocity = screenw//125
                else:
                    self.players[i].x_velocity = -screenw//125

            self.player_list.update()

            for i in range(self.population):
                if self.players[i].alive == False:
                    continue

                if self.players[i].isPlayerOut():
                    self.players[i].alive = False

                blocks_hit = pygame.sprite.spritecollide(self.players[i], self.block_list, False)
                if len(blocks_hit) > 0:
                    self.players[i].alive = False

                if self.players[i].alive == False:
                    self.numalive -= 1
                    self.player_list.remove(self.players[i])
                    self.neuvol.networkScore(self.gen[i], self.score)

            '''Check if Slab/Block is out'''
            if self.blocks[0].isBlockOut():
                self.blocks = self.blocks[1:]

            if self.slabs[0].isSlabOut():
                self.slabs = self.slabs[1:]

            '''Check if Section is out'''
            if self.sections[0].isSectionOut():
                self.block_list.remove(i for i in self.sections[0].returnAll())
                self.sections = self.sections[1:]

            '''Check if new section needs to be created'''
            if len(self.sections) == 2 and self.sections[0].isCreateNew():
                self.actualscore += 1
                self.sections.append(Section(0, screenw, screenh//2))
                for i in self.sections[2].returnAll():
                    self.block_list.add(i)
                self.slabs.append(self.sections[2].returnSlab()[0])
                for j in self.sections[2].returnBlocks():
                    self.blocks.append(j)

            self.score += 1

            if self.actualscore > 5:
                pygame.time.Clock().tick(240)

            if self.actualscore > self.maxscore:
                self.maxscore = self.actualscore

            self.block_list.update()

            screen.fill(WHITE)
            screen.blit(self.font2.render("Generation: " + str(self.generation), True, BLACK, None), (0,0))
            screen.blit(self.font2.render("Max Score: " + str(self.maxscore), True, BLACK, None), (0,30))
            screen.blit(self.font2.render("Alive: " + str(self.numalive), True, BLACK, None), (0,60))
            screen.blit(self.font.render(str(self.actualscore), True, BLACK, None), (screenw//2 - self.font.size(str(self.actualscore))[0]//2,screenh//10))
            self.block_list.draw(screen)
            self.player_list.draw(screen)
            pygame.display.flip()

        return self.maxscore

def run(Neuvol, population):
    maxscore = 0
    score = 0
    generation = 0
    font = pygame.font.Font(None, 50)
    while 1:
        generation += 1
        game = Game(Neuvol, population, maxscore, generation)
        score = game.startGame()
        if score > maxscore:
            maxscore = score

pygame.init()
pygame.display.set_caption("Brick Jump")
screenw = 500
screenh = 900
screen = pygame.display.set_mode((screenw, screenh))
screen.fill(WHITE)

Neuvol = Neuvol()

run(Neuvol, 50)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
