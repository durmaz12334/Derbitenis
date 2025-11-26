# ==========================
#  DERBİ TENİS - SESLİ SÜRÜM
# ==========================

import pygame
import sys
import os
import random
import time
import math

pygame.init()

# ==========================
#  EXE UYUMLU DOSYA YOLU
# ==========================
def resource_path(relative):
    """Hem .py hem .exe halinde dosya yolunu düzgün bulmak için."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

# ==========================
#  SES SİSTEMİ
# ==========================
pygame.mixer.init(frequency=22050, size=-16, channels=2)

try:
    menu_music_path  = resource_path("sounds/menu_music.mp3")
    game_music_path  = resource_path("sounds/game_music.mp3")
    hit_sound_path   = resource_path("sounds/hit.wav")
    point_sound_path = resource_path("sounds/point.wav")
    win_sound_path   = resource_path("sounds/win.wav")

    sound_hit   = pygame.mixer.Sound(hit_sound_path)
    sound_point = pygame.mixer.Sound(point_sound_path)
    sound_win   = pygame.mixer.Sound(win_sound_path)
except Exception as e:
    print("Ses dosyaları yüklenirken hata:", e)
    sound_hit = sound_point = sound_win = None

# oyun müziği kontrol değişkenleri (her durumda var olsunlar)
game_music_started = None
GAME_MUSIC_DURATION = 12  # saniye

def play_menu_music():
    try:
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Menü müziği yüklenemedi:", e)

def play_game_music():
    global game_music_started
    try:
        pygame.mixer.music.load(game_music_path)
        pygame.mixer.music.set_volume(0.45)
        pygame.mixer.music.play(-1)
        game_music_started = time.time()
    except Exception as e:
        print("Oyun müziği yüklenemedi:", e)
        game_music_started = None

# ==========================
#  EKRAN MODU
# ==========================
FULLSCREEN = False

if FULLSCREEN:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
else:
    WIDTH = 1280
    HEIGHT = 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Derbi Tenis - Birlikte Güçlüyüz")
clock = pygame.time.Clock()
FPS = 60

# ==========================
#  FONTLAR
# ==========================
TITLE_FONT = pygame.font.SysFont(None, int(HEIGHT * 0.15))
SUB_FONT   = pygame.font.SysFont(None, int(HEIGHT * 0.06))
MENU_FONT  = pygame.font.SysFont(None, int(HEIGHT * 0.05))
CHANT_FONT = pygame.font.SysFont(None, int(HEIGHT * 0.045))

font      = pygame.font.SysFont(None, int(HEIGHT * 0.06))
big_font  = pygame.font.SysFont(None, int(HEIGHT * 0.14))
win_font  = pygame.font.SysFont(None, int(HEIGHT * 0.20))
golden_font  = pygame.font.SysFont(None, int(HEIGHT * 0.05))
golden_label = golden_font.render("Golden Shot = +5", True, (255, 215, 0))

# ==========================
#  OYUN ORANLAR / BOYUTLAR
# ==========================
CROWD_HEIGHT = int(HEIGHT * 0.26)

PADDLE_WIDTH  = int(WIDTH * 0.010)
PADDLE_HEIGHT = int(HEIGHT * 0.16)
BALL_RADIUS   = int(WIDTH * 0.010)

PADDLE_SPEED = max(3, int(WIDTH * 0.004))
BALL_SPEED   = max(4, int(WIDTH * 0.0055))

# ==========================
#  NESNELERİ BAŞLAT
# ==========================
def reset_objects():
    global paddle_left, paddle_right, ball_x, ball_y

    paddle_left = pygame.Rect(
        int(WIDTH * 0.04),
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT
    )

    paddle_right = pygame.Rect(
        int(WIDTH * 0.96) - PADDLE_WIDTH,
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT
    )

    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2

reset_objects()

ball_vx = BALL_SPEED * random.choice([1, -1])
ball_vy = random.choice([-3, -2, 2, 3])

score_left = 0
score_right = 0
WIN_SCORE = 10

# ==========================
#  GOLDEN SHOT
# ==========================
is_golden = False
golden_end_time = 0
next_golden_time = time.time() + random.randint(15, 35)

# ==========================
#  TRİBÜNLER (FB - GS)
# ==========================
FB_COLORS = [(250, 220, 0), (0, 40, 120), (230, 230, 230)]
GS_COLORS = [(200, 0, 0), (255, 200, 0), (240, 240, 240)]

crowd = []
for _ in range(550):
    x = random.randint(0, WIDTH)
    y = random.randint(0, CROWD_HEIGHT - 5)

    if x < WIDTH // 2:
        c = random.choice(FB_COLORS)
    else:
        c = random.choice(GS_COLORS)

    crowd.append((x, y, c))

def draw_crowd():
    pygame.draw.rect(screen, (22, 22, 22), (0, 0, WIDTH, CROWD_HEIGHT))

    r = max(2, int(WIDTH * 0.0035))
    for x, y, c in crowd:
        pygame.draw.circle(screen, c, (x, y), r)

    pygame.draw.rect(screen, (0, 40, 120), (0, CROWD_HEIGHT - 14, WIDTH // 2, 14))
    pygame.draw.rect(screen, (200, 0, 0), (WIDTH // 2, CROWD_HEIGHT - 14, WIDTH, 14))

# ==========================
#  ÇİMLİ SAHA
# ==========================
def draw_grass():
    for y in range(CROWD_HEIGHT, HEIGHT):
        t = (y - CROWD_HEIGHT) / (HEIGHT - CROWD_HEIGHT)
        shade = int(80 + t * 40)
        pygame.draw.line(screen, (20, shade, 20), (0, y), (WIDTH, y))

    stripe = int(HEIGHT * 0.06)
    for i in range(CROWD_HEIGHT, HEIGHT, stripe * 2):
        o = pygame.Surface((WIDTH, stripe), pygame.SRCALPHA)
        o.fill((0, 0, 0, 45))
        screen.blit(o, (0, i))

    pygame.draw.line(
        screen,
        (230, 230, 230),
        (WIDTH // 2, CROWD_HEIGHT),
        (WIDTH // 2, HEIGHT),
        4
    )

# ==========================
#  GERİ SAYIM
# ==========================
countdown_active = False
countdown_start = 0

def start_countdown():
    global countdown_active, countdown_start
    countdown_active = True
    countdown_start = time.time()

def reset_ball():
    global ball_x, ball_y, ball_vx, ball_vy, is_golden
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_vx = 0
    ball_vy = 0
    is_golden = False
    start_countdown()

# ==========================
#  SPİKER
# ==========================
show_commentator = False
comment_text = ""
comment_end_time = 0

def commentator_say(text, duration=4):
    global show_commentator, comment_text, comment_end_time
    show_commentator = True
    comment_text = text
    comment_end_time = time.time() + duration

def draw_commentator():
    if not show_commentator:
        return

    face_x = WIDTH // 2 - 90
    face_y = CROWD_HEIGHT + 40

    pygame.draw.circle(screen, (240, 220, 180), (face_x, face_y), 40)
    pygame.draw.circle(screen, (0, 0, 0), (face_x - 15, face_y - 10), 6)
    pygame.draw.circle(screen, (0, 0, 0), (face_x + 15, face_y - 10), 6)
    pygame.draw.rect(screen, (0, 0, 0), (face_x - 20, face_y + 10, 40, 8))

    bubble = pygame.Rect(face_x + 50, face_y - 50, 420, 90)
    pygame.draw.rect(screen, (255, 255, 255), bubble, border_radius=12)
    pygame.draw.rect(screen, (50, 50, 50), bubble, 3, border_radius=12)

    txt = MENU_FONT.render(comment_text, True, (0, 0, 0))
    screen.blit(txt, (bubble.x + 15, bubble.y + 25))

# ==========================
#  PANKART (BİRLİKTE GÜÇLÜYÜZ)
# ==========================
BANNER_WIDTH  = int(WIDTH * 0.56)
BANNER_HEIGHT = int(CROWD_HEIGHT * 0.45)
banner_y = -BANNER_HEIGHT
banner_target_y = int(CROWD_HEIGHT * 0.35)
banner_visible = False
banner_end_time = 0
banner_next_time = time.time() + random.randint(20, 30)

banner_text = MENU_FONT.render("BİRLİKTE GÜÇLÜYÜZ", True, (0, 0, 0))

def update_banner(now):
    global banner_y, banner_visible, banner_end_time, banner_next_time

    if (not banner_visible) and now >= banner_next_time:
        banner_visible = True
        banner_end_time = now + 4
        banner_y = -BANNER_HEIGHT

    if banner_visible:
        if now <= banner_end_time:
            banner_y += (banner_target_y - banner_y) * 0.12
        else:
            banner_y += ((-BANNER_HEIGHT) - banner_y) * 0.18
            if banner_y <= -BANNER_HEIGHT + 3:
                banner_visible = False
                banner_next_time = now + random.randint(20, 30)

def draw_banner(now):
    if not banner_visible:
        return

    wave = math.sin(now * 3) * 4
    x = WIDTH // 2 - BANNER_WIDTH // 2
    y = int(banner_y + wave)

    body = pygame.Rect(x, y, BANNER_WIDTH, BANNER_HEIGHT)

    pygame.draw.rect(screen, (250, 250, 250), body, border_radius=16)
    pygame.draw.rect(screen, (200, 200, 200), body, 3, border_radius=16)

    tip_mid = x + BANNER_WIDTH // 2
    tip_y = y + BANNER_HEIGHT + 32

    pygame.draw.polygon(screen, (250, 250, 250), [
        (x, y + BANNER_HEIGHT),
        (x + BANNER_WIDTH, y + BANNER_HEIGHT),
        (tip_mid, tip_y)
    ])
    pygame.draw.polygon(screen, (200, 200, 200), [
        (x, y + BANNER_HEIGHT),
        (x + BANNER_WIDTH, y + BANNER_HEIGHT),
        (tip_mid, tip_y)
    ], 3)

    text_rect = banner_text.get_rect(center=(x + BANNER_WIDTH // 2, y + BANNER_HEIGHT // 2))
    screen.blit(banner_text, text_rect)

# ==========================
#  TEZAHÜRAT
# ==========================
fb_next = time.time() + random.randint(8, 15)
gs_next = time.time() + random.randint(8, 15)
fb_until = 0
gs_until = 0

CHANT_TEXT = CHANT_FONT.render("BİRLİKTE GÜÇLÜYÜZ!", True, (255, 255, 255))

def update_chants(now):
    global fb_next, gs_next, fb_until, gs_until

    if now >= fb_next:
        fb_until = now + 1.2
        fb_next = now + random.randint(12, 20)

    if now >= gs_next:
        gs_until = now + 1.2
        gs_next = now + random.randint(12, 20)

def draw_chants(now):
    if now < fb_until:
        screen.blit(CHANT_TEXT, (40, 10))
    if now < gs_until:
        screen.blit(CHANT_TEXT, (WIDTH - CHANT_TEXT.get_width() - 40, 10))

# ==========================
#  KONTROLLER EKRANI
# ==========================
def controls_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        draw_grass()
        draw_crowd()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = TITLE_FONT.render("KONTROLLER", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        text_list = [
            "Sol Oyuncu: W / S",
            "Sağ Oyuncu: Yukarı / Aşağı ok tuşları",
            "Golden Shot: +5 puan (top altın renkteyken)",
            "Tribünler otomatik 'Birlikte Güçlüyüz' der",
            "",
            "[ESC] Geri Dön"
        ]

        for i, line in enumerate(text_list):
            t = MENU_FONT.render(line, True, (255, 255, 255))
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 240 + i * 55))

        pygame.display.flip()
        clock.tick(60)

# ==========================
#  ANA MENÜ
# ==========================
def menu_screen():
    t = 0
    play_menu_music()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_c:
                    controls_screen()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        draw_grass()
        draw_crowd()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        t += 0.07
        offset = int(abs(12 * math.sin(t)))

        title = TITLE_FONT.render("DERBİ TENİS", True, (255, 255, 255))
        sub   = SUB_FONT.render('"Birlikte Güçlüyüz"', True, (255, 215, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2,
                                                  HEIGHT // 2 - 150 + offset)))
        screen.blit(sub,   sub.get_rect(center=(WIDTH // 2,
                                                HEIGHT // 2 - 70)))

        start = MENU_FONT.render("[SPACE] Maça Başla", True, (230, 230, 230))
        ctrl  = MENU_FONT.render("[C] Kontroller",    True, (230, 230, 230))
        esc   = MENU_FONT.render("[ESC] Çıkış",       True, (230, 230, 230))

        screen.blit(start, start.get_rect(center=(WIDTH // 2,
                                                  HEIGHT // 2 + 60)))
        screen.blit(ctrl,  ctrl.get_rect(center=(WIDTH // 2,
                                                 HEIGHT // 2 + 130)))
        screen.blit(esc,   esc.get_rect(center=(WIDTH // 2,
                                                HEIGHT // 2 + 200)))

        pygame.display.flip()
        clock.tick(60)

# ==========================
#  OYUNU BAŞLAT
# ==========================
menu_screen()
play_game_music()
commentator_say("Galatasaray - Fenerbahçe derbisine hoş geldiniz!", 5)
start_countdown()

# ==========================
#  KAZANMA ANİMASYONU
# ==========================
def show_winner(text):
    if sound_win is not None:
        sound_win.play()

    for _ in range(90):
        screen.fill((0, 0, 0))
        glow = (255, random.randint(80, 255), 0)

        img = win_font.render(text, True, glow)
        screen.blit(img, img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

        sub = SUB_FONT.render("Birlikte Güçlüyüz", True, (255, 215, 0))
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

        pygame.display.flip()
        clock.tick(60)
    return 0, 0

# ==========================
#  ANA OYUN DÖNGÜSÜ
# ==========================
while True:
    now = time.time()

    # Oyun müziğini süre dolunca durdur
    if game_music_started is not None and pygame.mixer.music.get_busy():
        if now - game_music_started >= GAME_MUSIC_DURATION:
            pygame.mixer.music.stop()
            game_music_started = None

    # Spiker süresi bitti mi?
    if show_commentator and now > comment_end_time:
        show_commentator = False

    # EVENTLER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # RAKET HAREKETİ
    if keys[pygame.K_w]:
        paddle_left.y -= PADDLE_SPEED
    if keys[pygame.K_s]:
        paddle_left.y += PADDLE_SPEED
    if keys[pygame.K_UP]:
        paddle_right.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN]:
        paddle_right.y += PADDLE_SPEED

    paddle_left.clamp_ip(screen.get_rect())
    paddle_right.clamp_ip(screen.get_rect())

    # GERİ SAYIM
    if countdown_active:
        elapsed = now - countdown_start

        if elapsed < 1:
            txt = "3"
        elif elapsed < 2:
            txt = "2"
        elif elapsed < 3:
            txt = "1"
        elif elapsed < 4:
            txt = "GO!"
        else:
            countdown_active = False
            ball_vx = BALL_SPEED * random.choice([1, -1])
            ball_vy = random.choice([-3, -2, 2, 3])
            txt = ""

        draw_grass()
        draw_crowd()
        update_banner(now)
        draw_banner(now)
        update_chants(now)
        draw_chants(now)

        pygame.draw.rect(screen, (0, 200, 255), paddle_left)
        pygame.draw.rect(screen, (255, 80, 0),  paddle_right)

        img = big_font.render(txt, True, (255, 255, 0))
        screen.blit(img, img.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        draw_commentator()

        pygame.display.flip()
        clock.tick(FPS)
        continue

    # TOP HAREKETİ
    ball_x += ball_vx
    ball_y += ball_vy

    # Üst / alt çarpma
    if ball_y - BALL_RADIUS < CROWD_HEIGHT:
        ball_y = CROWD_HEIGHT + BALL_RADIUS
        ball_vy *= -1
    if ball_y + BALL_RADIUS > HEIGHT:
        ball_y = HEIGHT - BALL_RADIUS
        ball_vy *= -1

    # GOLDEN SHOT
    if (not is_golden) and now >= next_golden_time:
        is_golden = True
        golden_end_time = now + 10
        next_golden_time = now + random.randint(20, 40)
        ball_vx *= 1.8
        ball_vy *= 1.8
    if is_golden and now > golden_end_time:
        is_golden = False

    # RAKET ÇARPMALARI
    if ball_x - BALL_RADIUS <= paddle_left.right:
        if paddle_left.y <= ball_y <= paddle_left.y + PADDLE_HEIGHT:
            ball_x = paddle_left.right + BALL_RADIUS
            ball_vx *= -1
            if sound_hit is not None:
                sound_hit.play()
            dif = ball_y - (paddle_left.y + PADDLE_HEIGHT / 2)
            ball_vy += dif * 0.07
            ball_vx *= 1.12
            ball_vy *= 1.12

    if ball_x + BALL_RADIUS >= paddle_right.left:
        if paddle_right.y <= ball_y <= paddle_right.y + PADDLE_HEIGHT:
            ball_x = paddle_right.left - BALL_RADIUS
            ball_vx *= -1
            if sound_hit is not None:
                sound_hit.play()
            dif = ball_y - (paddle_right.y + PADDLE_HEIGHT / 2)
            ball_vy += dif * 0.07
            ball_vx *= 1.12
            ball_vy *= 1.12

    # PUAN
    if ball_x < 0:
        if is_golden:
            score_right += 5
        else:
            score_right += 1
        if sound_point is not None:
            sound_point.play()
        reset_ball()

    if ball_x > WIDTH:
        if is_golden:
            score_left += 5
        else:
            score_left += 1
        if sound_point is not None:
            sound_point.play()
        reset_ball()

    # KAZANMA
    if score_left >= WIN_SCORE:
        score_left, score_right = show_winner("SOL TRİBÜN KAZANDI!")
        commentator_say("Kazanan da kaybeden de... Birlikte Güçlüyüz!", 5)
        reset_objects()
        start_countdown()

    if score_right >= WIN_SCORE:
        score_left, score_right = show_winner("SAĞ TRİBÜN KAZANDI!")
        commentator_say("Kazanan da kaybeden de... Birlikte Güçlüyüz!", 5)
        reset_objects()
        start_countdown()

    # HIZ LİMİTİ
    max_vx = WIDTH * 0.017
    max_vy = HEIGHT * 0.017
    ball_vx = max(-max_vx, min(max_vx, ball_vx))
    ball_vy = max(-max_vy, min(max_vy, ball_vy))

    # ÇİZİM
    draw_grass()
    draw_crowd()
    update_banner(now)
    draw_banner(now)
    update_chants(now)
    draw_chants(now)

    pygame.draw.rect(screen, (0, 200, 255), paddle_left)
    pygame.draw.rect(screen, (255, 80, 0),  paddle_right)

    if is_golden:
        pygame.draw.circle(screen, (255, 215, 0), (int(ball_x), int(ball_y)), BALL_RADIUS)
        screen.blit(golden_label, (WIDTH - golden_label.get_width() - 20, 10))
    else:
        pygame.draw.circle(screen, (255, 255, 255), (int(ball_x), int(ball_y)), BALL_RADIUS)

    s_left  = font.render(str(score_left),  True, (255, 255, 255))
    s_right = font.render(str(score_right), True, (255, 255, 255))
    screen.blit(s_left,  (WIDTH // 2 - 80, CROWD_HEIGHT + 20))
    screen.blit(s_right, (WIDTH // 2 + 40, CROWD_HEIGHT + 20))

    draw_commentator()

    pygame.display.flip()
    clock.tick(FPS)
