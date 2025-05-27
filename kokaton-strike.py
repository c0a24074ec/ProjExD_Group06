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
player_img = pygame.image.load("ex5/0.png").convert_alpha()  # 画像パスは環境に合わせて
default_img = pygame.transform.scale(player_img, (40, 40))

class HPBar:
    def __init__(self, max_hp):
        self.max_hp = max_hp  
        self.hp = max_hp    # 現在のHPを初期化
        self.width = 40    # HPバーの横幅（ピクセル）
        self.height = 6    # HPバーの高さ（ピクセル）

    def draw(self, screen, center_pos, enemy_radius):
        hp_ratio = self.hp / self.max_hp   # 現在のHPの割合（0.0〜1.0）
        bar_x = center_pos[0] - self.width // 2   # HPバーの左端X座標
        bar_y = center_pos[1] + enemy_radius + 5   # HPバーのY座標

        # 背景（灰色）とHPバー（緑）
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, self.width, self.height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(self.width * hp_ratio), self.height))

    def take_damage(self, amount=1):
        self.hp = max(0, self.hp - amount)

    def is_dead(self):
        return self.hp <= 0

# プレイヤー
player_pos = [150, 300]
player_radius = 20
player_vel = [0, 0]
dragging = False
launched = False
hit_enemies=set()
player_hp = HPBar(10)
# 敵（赤玉）
enemy_radius = 25
enemies = []
max_enemies = 5
enemy_spawn_timer = 0
enemy_spawn_delay = 90

FRICTION = 0.98
FONT = pygame.font.SysFont(None, 36)
attack_font=pygame.font.SysFont("MS Gothic",48,bold=True)

score = 0  # スコア変数追加

action_count=0 # プレイヤーの行動回数
enemy_attack_interval=3 # 何回行動したら攻撃されるか

def distance(p1, p2):
    if isinstance(p2, dict):  
        p2 = p2["pos"]
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

    # 敵を描画
    for e in enemies:
        pygame.draw.circle(screen, RED, e["pos"], enemy_radius)
        e["hp_obj"].draw(screen, e["pos"], enemy_radius)
    # 引っ張り線
    if dragging:
        pygame.draw.line(screen, GREEN, player_pos, pygame.mouse.get_pos(), 3)

    # プレイヤー画像を描画
    rect = default_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
    screen.blit(default_img, rect)
    player_hp.draw(screen, player_pos, player_radius)

    # スコア表示
    score_surf = FONT.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surf, (20, 20))

    pygame.display.flip()


running = True
while running:
    clock.tick(60)
    enemy_spawn_timer += 1

    # 敵の出現
    if enemy_spawn_timer >= enemy_spawn_delay and len(enemies) < max_enemies:
        x = random.randint(WIDTH // 2, WIDTH - enemy_radius)
        y = random.randint(enemy_radius, HEIGHT - enemy_radius)
        enemies.append({
            "pos":[x,y],
            "hp_obj":HPBar(3)
        })
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
            enemy_id=id(e)
            if enemy_id not in hit_enemies and distance(player_pos, e) <= player_radius + enemy_radius:
                hit_enemies.add(enemy_id)
                e["hp_obj"].take_damage()
                if e["hp_obj"].is_dead():
                    enemies.remove(e)
                    score += 1

        if math.hypot(player_vel[0], player_vel[1]) < 0.5:
            launched = False
            player_vel = [0, 0]
            hit_enemies.clear()

            action_count += 1

            # 行動回数が一定に達したら敵の攻撃
            if action_count >= enemy_attack_interval:
                attack_text=attack_font.render("敵の攻撃！",True,RED)
                screen.blit(attack_text,(WIDTH//2-attack_text.get_width()//2,HEIGHT//2-24))
                pygame.display.flip()
                pygame.time.wait(1000) # 1秒表示

                player_hp.take_damage(2)
                action_count=0

    draw()

pygame.quit()