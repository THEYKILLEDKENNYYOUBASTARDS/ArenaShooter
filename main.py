import pygame
import math
import random
from pygame import transform, image

# Initialize pygame
pygame.init()

# Game constants
fps = 60
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
clock = pygame.time.Clock()

# Load images
try:
    bgs = transform.scale(image.load('bg.jpg'), (900, 800))
    banners = transform.scale(image.load('meter.png'), (100, 700))
    guns = transform.scale(image.load('aim.png'), (100, 100))
    target_images = [
        transform.scale(image.load('enemy.png'), (120, 80)),
        transform.scale(image.load('enemy.png'), (102, 68)),
        transform.scale(image.load('enemy.png'), (84, 56)),
        transform.scale(image.load('enemy.png'), (200, 150))  # Big boss enemy
    ]
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    exit()

# Game settings
targets = {
    1: [10, 5, 3],  # Level 1 target counts
    2: [12, 8, 5],  # Level 2 target counts
    3: [15, 12, 8, 3],  # Level 3 target counts
    4: [1]  # Level 4 - just the boss
}

level = 1
score = 0
font = pygame.font.SysFont('Arial', 30)

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.speed = 15
        self.radius = 5
        self.active = True
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Deactivate if out of screen
        if (self.x < 0 or self.x > WIDTH or 
            self.y < 0 or self.y > HEIGHT):
            self.active = False
            
    def draw(self):
        if self.active:
            lasers = [pygame.Color('red'), pygame.Color('purple'), 
                     pygame.Color('green'), pygame.Color('yellow')]
            pygame.draw.circle(screen, lasers[level-1], (int(self.x), int(self.y)), self.radius)

class Target:
    def __init__(self, x, y, size, speed, level):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.level = level
        self.active = True
        self.direction = random.choice([-1, 1])
        self.rect = pygame.Rect(x, y, size, size)
        
        # For boss enemy (level 4)
        if level == 4:
            self.health = 5  # Boss takes 5 hits to defeat
            self.max_health = 5
            self.size = 200  # Override size for boss
            self.rect = pygame.Rect(x, y, self.size, self.size)
    
    def update(self):
        if not self.active:
            return False
        
        # Move target - boss moves slower but in a zigzag pattern
        if self.level == 4:
            self.x += self.speed * self.direction * 0.7  # Slower movement
            self.y += math.sin(pygame.time.get_ticks() * 0.005) * 2  # Vertical wobble
        else:
            self.x += self.speed * self.direction
        
        # Reverse direction at screen edges
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.direction *= -1
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        return True
    
    def draw(self):
        if self.active:
            screen.blit(target_images[self.level - 1], (self.x, self.y))
            
            # Draw health bar for boss
            if self.level == 4:
                health_bar_width = 100
                health_ratio = self.health / self.max_health
                pygame.draw.rect(screen, (255, 0, 0), (self.x + 50, self.y - 20, health_bar_width, 10))
                pygame.draw.rect(screen, (0, 255, 0), (self.x + 50, self.y - 20, health_bar_width * health_ratio, 10))

def init_targets():
    all_targets = []
    
    if level == 1:
        my_list = targets[1]
        for i in range(3):
            for j in range(my_list[i]):
                size = 60 - i * 12
                speed = random.uniform(1.0, 2.0)
                x = WIDTH // (my_list[i] + 1) * (j + 1)
                y = 300 - (i * 150) + 30 * (j % 2)
                all_targets.append(Target(x, y, size, speed, level))
    
    elif level == 2:
        my_list = targets[2]
        for i in range(3):
            for j in range(my_list[i]):
                size = 50 - i * 10
                speed = random.uniform(1.5, 2.5)
                x = WIDTH // (my_list[i] + 1) * (j + 1)
                y = 300 - (i * 150) + 30 * (j % 2)
                all_targets.append(Target(x, y, size, speed, level))
    
    elif level == 3:
        my_list = targets[3]
        for i in range(4):
            for j in range(my_list[i]):
                size = 40 - i * 8
                speed = random.uniform(2.0, 3.0)
                x = WIDTH // (my_list[i] + 1) * (j + 1)
                y = 300 - (i * 100) + 30 * (j % 2)
                all_targets.append(Target(x, y, size, speed, level))
    
    elif level == 4:
        # Create the boss enemy
        x = WIDTH // 2 - 100  # Center the boss
        y = 200
        size = 200
        speed = 1.5  # Slower speed
        boss = Target(x, y, size, speed, level)
        all_targets.append(boss)
    
    return all_targets

