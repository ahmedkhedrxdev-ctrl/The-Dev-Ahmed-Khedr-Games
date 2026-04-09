import pygame
import random
import sys
import os

# --- دالة المسارات للتحويل لـ EXE ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- إعدادات اللعبة ---
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
FPS = 60

BIRD_X, BIRD_Y = 50, 250
BIRD_SCALE = 1.5
PIPE_WIDTH, PIPE_GAP = 46, 150
PIPE_SPEED = 7
GRAVITY, JUMP_STRENGTH = 0.3, -6

# --- تهيئة ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Ryu")

try:
    icon_img = pygame.image.load(resource_path("assets/icon.png"))
    pygame.display.set_icon(icon_img)
except: pass

clock = pygame.time.Clock()

# --- تحميل الأصول ---
bird_img = pygame.image.load(resource_path("assets/bird.png")).convert_alpha()
pipe_head_img = pygame.image.load(resource_path("assets/pipeHead.png")).convert_alpha()
pipe_body_img = pygame.image.load(resource_path("assets/pipeBody.png")).convert_alpha()
morning_img = pygame.image.load(resource_path("assets/Morning.png")).convert()
night_img = pygame.image.load(resource_path("assets/Night.png")).convert()
start_img = pygame.image.load(resource_path("assets/s.png")).convert_alpha()
restart_img = pygame.image.load(resource_path("assets/r.png")).convert_alpha()
main_menu_img = pygame.image.load(resource_path("assets/MM.png")).convert_alpha()

scale_f = 15
morning_scaled = pygame.transform.scale(morning_img, (morning_img.get_width()*scale_f, morning_img.get_height()*scale_f))
night_scaled = pygame.transform.scale(night_img, (night_img.get_width()*scale_f, night_img.get_height()*scale_f))

score_font = pygame.font.Font(resource_path("assets/04B_19__.TTF"), 48)
dialog_font = pygame.font.SysFont("Consolas", 19, bold=False)

# --- نظام الـ Dialog Box (الشاشة السوداء بالكامل) ---
dialog_messages = [
    "Welcome To My Game!",
    "Thanks For Playing The Game.",
    "This Game Copyrights Return to",
    "Ahmed Khader Waseef!",
    "We'll See You In Another Game.",
    "Finally, All Of This Is From The Grace Of God.",
    "PRESS ANY BUTTON TO QUIT.",
]
dialog_active = False
dialog_stage = 0 
current_msg_idx = 0
char_idx = 0
typing_timer = 0
box_scale = 0.0

def play_type_sound():
    pygame.mixer.Sound(buffer=bytes([128]*150)).play()

