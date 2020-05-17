###############################################################################################
#Use this file to play the brick breaker game yourself, using the left and right arrow keys.
#This file has nothing to do with the AI, it is just the game environment used.
###############################################################################################
import pygame
import random

pygame.init()
w, h = 500, 500
win = pygame.display.set_mode((w, h))
pygame.display.set_caption("Brick Breaker")
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
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.vel
            self.currvel = -2
            if self.x < 0:
                self.x = 0
                self.currvel = 0
        if keys[pygame.K_RIGHT] and self.x < w - self.width:
            self.x += self.vel
            self.currvel = 2
            if self.x > w - self.width:
                self.x = w - self.width
                self.currvel = 0

class Brick:
    def __init__(self, x=0, y=0):
        self.width = 50
        self.height = 20
        self.x = x
        self.y = y
        self.currvel = 0  # only to avoid errors in collision detection
        self.breakable = True

class Ball:
    def __init__(self):
        self.radius = 8
        self.x = w // 2
        self.y = h - 150
        self.xvel = random.randrange(-5, 6, 2)
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


running = True
paddle = Paddle()
box_obs = [paddle]
brick_y = 80
def_brick_w = Brick().width
def_brick_h = Brick().height
for _ in range(5):
    brick_x = 0
    for _ in range((w//Brick().width)):
        box_obs.append(Brick(brick_x, brick_y))
        brick_x += def_brick_w
    brick_y += def_brick_h
ball = Ball()
dead_ball = 0
score, deaths = 0, 0
while running:
    clock.tick(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if dead_ball:
        pygame.time.delay(1000)
    if len(box_obs) == 1:
        win_label = win_font.render("YOU WIN!", 1, (255, 255, 255))
        win.blit(win_label, ((w - win_label.get_width()) // 2, 200))
        pygame.display.update()
        pygame.time.delay(1000)
        break
    paddle.currvel = 0
    keys = pygame.key.get_pressed()
    paddle.move(keys)
    dead_ball = ball.move(box_obs)
    if dead_ball:
        del ball
        box_obs.remove(paddle)
        del paddle
        pygame.time.delay(1000)
        paddle = Paddle()
        box_obs.insert(0, paddle)
        ball = Ball()
        deaths += 1

    win.fill((0, 0, 0))
    pygame.draw.rect(win, (255, 255, 255), (paddle.x, paddle.y, paddle.width, paddle.height))
    pygame.draw.circle(win, (255, 255, 255), (ball.x, ball.y), ball.radius)
    for brick in box_obs[1:]:
        pygame.draw.rect(win, (0, 0, 255), (brick.x+1, brick.y+1, brick.width-2, brick.height-2))
    score = 51 - len(box_obs)
    score_label = font.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))
    death_label = font.render("Deaths: " + str(deaths), 1, (255, 255, 255))
    win.blit(death_label, (w - death_label.get_width() - 10, 10))
    pygame.display.update()

pygame.quit()