all_targets = init_targets()
bullets = []
spawn_timer = 0
spawn_delay = 1000  # milliseconds
last_spawn_time = pygame.time.get_ticks()
last_shot_time = 0
shot_delay = 200  # milliseconds between shots

def draw_gun():
    mouse_pos = pygame.mouse.get_pos()
    gun_point = (WIDTH / 2, HEIGHT - 200)
    
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
    else:
        slope = -100000
    
    angle = math.atan(slope)
    rotation = math.degrees(angle)
    
    if mouse_pos[0] < WIDTH / 2:
        gun = pygame.transform.flip(guns, True, False)
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
    else:
        gun = guns
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))

def shoot():
    global last_shot_time
    current_time = pygame.time.get_ticks()
    
    if current_time - last_shot_time > shot_delay:
        last_shot_time = current_time
        mouse_pos = pygame.mouse.get_pos()
        gun_point = (WIDTH / 2, HEIGHT - 200)
        bullets.append(Bullet(gun_point[0], gun_point[1], mouse_pos[0], mouse_pos[1]))

def check_hits():
    global score, all_targets, bullets
    bullets_to_keep = []
    
    for bullet in bullets:
        if not bullet.active:
            continue
            
        bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, 
                                 bullet.radius * 2, bullet.radius * 2)
        hit = False
        
        for target in all_targets:
            if target.active and bullet_rect.colliderect(target.rect):
                if target.level == 4:  # Boss enemy
                    target.health -= 1
                    if target.health <= 0:
                        target.active = False
                        score += 100  # Big points for defeating boss
                else:
                    target.active = False
                    score += (4 - level) * 10  # More points for harder levels
                hit = True
                break
                
        if not hit:
            bullets_to_keep.append(bullet)
        else:
            bullet.active = False
            
    bullets = [b for b in bullets if b.active]

def spawn_targets():
    global all_targets, last_spawn_time
    current_time = pygame.time.get_ticks()
    
    if current_time - last_spawn_time > spawn_delay and len(all_targets) < sum(targets[level]):
        last_spawn_time = current_time
        all_targets = init_targets()  # Reinitialize all targets

run = True
while run:
    clock.tick(fps)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                level = 1
                all_targets = init_targets()
                bullets = []
            elif event.key == pygame.K_2:
                level = 2
                all_targets = init_targets()
                bullets = []
            elif event.key == pygame.K_3:
                level = 3
                all_targets = init_targets()
                bullets = []
            elif event.key == pygame.K_4:
                level = 4
                all_targets = init_targets()
                bullets = []
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                shoot()
    
    # Game logic
    spawn_targets()
    
    # Update targets
    active_targets = 0
    for target in all_targets:
        if target.update():
            active_targets += 1
    
    # Update bullets
    for bullet in bullets:
        bullet.update()
    bullets = [b for b in bullets if b.active]
    
    # Check for hits
    check_hits()
    
    # Check if level is complete (all targets destroyed)
    if active_targets == 0:
        if level < 4:
            level += 1
            all_targets = init_targets()
            bullets = []
        else:
            # Game completed - show victory message
            victory_text = font.render("YOU WIN! Final Score: " + str(score), True, (255, 255, 255))
            screen.blit(victory_text, (WIDTH//2 - 150, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            run = False
    
    # Drawing
    screen.blit(bgs, (0, 0))
    screen.blit(banners, (0, HEIGHT - 200))
    
    # Draw targets
    for target in all_targets:
        target.draw()
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw()
    
    # Draw gun
    if level > 0:
        draw_gun()
    
    # Draw score
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    # Draw level info
    level_text = font.render(f'Level: {level}', True, (255, 255, 255))
    screen.blit(level_text, (10, 50))
    
    pygame.display.flip()

pygame.quit()