def draw_dialog_box():
    global box_scale, char_idx, typing_timer, dialog_stage, dialog_active, current_msg_idx
    
    # تعتيم كامل للشاشة (سواد تام)
    screen.fill((0, 0, 0))

    target_w, target_h = 550, 160
    cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2

    if dialog_stage == 0: 
        box_scale += 0.12
        if box_scale >= 1.0: box_scale = 1.0; dialog_stage = 1
    elif dialog_stage == 3: 
        box_scale -= 0.04
        if box_scale <= 0: dialog_active = False; return

    curr_w = int(target_w * box_scale)
    curr_h = int(target_h * box_scale)
    rect = pygame.Rect(cx - curr_w//2, cy - curr_h//2, curr_w, curr_h)
    
    if curr_h > 1:
        # تدرج لوني داخل الصندوق
        for i in range(curr_h):
            color_val = max(0, 120 - (i * 120 // curr_h)) 
            pygame.draw.line(screen, (0, 0, color_val), (rect.x, rect.y + i), (rect.x + curr_w, rect.y + i))
    
    pygame.draw.rect(screen, (255, 255, 255), rect, 3) 

    if dialog_stage in [1, 2]:
        full_text = dialog_messages[current_msg_idx]
        if dialog_stage == 1:
            typing_timer += 1
            if typing_timer % 3 == 0:
                char_idx += 1
                play_type_sound()
                if char_idx >= len(full_text): dialog_stage = 2
        
        shown_text = full_text[:char_idx]
        txt_surf = dialog_font.render(shown_text, True, (255, 255, 255))
        screen.blit(txt_surf, (rect.x + 30, rect.y + 50))

# --- منطق اللعبة ---
music1 = resource_path("assets/Music1.mp3")
music2 = resource_path("assets/Music2.mp3")

def play_music(track):
    try:
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(-1)
    except: pass

bird_frames = []
for i in range(20):
    f = pygame.Surface((32, 32), pygame.SRCALPHA)
    f.blit(bird_img, (0,0), (i*32,0,32,32))
    bird_frames.append(f)

bird_y, bird_v, pipes, score, frame = BIRD_Y, 0, [], 0, 0
game_started, game_over = False, False
current_bg, next_bg = "morning", "night"
last_milestone = 0 # لمتابعة مضاعفات الـ 20
fade_alpha, fading = 0, False
secret_code = []

def create_pipe():
    h = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
    pipes.append({"x": SCREEN_WIDTH + 50, "top": h, "bottom": h + PIPE_GAP, "passed": False})

def reset_game():
    global bird_y, bird_v, pipes, score, last_milestone, current_bg
    bird_y, bird_v, pipes, score, last_milestone = BIRD_Y, 0, [], 0, 0
    current_bg = "morning"
    play_music(music1)

def draw_game():
    global fade_alpha, fading, current_bg
    screen.blit(morning_scaled if current_bg == "morning" else night_scaled, (0,0))

    if fading:
        fs = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        fs.blit(night_scaled if next_bg == "night" else morning_scaled, (0,0))
        fs.set_alpha(fade_alpha)
        screen.blit(fs,(0,0))
        fade_alpha += 5
        if fade_alpha >= 255: fading, current_bg = False, next_bg

    idx = (pygame.time.get_ticks() // 100) % 20
    bs = pygame.transform.scale(bird_frames[idx], (int(32*BIRD_SCALE), int(32*BIRD_SCALE)))
    screen.blit(bs,(BIRD_X,bird_y))

    for p in pipes:
        screen.blit(pipe_head_img,(p["x"], p["top"]-pipe_head_img.get_height()))
        screen.blit(pygame.transform.scale(pipe_body_img, (PIPE_WIDTH, p["top"]-pipe_head_img.get_height())), (p["x"],0))
        screen.blit(pipe_head_img,(p["x"], p["bottom"]))
        screen.blit(pygame.transform.scale(pipe_body_img, (PIPE_WIDTH, SCREEN_HEIGHT-p["bottom"])), (p["x"], p["bottom"]+pipe_head_img.get_height()))

    txt = score_font.render(str(score), True, (255,255,255))
    screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 20))

    if not game_started and not game_over:
        screen.blit(start_img,(SCREEN_WIDTH//2-start_img.get_width()//2, SCREEN_HEIGHT//2+50))
    if game_over:
        screen.blit(restart_img,(SCREEN_WIDTH//2-restart_img.get_width()//2, SCREEN_HEIGHT//2+50))
        screen.blit(main_menu_img,(SCREEN_WIDTH//2-main_menu_img.get_width()//2, SCREEN_HEIGHT//2+130))
    
    if dialog_active: draw_dialog_box()

# --- اللوب ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if not game_started and not game_over and not dialog_active:
                secret_code.append(event.key)
                if len(secret_code) > 7: secret_code.pop(0)
                if secret_code == [pygame.K_RIGHT, pygame.K_RIGHT, pygame.K_RIGHT, pygame.K_UP, pygame.K_UP, pygame.K_UP, pygame.K_DOWN]:
                    dialog_active, dialog_stage, current_msg_idx, char_idx, box_scale = True, 0, 0, 0, 0.0
            
            if dialog_active and dialog_stage == 2:
                current_msg_idx += 1
                if current_msg_idx < len(dialog_messages): dialog_stage, char_idx = 1, 0
                else: dialog_stage = 3
            elif game_started and not game_over:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP): bird_v = JUMP_STRENGTH

        if event.type == pygame.MOUSEBUTTONDOWN and not dialog_active:
            mx, my = pygame.mouse.get_pos()
            if not game_started and not game_over:
                bx, by = SCREEN_WIDTH//2-start_img.get_width()//2, SCREEN_HEIGHT//2+50
                if bx<mx<bx+start_img.get_width() and by<my<by+start_img.get_height():
                    game_started = True; play_music(music1)
            elif game_over:
                # Restart
                if SCREEN_WIDTH//2-75<mx<SCREEN_WIDTH//2+75 and SCREEN_HEIGHT//2+50<my<SCREEN_HEIGHT//2+110:
                    game_over, game_started = False, True; reset_game()
                # Menu
                if SCREEN_WIDTH//2-75<mx<SCREEN_WIDTH//2+75 and SCREEN_HEIGHT//2+130<my<SCREEN_HEIGHT//2+190:
                    game_over, game_started = False, False; reset_game()

    if game_started and not game_over and not dialog_active:
        bird_v += GRAVITY
        bird_y += bird_v
        for p in pipes: p["x"] -= PIPE_SPEED
        for p in pipes:
            if not p["passed"] and BIRD_X > p["x"]+PIPE_WIDTH:
                p["passed"] = True
                score += 1
                # التبديل كل 20 نقطة
                if score > 0 and score % 20 == 0 and score != last_milestone:
                    last_milestone = score
                    fading, fade_alpha = True, 0
                    if current_bg == "morning":
                        next_bg, track = "night", music2
                    else:
                        next_bg, track = "morning", music1
                    play_music(track)

        for p in pipes:
            if (BIRD_X + 35 > p["x"] and BIRD_X < p["x"] + PIPE_WIDTH and (bird_y < p["top"] or bird_y + 35 > p["bottom"])):
                pygame.mixer.music.stop(); game_over, game_started = True, False
        if pipes and pipes[0]["x"] < -100: pipes.pop(0)
        if bird_y > SCREEN_HEIGHT or bird_y < 0: pygame.mixer.music.stop(); game_over, game_started = True, False
        frame += 1
        if frame % 90 == 0: create_pipe()

    draw_game()
    pygame.display.flip()

pygame.quit()
sys.exit()
