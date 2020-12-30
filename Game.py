import sys
import time
import random
import pygame

#Initializing pygame modules needed
pygame.font.init()
pygame.mixer.init()

#Setting up the window
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Meteor Burst')

#Setting up the fonts
FONT_ONE = pygame.font.SysFont('comicsans',100)
FONT_TWO = pygame.font.SysFont('Bahnschrift',30)
FONT_THREE = pygame.font.SysFont('Arial',30)

#------------------Setting up the images------------------#

#The background
BG = pygame.transform.scale(pygame.image.load('IMGS/background.png'), (WIDTH, HEIGHT))

#The meteors
M_ONE = pygame.transform.scale(pygame.image.load('IMGS/meteor1.png'), (70,50))
M_TWO = pygame.transform.scale(pygame.image.load('IMGS/meteor2.png'), (70,50))
M_THREE = pygame.transform.scale(pygame.image.load('IMGS/meteor3.png'), (70,50))

#The cursor image
CURSOR = pygame.transform.scale(pygame.image.load('IMGS/target.png'), (80,80))

#------------------Setting up the images------------------#

#The sound
LOSE_SOUND = pygame.mixer.Sound('lose.wav') 
CLICK_SOUND = pygame.mixer.Sound('click.wav')
LOSE_POINT_SOUND = pygame.mixer.Sound('lose_point.wav')

LOSE_SOUND = pygame.mixer.Sound('lose.wav') 
LOSE_SOUND.set_volume(50)

EXP_SOUND = pygame.mixer.Sound('Explosion.wav')
EXP_SOUND.set_volume(0.2)

MUSIC = pygame.mixer.music.load('bg_music.wav')
pygame.mixer.music.play(-1)

class Target:
    def __init__(self,x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def draw(self):
        '''
        Places the target on the screen
        '''
        WIN.blit(self.image, (self.x - 40, self.y - 40))

    def width(self):
        '''
        Returns the img width
        '''
        return self.image.get_width()

    def height(self):
        '''
        Returns the img height
        '''
        return self.image.get_height()

class Meteor:
    def __init__(self, x, y, image, angle):
        self.x = x
        self.y = y
        self.image = image
        self.angle = angle

    def draw(self):
        '''
        Places the meteor on the screen
        '''
        WIN.blit(pygame.transform.rotate(self.image, self.angle), (self.x, self.y))

    def move(self, vel):
        '''
        Moves the meteor
        '''
        self.y += vel

    def width(self):
        '''
        Returns the img width
        '''
        return self.image.get_width()

    def height(self):
        '''
        Returns the img height
        '''
        return self.image.get_height()

    def shot(self, pos):
        '''
        Checks if mouse position is in meteor
        '''
        if pos[0] > self.x and pos[0] < self.x + self.width():
                if pos[1] > self.y and pos[1] < self.y + self.height():
                    return True
        return False

class Gun:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        '''
        Places the gun on the screen
        '''
        pygame.draw.line(WIN, (0,255,0), (0,600), (self.x, self.y), 3)
        pygame.draw.line(WIN, (0,255,0), (800,600), (self.x, self.y), 3)
        pygame.draw.circle(WIN, (255,0,0), (self.x, self.y), 5)

class Explosion(pygame.sprite.Sprite):
    '''
    Animates the explosion
    '''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.frames = []
        for i in range(1,16):
            frame = pygame.transform.scale(pygame.image.load(f'IMGS/explosion{i}.png'), (150,150))
            self.frames.append(frame)

        self.index = 0  
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]
        self.counter = 0


    def update(self):
        '''
        Updates the explosion animation
        '''
        speed = 4
        self.counter += 1

        while self.counter >= speed and self.index < len(self.frames) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.frames[self.index]

        if self.index >= len(self.frames) - 1 and self.counter >= speed:
            self.kill()

def draw_window(level, meteor_list, lives, points):
    '''
    Draws the window
    '''
    level_label = FONT_THREE.render(f'Level: {level}',1,(100,0,255))
    lives_label = FONT_THREE.render(f'Lives: {lives}',1,(255,0,100))
    points_label = FONT_THREE.render('Points',1,(0,255,0))
    points_value = FONT_THREE.render(f'{points}',1,(0,255,0))

    for meteor in meteor_list:
        meteor.draw()

    WIN.blit(level_label, (10,10))
    WIN.blit(lives_label, (WIDTH/2 + 290 ,10))
    WIN.blit(points_label, (WIDTH/2 - points_label.get_width()/2, 10))
    WIN.blit(points_value, (WIDTH/2 - points_value.get_width()/2, 50))

