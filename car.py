import pygame
import random
import os
from sys import exit

# ======================================
# Inisialisasi
# ======================================
pygame.init()

WIDTH = 500
HEIGHT = 700

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Game")

clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont("Arial", 26, bold=True)
font_title = pygame.font.SysFont("Arial", 40, bold=True)
font_small = pygame.font.SysFont("Arial", 20)

# ======================================
# Konstanta
# ======================================
ROAD_LEFT = 120
ROAD_RIGHT = 380

CAR_WIDTH = 60
CAR_HEIGHT = 100

PLAYER_SPEED = 7

MIN_SPEED = 6
MAX_SPEED = 18
ACCELERATION = 0.2
DECELERATION = 0.15

WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
RED = (255, 50, 50)

# Game States
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# ======================================
# Folder Asset
# ======================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "asset")

# ======================================
# Load Image
# ======================================
def load_image(filename, scale=None):
    path = os.path.join(ASSET_DIR, filename)

    if not os.path.exists(path):
        print("File tidak ditemukan :", path)
        pygame.quit()
        exit()

    image = pygame.image.load(path).convert_alpha()

    if scale is not None:
        image = pygame.transform.scale(image, scale)

    return image


# Load semua aset
road_image = load_image("jalan.png", (WIDTH, HEIGHT))
car_image = load_image("car.png", (CAR_WIDTH, CAR_HEIGHT))
car_left_image = load_image("car_kiri.png", (CAR_WIDTH, CAR_HEIGHT))
car_right_image = load_image("car_kanan.png", (CAR_WIDTH, CAR_HEIGHT))
enemy_images = [
    load_image("Putih.png", (CAR_WIDTH, CAR_HEIGHT)),
    load_image("Kuning_putih.png", (CAR_WIDTH, CAR_HEIGHT)),
    load_image("hitam.png", (CAR_WIDTH, CAR_HEIGHT)),
    load_image("hijau.png", (CAR_WIDTH, CAR_HEIGHT))
]
explosion_image = load_image("ledakan.png", (120, 120))


# ======================================
# Player
# ======================================
class Player(pygame.Rect):

    def __init__(self):
        super().__init__(
            WIDTH // 2 - CAR_WIDTH // 2,
            HEIGHT - 140,
            CAR_WIDTH,
            CAR_HEIGHT
        )
        self.image = car_image

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.x -= PLAYER_SPEED
            self.image = car_left_image
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.x += PLAYER_SPEED
            self.image = car_right_image
        else:
            self.image = car_image

        # Batas jalan
        if self.left < ROAD_LEFT:
            self.left = ROAD_LEFT

        if self.right > ROAD_RIGHT:
            self.right = ROAD_RIGHT

    def draw(self):
        window.blit(self.image, self)


# ======================================
# Enemy
# ======================================
class Enemy(pygame.Rect):

    def __init__(self):
        super().__init__(
            random.randint(ROAD_LEFT, ROAD_RIGHT - CAR_WIDTH),
            -120,
            CAR_WIDTH,
            CAR_HEIGHT
        )
        self.image = random.choice(enemy_images)

    def update(self, speed):
        global score
        self.y += speed

        if self.top > HEIGHT:
            self.reset()
            score += 1

    def reset(self):
        self.y = -120
        self.x = random.randint(ROAD_LEFT, ROAD_RIGHT - CAR_WIDTH)
        self.image = random.choice(enemy_images)

    def draw(self):
        window.blit(self.image, self)


# ======================================
# Inisialisasi Objek & State
# ======================================
player = Player()
enemy = Enemy()

speed = MIN_SPEED
score = 0
road_y = 0
state = STATE_START
explosion_pos = None


