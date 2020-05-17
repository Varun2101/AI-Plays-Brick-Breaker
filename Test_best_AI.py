###############################################################################################
#Use this file to test the pickled NEAT models, or the models that you've trained and pickled
#To test your own models, change testing_best to True (optionally specify the file on line 139)
#To test specific cases of the random start, uncomment the xvel line in __init__ in class Ball
###############################################################################################
testing_best = False

import pygame
import random
import pickle

pygame.init()
w, h = 500, 500
win = pygame.display.set_mode((w, h))
pygame.display.set_caption("AI Plays Brick Breaker")
font = pygame.font.SysFont("comicsans", 30)
win_font = pygame.font.SysFont("comicsans", 50)
clock = pygame.time.Clock()

class Paddle:
    def __init__(self):
        self.width = 80
        self.height = 20
        self.x = (w - self.width) // 2
        self.y = h - 10 - self.height
        self.vel = 5
        self.currvel = 0  # for applying spin to ball
        self.breakable = False

    def move(self, keys):
        if keys['left'] and self.x > 0:
            self.x -= self.vel
            self.currvel = -2
            if self.x < 0:
                self.x = 0
                self.currvel = 0
        if keys['right'] and self.x < w - self.width:
            self.x += self.vel
            self.currvel = 2
            if self.x > w - self.width:
                self.x = w - self.width
                self.currvel = 0

class Brick:
    def __init__(self, x=0, y=0, boxIndex=0):
        self.width = 50
        self.height = 20
        self.x = x
        self.y = y
        self.currvel = 0  # only to avoid errors in collision detection
        self.breakable = True
        self.index = boxIndex

class Ball:
    def __init__(self):
        self.radius = 8
        self.x = w // 2
        self.y = h - 150
        self.xvel = random.randrange(-5, 6, 2)  # uncomment to allow randomness
        #self.xvel = 1  # uncomment to play the winning sequence
        self.yvel = -5
        self.softcap = 7

    def move(self, box_obs):
        self.x += self.xvel
        self.y += self.yvel
        # make sure you actually collide for a single frame before changing direction
        if self.x < self.radius:
            self.x = self.radius
            self.xvel = -self.xvel
        if self.x > w - self.radius:
            self.x = w - self.radius
            self.xvel = -self.xvel
        if self.y < self.radius:
            self.y = self.radius
            self.yvel = -self.yvel

        x_cooldown, y_cooldown = 0, 0  # to prevent multiple collisions in a single axis in a single frame
        for box in box_obs:
            if y_cooldown == 1 and x_cooldown == 1:
                break  # exits early to save computation
            #collision from above
            if y_cooldown == 0 and 0 < box.y - self.y <= self.radius and box.x - self.radius/2 <= self.x <= box.x + box.width + self.radius/2:
                self.y = box.y - self.radius
                self.yvel = -self.yvel
                self.xvel += box.currvel
                if self.xvel > 0 and self.xvel > self.softcap:
                    self.xvel = self.softcap
                elif self.xvel < 0 and self.xvel < -self.softcap:
                    self.xvel = -self.softcap
                y_cooldown = 1  # so that it doesn't register multiple collisions in the same frame
                if box.breakable:
                    box_obs.pop(box_obs.index(box))
            #collision from below - only for bricks, not paddle, so no currvel
            elif y_cooldown == 0 and 0 < self.y - box.y - box.height <= self.radius and box.x - self.radius/2 <= self.x <= box.x + box.width + self.radius/2:
                #self.x -= int((self.xvel/abs(self.xvel))*(self.xvel/self.yvel)*(self.radius - self.y + box.y + box.height))
                self.y = box.y + box.height + self.radius
                self.yvel = -self.yvel
                y_cooldown = 1
                if box.breakable:
                    box_obs.pop(box_obs.index(box))
            #collision from left - not adding currvel for same reason
            elif x_cooldown == 0 and 0 < box.x - self.x <= self.radius and box.y - self.radius <= self.y <= box.y + box.height + self.radius:
                self.x = box.x - self.radius
                self.xvel = -self.xvel
                x_cooldown = 1
                if box.breakable:
                    box_obs.pop(box_obs.index(box))
            #collision from right - same as above
            elif x_cooldown == 0 and 0 < self.x - box.x - box.width <= self.radius and box.y - self.radius <= self.y <= box.y + box.height + self.radius:
                self.x = box.x + box.width + self.radius
                self.xvel = -self.xvel
                x_cooldown = 1
                if box.breakable:
                    box_obs.pop(box_obs.index(box))

        if self.y > h - 5:  # kill ball
            return 1
        return 0

paddle = Paddle()
running = True
box_obs = [paddle]
brick_y = 80
def_brick_w = Brick().width
def_brick_h = Brick().height
boxIndex = 0
for _ in range(5):
    brick_x = 0
    for _ in range((w // Brick().width)):
        box_obs.append(Brick(brick_x, brick_y, boxIndex))
        boxIndex += 1
        brick_x += def_brick_w
    brick_y += def_brick_h
ball = Ball()
dead_ball = 0
start_ticks = pygame.time.get_ticks()  # to prevent infinite loop, break after 200 seconds
if testing_best:
    neural_net = pickle.load(open("best.pickle", "rb"))
# uses the best model for each default value of xvel, else uses best.pickle if xvel has been set to new value
elif ball.xvel in [-5, -3, 1]:
    neural_net = pickle.load(open("brick_breaker_51.3.pickle", "rb"))
elif ball.xvel in [-1, 5]:
    neural_net = pickle.load(open("brick_breaker_49.2.pickle", "rb"))
elif ball.xvel == 3:
    neural_net = pickle.load(open("brick_breaker_44.pickle", "rb"))
else:
    neural_net = pickle.load(open("best.pickle", "rb"))
while running:
    clock.tick(100)  # sets 100fps
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            quit()
            break
    paddle.currvel = 0
    keys = {'left': False, 'right': False}
    # input for NEAT will be the following + 1 or 0 for each brick that's unbroken/broken in order.
    inputList = [paddle.x, paddle.y, ball.x, ball.y, ball.xvel, ball.yvel]
    brokenList = [0] * boxIndex
    for box in box_obs[1:]:
        brokenList[box.index] = 1
    inputList.extend(brokenList)
    output = neural_net.activate(tuple(inputList))
    if output[0] > 0.5:
        keys['left'] = True
    if output[1] > 0.5:
        keys['right'] = True
    paddle.move(keys)
    dead_ball = ball.move(box_obs)
    score = 51 - len(box_obs)

    if dead_ball:
        running = False

    win.fill((0, 0, 0))
    pygame.draw.rect(win, (255, 255, 255), (paddle.x, paddle.y, paddle.width, paddle.height))
    pygame.draw.circle(win, (255, 255, 255), (ball.x, ball.y), ball.radius)
    for brick in box_obs[1:]:
        pygame.draw.rect(win, (0, 0, 255), (brick.x + 1, brick.y + 1, brick.width - 2, brick.height - 2))
    score_label = font.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))
    if len(box_obs) == 1:
        win_label = win_font.render("YOU WIN!", 1, (255, 255, 255))
        win.blit(win_label, ((w - win_label.get_width())//2, 200))
        pygame.display.update()
        pygame.time.delay(1000)
        break
    pygame.display.update()

    if (pygame.time.get_ticks() - start_ticks)/1000 > 200:
        running = False
        print("Infinite loop occurred")
        break