def main():
    '''
    Runs the main logic of the game
    '''
    run = True
    clock = pygame.time.Clock()

    level = 0

    meteor_vel = 1
    meteor_list = []
    wave = 0
    wave_length = 0
    angle = 0

    lives = 3

    cursor = Target(300,300, CURSOR)

    explode_group = pygame.sprite.Group()
    gun = Gun(WIDTH/2, HEIGHT/2)

    points = 0

    def lose(points):
        class PlayButton:
            '''
            Creating the button class
            '''
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width 
                self.height = height
                self.color = (0,255,0)
                self.color_text = (0,0,255)

            def draw(self):
                '''
                Draws the button for us
                '''
                pygame.draw.rect(WIN, self.color_text, (self.x, self.y, self.width, self.height))
                click_label = FONT_TWO.render('Click here to main menu screen or quit the game',1,(255,0,0))

                WIN.blit(click_label, (WIDTH/2 - click_label.get_width()/2, self.y + 25))

            def isover(self, pos):
                '''
                Checks if cursor position is in button
                '''
                if pos[0] > self.x and pos[0] < self.x + self.width:
                    if pos[1] > self.y and pos[1] < self.y + self.height:
                        return True
                return False

        run = True

        button = PlayButton(WIDTH/2 - 345 ,400, 690, 100)
        points_label = FONT_TWO.render('Points',1,(255,0,0))
        points_value = FONT_TWO.render(f'{points}',1,(255,0,0))
        lost_label = FONT_ONE.render('You lost!',1,(255,0,0))

        while run:

            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button.isover(pos):
                        CLICK_SOUND.play()
                        main_menu()
                if event.type == pygame.MOUSEMOTION:
                    if button.isover(pos):
                        button.color = (0,0,255)
                        button.color_text = (0,255,0)
                    else:
                        button.color = (0,255,0)
                        button.color_text = (0,0,255)

            WIN.fill((0,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 100))
            WIN.blit(points_label, (WIDTH/2 - points_label.get_width()/2, 200))
            WIN.blit(points_value, (WIDTH/2 - points_value.get_width()/2, 250))
            button.draw()

            pygame.display.update()

    while run:

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                gun.x = pos[0]
                gun.y = pos[1]
                for meteor in meteor_list:
                    if meteor.shot(pos):
                        EXP_SOUND.play()
                        meteor_list.remove(meteor)
                        explode = Explosion(pos[0], pos[1])
                        explode_group.add(explode)
                        points += 1
            
            if cursor.y > 0 and cursor.y < HEIGHT and cursor.x > 0 and cursor.x < WIDTH:
                if pos[1] > 0 and pos[1] < HEIGHT and pos[0] > 0 and pos[0] < WIDTH:
                    cursor.x = pos[0]
                    cursor.y = pos[1] 

        if lives == 0:
            LOSE_SOUND.play()
            lose(points)

        if len(meteor_list) == 0:
            meteor_vel += 0.3
            wave += 1
            wave_length += 3
            level += 1

            for _ in range(wave_length):
                meteor = Meteor(random.randrange(10, WIDTH - 100), random.randrange(-1500, -100), random.choice([M_ONE, M_TWO, M_THREE]), angle)
                meteor_list.append(meteor)
            
        for meteor in meteor_list:
            meteor.move(meteor_vel)
            meteor.angle += random.randrange(1,10)

            if meteor.y + meteor.height() > HEIGHT:
                LOSE_POINT_SOUND.play()
                lives -= 1
                meteor_list.remove(meteor)

        clock.tick(100)
        WIN.blit(BG, (0,0))
        draw_window(level, meteor_list, lives, points)
        explode_group.draw(WIN)
        explode_group.update()
        gun.draw()
        cursor.draw()
        pygame.display.update()

def main_menu():
    '''
    Displays the main menu for us
    '''
    class PlayButton:
        '''
        Creating the button class
        '''
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width 
            self.height = height
            self.color = (255,0,0)
            self.color_text = (0,255,0)

        def draw(self):
            '''
            Draws the button for us
            '''
            pygame.draw.rect(WIN, self.color, (self.x, self.y, self.width, self.height))
            click_label = FONT_ONE.render('Play',1,self.color_text)

            WIN.blit(click_label, (WIDTH/2 - click_label.get_width()/2, self.y + 20))

        def isover(self, pos):
            '''
            Checks if cursor position is in button
            '''
            if pos[0] > self.x and pos[0] < self.x + self.width:
                if pos[1] > self.y and pos[1] < self.y + self.height:
                    return True
            return False

    run = True 

    title_label = FONT_ONE.render('Meteor Burst',1,(0,0,255))

    button = PlayButton(WIDTH/2 - 100, 350, 200, 110)

    while run:
        pygame.display.update()
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.isover(pos):
                    CLICK_SOUND.play()
                    main()
            if event.type == pygame.MOUSEMOTION:
                if button.isover(pos):
                    button.color = (0,255,0)
                    button.color_text = (255,0,0)
                else:
                    button.color = (255,0,0)
                    button.color_text = (0,255,0)

        WIN.blit(BG, (0,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 150))
        button.draw()

main_menu()