# ======================================
# Draw Screen
# ======================================
def draw():
    # Render scrolling background
    window.blit(road_image, (0, int(road_y)))
    window.blit(road_image, (0, int(road_y) - HEIGHT))

    if state == STATE_START:
        # Start Menu Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        window.blit(overlay, (0, 0))

        # Title
        title_text = font_title.render("RETRO CAR RACER", True, GOLD)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        window.blit(title_text, title_rect)

        # Instructions
        inst_y = HEIGHT // 2 - 50
        instructions = [
            "Tekan [ ENTER ] untuk Mulai",
            "Tekan [ ESC ] untuk Keluar",
            "",
            "Kontrol:",
            "- Tombol KIRI / KANAN untuk belok",
            "- Tombol ATAS untuk gas",
            "- Tombol BAWAH untuk rem"
        ]
        for line in instructions:
            color = WHITE if not line.startswith("-") else (200, 200, 200)
            text = font_small.render(line, True, color)
            rect = text.get_rect(center=(WIDTH // 2, inst_y))
            window.blit(text, rect)
            inst_y += 35

    elif state == STATE_PLAYING:
        player.draw()
        enemy.draw()

        # HUD Panel (Score & Speed)
        hud_surface = pygame.Surface((180, 85), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 120))  # Semi-transparent card
        window.blit(hud_surface, (10, 10))

        score_text = font.render(f"Score : {score}", True, WHITE)
        speed_text = font.render(f"Speed : {int(speed * 10)} km/h", True, WHITE)
        window.blit(score_text, (20, 20))
        window.blit(speed_text, (20, 55))

    elif state == STATE_GAME_OVER:
        # Draw final positions of cars
        player.draw()
        enemy.draw()

        # Draw explosion effect at collision point
        if explosion_pos:
            explosion_rect = explosion_image.get_rect(center=explosion_pos)
            window.blit(explosion_image, explosion_rect)

        # Game Over Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 10, 10, 200))  # Semi-transparent dark red card
        window.blit(overlay, (0, 0))

        # Game Over Title
        go_text = font_title.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        window.blit(go_text, go_rect)

        # Final Score
        score_text = font.render(f"Skor Akhir: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(score_text, score_rect)

        # Actions instructions
        actions = [
            "Tekan [ R ] untuk Main Lagi",
            "Tekan [ Q ] untuk Keluar"
        ]
        action_y = HEIGHT // 2 + 80
        for line in actions:
            text = font_small.render(line, True, (220, 220, 220))
            rect = text.get_rect(center=(WIDTH // 2, action_y))
            window.blit(text, rect)
            action_y += 40


# ======================================
# Game Loop
# ======================================
running = True

while running:
    clock.tick(60)

    # ----------------------------------
    # Event Handling
    # ----------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if state == STATE_START:
                if event.key == pygame.K_RETURN:
                    # Reset game stats and start game
                    score = 0
                    speed = MIN_SPEED
                    player.x = WIDTH // 2 - CAR_WIDTH // 2
                    player.image = car_image
                    enemy.reset()
                    explosion_pos = None
                    state = STATE_PLAYING
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif state == STATE_GAME_OVER:
                if event.key == pygame.K_r:
                    # Reset game stats and start game
                    score = 0
                    speed = MIN_SPEED
                    player.x = WIDTH // 2 - CAR_WIDTH // 2
                    player.image = car_image
                    enemy.reset()
                    explosion_pos = None
                    state = STATE_PLAYING
                elif event.key == pygame.K_q:
                    running = False

    # ----------------------------------
    # Game Logic & Updates
    # ----------------------------------
    if state == STATE_PLAYING:
        # Move Player
        player.move()

        # Speed logic based on keys
        keys = pygame.key.get_pressed()

        # Gas (Accelerate)
        if [pygame.K_UP]:
            speed += ACCELERATION
            if speed > MAX_SPEED:
                speed = MAX_SPEED
        else:
            speed -= DECELERATION
            if speed < MIN_SPEED:
                speed = MIN_SPEED

        # Rem (Brake)
        if [pygame.K_DOWN]:
            speed -= 0.4
            if speed < 2:
                speed = 2

        # Update Enemy
        enemy.update(speed)

        # Collision detection
        if player.colliderect(enemy):
            # Calculate collision center
            collision_x = (max(player.left, enemy.left) + min(player.right, enemy.right)) // 2
            collision_y = (max(player.top, enemy.top) + min(player.bottom, enemy.bottom)) // 2
            explosion_pos = (collision_x, collision_y)
            state = STATE_GAME_OVER

        # Update road background scrolling based on current speed
        road_y += speed
        if road_y >= HEIGHT:
            road_y -= HEIGHT

    else:
        # Menus animation: slowly scroll the road in the background (speed = 2)
        road_y += 2
        if road_y >= HEIGHT:
            road_y -= HEIGHT

    # ----------------------------------
    # Rendering
    # ----------------------------------
    draw()
    pygame.display.update()

pygame.quit()
exit()
