import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("画像付きプレイヤーゲーム")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

# 画像読み込み・リサイズ
player_img = pygame.image.load("ex5/ex5/fig/0.png").convert_alpha()
default_img = pygame.transform.scale(player_img, (40, 40))

explosion_img = pygame.image.load("ex5/ex5/fig/bakuha.png").convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (500, 500))

player_pos = [150, 300]
player_radius = 20
player_vel = [0, 0]
dragging = False
launched = False

enemy_radius = 25
enemies = []
max_enemies = 5
enemy_spawn_timer = 0
enemy_spawn_delay = 90

FRICTION = 0.98
FONT = pygame.font.SysFont(None, 36)
score = 0

hamehameha_active = False
hame_timer = 0

explosions = pygame.sprite.Group()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.frame = 0

    def update(self):
        self.frame += 1
        if self.frame > 30:
            self.kill()

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def keep_player_in_screen():
    if player_pos[0] - player_radius < 0:
        player_pos[0] = player_radius
        player_vel[0] *= -1
    elif player_pos[0] + player_radius > WIDTH:
        player_pos[0] = WIDTH - player_radius
        player_vel[0] *= -1

    if player_pos[1] - player_radius < 0:
        player_pos[1] = player_radius
        player_vel[1] *= -1
    elif player_pos[1] + player_radius > HEIGHT:
        player_pos[1] = HEIGHT - player_radius
        player_vel[1] *= -1

def draw():
    screen.fill(WHITE)

    for e in enemies:
        pygame.draw.circle(screen, RED, e, enemy_radius)

    if dragging:
        pygame.draw.line(screen, GREEN, player_pos, pygame.mouse.get_pos(), 3)

    rect = default_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
    screen.blit(default_img, rect)

    score_surf = FONT.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surf, (20, 20))

    if hamehameha_active:
        text = FONT.render("Skill!", True, RED)
        screen.blit(text, (WIDTH // 2 - 60, HEIGHT // 2 - 30))

    explosions.draw(screen)
    explosions.update()
    pygame.display.flip()

running = True
while running:
    clock.tick(60)
    enemy_spawn_timer += 1

    if enemy_spawn_timer >= enemy_spawn_delay and len(enemies) < max_enemies:
        x = random.randint(WIDTH // 2, WIDTH - enemy_radius)
        y = random.randint(enemy_radius, HEIGHT - enemy_radius)
        enemies.append([x, y])
        enemy_spawn_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not dragging:
            mx, my = pygame.mouse.get_pos()
            if distance((mx, my), player_pos) <= player_radius:
                dragging = True

        if event.type == pygame.MOUSEBUTTONUP and dragging:
            mx, my = pygame.mouse.get_pos()
            dx = player_pos[0] - mx
            dy = player_pos[1] - my
            player_vel = [dx / 5, dy / 5]
            dragging = False
            launched = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not hamehameha_active:
                hamehameha_active = True
                hame_timer = 30
                # 中心に爆発（サイズ500）
                explosions.add(Explosion(player_pos[:], explosion_img))
                enemies.clear()
                score += 5  # 全滅ボーナス

    if hamehameha_active:
        hame_timer -= 1
        if hame_timer <= 0:
            hamehameha_active = False

    if launched:
        player_pos[0] += player_vel[0]
        player_pos[1] += player_vel[1]
        player_vel[0] *= FRICTION
        player_vel[1] *= FRICTION
        keep_player_in_screen()

        for e in enemies[:]:
            if distance(player_pos, e) <= player_radius + enemy_radius:
                enemies.remove(e)
                score += 1

        if math.hypot(player_vel[0], player_vel[1]) < 0.5:
            launched = False
            player_vel = [0, 0]

    draw()

pygame.quit()
