import pygame
import math
import random
from pygame import transform, image
from random import randint
from time import time as timer
pygame.init()

FPS = 60
WIDTH = 640
HEIGHT = 480
RED = (255, 0, 0)
GREEN = (0, 168, 82)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
window = pygame.display.set_mode([WIDTH, HEIGHT])
clock = pygame.time.Clock()
background = transform.scale(image.load('image.png'), (640, 480))

# Initialize mouse position
mouse_x, mouse_y = 0, 0

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (50, 75))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.original_image = self.image.copy()
        self.angle = 0
        
    def reset(self):          
        window.blit(self.image, (self.rect.x, self.rect.y))
        
    def rotate_toward_mouse(self, mouse_pos):
        # Calculate angle between player and mouse
        dx = mouse_pos[0] - (self.rect.x + self.rect.width // 2)
        dy = mouse_pos[1] - (self.rect.y + self.rect.height // 2)
        self.angle = math.degrees(math.atan2(-dy, dx))
        
        # Rotate player image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=RED):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Add border to make walls more visible
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, width, height), 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (3, 3), 3)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.speed = 15
        
        # Calculate direction vector
        dx = target_x - start_x
        dy = target_y - start_y
        distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
        
        self.vx = dx / distance * self.speed
        self.vy = dy / distance * self.speed
        
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Remove bullets that go off-screen
        if (self.rect.right < 0 or self.rect.left > WIDTH or 
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class Area:
    def __init__(self, x: int, y: int, w: int, h: int, color: tuple):
        self.rect = pygame.Rect(x, y, w, h)
        self.fill_color = color

    def color(self, new_color):
        self.fill_color = new_color

    def draw_rect(self):
        pygame.draw.rect(window, self.fill_color, self.rect)

    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

class Label(Area):
    def set_text(self, text: str, font_size: int, text_color=(0, 0, 0)):
        font = pygame.font.SysFont('Verdana', font_size)
        self.image = font.render(text, True, text_color)

    def draw(self, shift_x=0, shift_y=0):
        self.draw_rect()
        window.blit(self.image,
                    (self.rect.x + shift_x, self.rect.y + shift_y))

def print_text(message: str, x: int, y: int, font_color = (0, 0, 0), font_type = 'Verdana', font_size = 20):
    font_type = pygame.font.SysFont(font_type, font_size)
    text = font_type.render(message, True, font_color)
    window.blit(text, (x, y))

def show_rect(x: int, y: int, w: int, h: int, color: tuple):
    pygame.draw.rect(window, color, pygame.Rect(x, y, w, h))

# Initialize game variables
health = 100
speed_player = 1
speed_recharge = 1
last_shot_time = 0
shot_delay = 300  # milliseconds between shots

damage_cooldown = 3000
regen_rate = 3
fast_regeneration_rate = 5
inactive_threshold = 6000
last_damage_time = pygame.time.get_ticks()
last_action_time = pygame.time.get_ticks()
regeneration_timer = 0
regeneration_interval = 1000
is_regenerating = False

health_frame = Area(30, 40, 100, 10, RED)
death = Label(0, 0, WIDTH, HEIGHT, RED)
death.set_text('Смерть', 48)

# Create player and walls
player = GameSprite('kilibik.png', 100, 350, 7.5)
wall1 = Wall(200, 200, 100, 150)  # x, y, width, height
wall2 = Wall(400, 100, 50, 300, BLUE)
wall3 = Wall(100, 50, 300, 40, GREEN)

# Create sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
walls = pygame.sprite.Group()
all_sprites.add(player)
walls.add(wall1, wall2, wall3)
all_sprites.add(wall1, wall2, wall3)  # Add walls to all_sprites for drawing

gameplay = True
running = True
lose = False

# Main game loop
while running:
    clock.tick(FPS)
    window.fill((255, 255, 255))
    print_text('Здоровье', 30, 10)
    health_frame.draw_rect()
    show_rect(30, 40, health, 10, GREEN)

    window.blit(background, (0, 0))
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                health -= 10
                last_damage_time = pygame.time.get_ticks()
                last_action_time = pygame.time.get_ticks()
        # Shooting with mouse button
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > shot_delay:
                    last_shot_time = current_time
                    # Create bullet from player center to mouse position
                    start_x = player.rect.x + player.rect.width // 2
                    start_y = player.rect.y + player.rect.height // 2
                    new_bullet = Bullet(start_x, start_y, mouse_pos[0], mouse_pos[1])
                    bullets.add(new_bullet)
                    all_sprites.add(new_bullet)

    current_time = pygame.time.get_ticks()
    if current_time - last_damage_time > damage_cooldown:
        if current_time - last_action_time > inactive_threshold:
            regeneration_rate = fast_regeneration_rate
        else:
            regeneration_rate = 1
        
        if health < 100:
            is_regenerating = True

        if is_regenerating:
            regeneration_timer += clock.get_time()
            
            if regeneration_timer >= regeneration_interval:
                health += regeneration_rate
                regeneration_timer -= regeneration_interval
    else:
        is_regenerating = False

    health = min(health, 100)

    if health < 10:
        speed_player * 1.5
        speed_recharge * 1.5
    if health <= 0:
        running = False 
        lose = True
    keys = pygame.key.get_pressed()
    if gameplay:
        original_x, original_y = player.rect.x, player.rect.y
        
        if keys[pygame.K_w]:
            player.rect.y -= player.speed
            last_action_time = current_time
        if keys[pygame.K_s]:
            player.rect.y += player.speed
            last_action_time = current_time
        if keys[pygame.K_a]:
            player.rect.x -= player.speed
            last_action_time = current_time
        if keys[pygame.K_d]:
            player.rect.x += player.speed
            last_action_time = current_time
        
        # Rotate player toward mouse cursor
        player.rotate_toward_mouse(mouse_pos)

        # Check player collision with walls
        if pygame.sprite.spritecollide(player, walls, False):
            player.rect.x, player.rect.y = original_x, original_y
    
    # Update bullets
    bullets.update()
    
    # Check bullet collisions with walls
    for bullet in bullets:
        wall_collision = pygame.sprite.spritecollide(bullet, walls, False)
        if wall_collision:
            bullet.kill()

    # Draw all sprites
    all_sprites.draw(window)
    
    pygame.display.flip()

while lose:
    death.draw(200, 200)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lose = False
    pygame.display.flip()   
    clock.tick(FPS)

pygame.quit()