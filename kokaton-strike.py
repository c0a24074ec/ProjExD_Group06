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

class SoundManager():
    """
    ゲーム内のBGMや効果音の再生を管理するクラス
    """
    def __init__(self):
        """
        BGM、効果音を初期化しBGMをループ
        """
        pygame.mixer.init()
        pygame.mixer.music.load("ex5/sounds/maou_bgm.mp3")  # BGMの設定
        pygame.mixer.music.set_volume(0.2)  # 音量20%
        pygame.mixer.music.play(-1)  # ループ再生

        self.launch_sound = pygame.mixer.Sound("ex5/sounds/maou_launch.wav") # 発射音の設定
        self.launch_sound.set_volume(0.5)  # 発射音の音量設定(50&)

        self.hit_sound = pygame.mixer.Sound("ex5/sounds/maou_hit.wav") # 敵に当たった時の効果音の設定の設定
        self.hit_sound.set_volume(0.5)  # 敵ヒット音の音量設定(50%)

        self.wall_hit_sound = pygame.mixer.Sound("ex5/sounds/maou_wall.wav") # 壁にぶつかったときの効果音の設定
        self.wall_hit_sound.set_volume(0.7)  # 壁ヒット音の音量設定(70%)

    def play_launch(self): # 発射時の効果音を再生する
        self.launch_sound.play()

    def play_hit(self): # 敵に命中した時の効果音を再生する
        self.hit_sound.play()

    def play_wall_hit(self): # 壁にぶつかったときの効果音を再生する
        self.wall_hit_sound.play()

# SoundManagerのインスタンス化
sound_manager = SoundManager()

# 画像読み込み・リサイズ
player_img = pygame.image.load("ex5/fig/0.png").convert_alpha()  # 画像パスは環境に合わせて
default_img = pygame.transform.scale(player_img, (40, 40))

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
    hit = False # 最初は壁にぶつかっていない
    if player_pos[0] - player_radius < 0:
        player_pos[0] = player_radius
        player_vel[0] *= -1
        hit = True # 壁にぶつかったことを記録
    elif player_pos[0] + player_radius > WIDTH:
        player_pos[0] = WIDTH - player_radius
        player_vel[0] *= -1
        hit = True # 壁にぶつかったことを記録

    if player_pos[1] - player_radius < 0:
        player_pos[1] = player_radius
        player_vel[1] *= -1
        hit = True # 壁にぶつかったことを記録
    elif player_pos[1] + player_radius > HEIGHT:
        player_pos[1] = HEIGHT - player_radius
        player_vel[1] *= -1
        hit = True # 壁にぶつかったことを記録

    # 壁に当たったら効果音を鳴らす(Trueだったら鳴らす)
    if hit:
        sound_manager.play_wall_hit()

    return hit # 当たったかどうかを返す

def draw():
    screen.fill(WHITE)

    # 敵を描画
    for e in enemies:
        pygame.draw.circle(screen, RED, e, enemy_radius)

    # 引っ張り線
    if dragging:
        pygame.draw.line(screen, GREEN, player_pos, pygame.mouse.get_pos(), 3)

    # プレイヤー画像を描画
    rect = default_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
    screen.blit(default_img, rect)

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
            sound_manager.play_launch() #発射したときの効果音を鳴らす

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
                sound_manager.play_hit() #敵に当たったときの効果音を鳴らす

        if math.hypot(player_vel[0], player_vel[1]) < 0.5:
            launched = False
            player_vel = [0, 0]

    draw()

pygame.quit()
