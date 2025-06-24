import time
import pygame
pygame.init()

FPS = 60
WIDTH = 640
HEIGHT = 480
RED = (255, 0, 0)
GREEN = (0, 168, 82)
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


class RectDraw(pygame.sprite.Sprite):
    def init(self, color,wall = False, hideout = False):
        super().init()
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()
        self.color = color
    
    def update_surf(self, size, line=0):
        pygame.draw.rect(window, self.color, size, line)

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

health = 100
speed_player = 1
speed_recharge = 1

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

running = True

while running:
    window.fill((255, 255, 255))
    print_text('Здоровье', 30, 10)
    health_frame.draw_rect()
    show_rect(30, 40, health, 10, GREEN)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
               health -= 10
               last_damage_time = pygame.time.get_ticks()
               last_action_time = pygame.time.get_ticks()

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
        death.draw(200, 200)

    pygame.display.update()
    clock.tick(FPS)