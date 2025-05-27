import pygame
import math
import random
import time

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("画像付きプレイヤーゲーム")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont(None, 36)
FONT_JP = pygame.font.SysFont("meiryo", 80)
FONT_JP_SMALL = pygame.font.SysFont("meiryo", 40)

# 画像読み込み・リサイズ
player_img = pygame.image.load("ex5/fig/0.png").convert_alpha()  # 画像パスは環境に合わせて
default_img = pygame.transform.scale(player_img, (40, 40))
crying_img = pygame.image.load("ex5/fig/8.png").convert_alpha()
crying_img = pygame.transform.scale(crying_img, (40, 40))
bg_img = pygame.image.load("ex5/fig/222_bg.jpg").convert_alpha()

# プレイヤー
player_pos = [150, 300]
player_radius = 20
player_vel = [0, 0]
dragging = False
launched = False

# 敵（赤玉）
enemy_radius = 25
enemies = []
max_enemies = 5
enemy_spawn_timer = 0
enemy_spawn_delay = 90

FRICTION = 0.98
FONT = pygame.font.SysFont(None, 36)

score = 0  # スコア変数追加

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
    screen.blit(bg_img ,(0,0))

    # 敵を描画
    for e in enemies:
        pygame.draw.circle(screen, RED, e, enemy_radius)

    # 引っ張り線
    if dragging:
        pygame.draw.line(screen, GREEN, player_pos, pygame.mouse.get_pos(), 3)
    if score >= 10:
        show_game_over()
        running = False

    # プレイヤー画像を描画
    rect = default_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
    screen.blit(default_img, rect)

    # スコア表示
    score_surf = FONT.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surf, (20, 20))

    score_text = f"Score: {score}"
    score_surf = FONT.render(score_text, True, BLACK)
    score_rect = score_surf.get_rect(topleft=(20, 20))

    bg_rect = score_rect.inflate(10, 10)
    pygame.draw.rect(screen, WHITE, bg_rect)

    screen.blit(score_surf,score_rect)

    pygame.display.flip()


def show_game_over():
    blackout = pygame.Surface((WIDTH, HEIGHT))
    blackout.fill((0, 0, 0))
    blackout.set_alpha(180)
    screen.blit(blackout, (0, 0))

    text_surface = FONT_JP.render("ゲームオーバー", True, (255, 0, 0))  
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)

    pygame.display.update()
    time.sleep(5)


def show_start_screen():
    screen.fill(BLACK)

    title_surface = FONT_JP.render("ゲームスタート", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(title_surface, title_rect)

    start_surface = FONT_JP_SMALL.render("クリックしてスタート", True, WHITE)
    start_rect = start_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(start_surface, start_rect)

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

# まず開始画面を表示
show_start_screen()

running = True
while running:
    clock.tick(60)
    enemy_spawn_timer += 1

    # 敵の出現
    if enemy_spawn_timer >= enemy_spawn_delay and len(enemies) < max_enemies:
        x = random.randint(WIDTH // 2, WIDTH - enemy_radius)
        y = random.randint(enemy_radius, HEIGHT - enemy_radius)
        enemies.append([x, y])
        enemy_spawn_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # プレイヤー引っ張り
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

    # プレイヤー移動
    if launched:
        player_pos[0] += player_vel[0]
        player_pos[1] += player_vel[1]
        player_vel[0] *= FRICTION
        player_vel[1] *= FRICTION

        # 壁にはみ出さないように位置制限
        keep_player_in_screen()

        # 敵に当たったら敵を消してスコアを増やす
        for e in enemies[:]:
            if distance(player_pos, e) <= player_radius + enemy_radius:
                enemies.remove(e)
                score += 1  # スコア加算

        if math.hypot(player_vel[0], player_vel[1]) < 0.5:
            launched = False
            player_vel = [0, 0]

    draw()

pygame.quit()
