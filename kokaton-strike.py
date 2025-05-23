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
player_img = pygame.image.load("ex5/fig/0.png").convert_alpha()  # 画像パスは環境に合わせて
default_img = pygame.transform.scale(player_img, (40, 40))

# プレイヤー
player_pos = [150, 300]
player_radius = 20
player_vel = [0, 0]
dragging = False
launched = False

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
    screen.fill(WHITE)

    # 引っ張り線
    if dragging:
        pygame.draw.line(screen, GREEN, player_pos, pygame.mouse.get_pos(), 3)

    # 画像を描画
    rect = default_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
    screen.blit(default_img, rect)
    enemy.draw()

    # スコア表示
    score_surf = FONT.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surf, (20, 20))

    pygame.display.flip()

class Enemy(): #敵クラス
    def __init__(self):
        self.enemies=[] #敵の位置情報リスト
        self.p = [] #敵の弾リスト
        self.spawn_timer=0 # 敵を出現させるタイマー
        self.spawn_delay=90 #敵が出現するフレーム数
        self.max_enemies=5 #敵の最大数
        self.radius=20 #敵キャラの当たり判定
        self.img=pygame.image.load(f"ex5/fig/enemy1.png") #敵の画像を読み込む
        self.img = pygame.transform.scale(self.img, (80, 71 )) #敵画像のサイズ変更
        self.shoot_timer = 0 #弾タイマーのカウンター
        self.shoot_delay = 60  #弾を発射する間隔

    def fire_p(self, enemy):
        angle = random.uniform(0, 2 * math.pi) #ランダムの角度を取得
        vx = math.cos(angle) * 5 #x方向の速度
        vy = math.sin(angle) * 5 #y方向の速度
        self.p.append({'pos': list(enemy),  'vel': [vx, vy] })

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay and len(self.enemies) < self.max_enemies:
            x = random.randint(WIDTH // 2, WIDTH - self.radius)# 敵のx座標
            y = random.randint(self.radius, HEIGHT - self.radius)# 敵のy座標
            self.enemies.append([x, y,5]) # 新しい敵を追加。初期体力は5
            self.spawn_timer = 0

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay: 
            for e in self.enemies:
                self.fire_p(e)
            self.shoot_timer = 0

        for b in self.p:
            b['pos'][0] += b['vel'][0]# x座標更新
            b['pos'][1] += b['vel'][1]# y座標更新
        # 画面外の弾をリストから削除
        self.p = [b for b in self.p if 0 <= b['pos'][0] <= WIDTH and 0 <= b['pos'][1] <= HEIGHT]

    def draw(self):
        for pos in self.enemies:
            rect = self.img.get_rect(center=(pos[0], pos[1]))
             # すべての弾を赤い円で描画
            for b in self.p:
                pygame.draw.circle(screen, RED, (int(b['pos'][0]), int(b['pos'][1])), 5)
            screen.blit(self.img, rect)

    def check_collision(self, player_pos, player_radius):
        global score
        for e in self.enemies:
           dist = distance(player_pos, e) # プレイヤーと敵の距離を計算
           if dist <= player_radius + self.radius:
            e[2] -= 1  # 体力を1減らす
            if e[2] <= 0:
                self.enemies.remove(e)  # 体力がなくなったら敵を消す
                score += 1             # スコ＋１

running = True
enemy=Enemy()
while running:
    clock.tick(60)
    enemy.update()
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

    if launched:
        player_pos[0] += player_vel[0]
        player_pos[1] += player_vel[1]
        player_vel[0] *= FRICTION
        player_vel[1] *= FRICTION

        keep_player_in_screen()
        enemy.check_collision(player_pos, player_radius)

        if math.hypot(player_vel[0], player_vel[1]) < 0.5:
            launched = False
            player_vel = [0, 0]

    draw()

pygame.quit()
