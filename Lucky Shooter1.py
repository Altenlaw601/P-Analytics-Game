# Adrian lawrence
# 1903014
import pygame
import random
import sys
import time
import statistics

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Fortune")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
BOSS_LASER_COLOR = (255, 100, 100)
PURPLE = (128, 0, 128)

# Utility functions for loading
def load_image(path, size=None):
    try:
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        return pygame.Surface((50, 50))  # fallback

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Error loading sound {path}: {e}")
        return None

# Load assets
player_img = load_image("assets/images/player.png", (50, 50))
enemy_img = load_image("assets/images/enemy.png", (50, 50))
bullet_img = load_image("assets/images/bullet.png", (5, 10))
boss_img = load_image("assets/images/enemy.png", (100, 100))
background_img = load_image("assets/images/background.jpg", (WIDTH, HEIGHT))

# Load dice images
dice_images = [load_image(f"assets/images/dice_{i}.png", (60, 60)) for i in range(1, 7)]

shoot_sound = load_sound("assets/sounds/shoot.mp3")
explosion_sound = load_sound("assets/sounds/explosion.wav")
dice_roll_sound = load_sound("assets/sounds/dice_roll.wav")
try:
    pygame.mixer.music.load("assets/sounds/background_music.mp3")
    pygame.mixer.music.play(-1)
except:
    print("Background music failed to load.")

# Game constants
player_speed = 5
bullet_speed = 7
bullet_cooldown = 0.3
boss_speed = 3
boss_attack_cooldown = 1.5

# Game states
MENU = "menu"
SPACE_MODE = "space"
DICE_MODE = "dice"
GAME_OVER = "over"
VICTORY = "victory"

def reset_game():
    global player, bullets, enemies, boss_bullets, player_health, score, boss, boss_health
    global boss_direction, last_bullet_time, last_boss_attack_time, power_up_active
    global last_dice_draw, dice_result, dice_timer_start, damage_values
    
    player = pygame.Rect(WIDTH // 2, HEIGHT - 60, 50, 50)
    bullets = []
    enemies = []
    boss_bullets = []
    player_health = 100
    score = 0
    boss = None
    boss_health = 100
    boss_direction = 1
    last_bullet_time = 0
    last_boss_attack_time = 0
    power_up_active = False
    last_dice_draw = 0
    dice_result = None
    dice_timer_start = 0
    damage_values = []

# Initialize game
reset_game()

# Fonts
font = pygame.font.SysFont("arial", 32)
title_font = pygame.font.SysFont("arial", 64, bold=True)

# Clock
clock = pygame.time.Clock()
game_mode = MENU

def draw_text(text, x, y, color=WHITE, font_size=32, center=True):
    font_obj = pygame.font.SysFont("arial", font_size)
    render = font_obj.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)

def draw_player():
    if power_up_active:
        pygame.draw.ellipse(screen, YELLOW, player.inflate(20, 20), 3)
    screen.blit(player_img, player)

def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, 100 * (health / max_health), 10))

def spawn_enemy():
    x = random.randint(0, WIDTH - 40)
    return pygame.Rect(x, 0, 40, 40)

def handle_dice_roll():
    global power_up_active, player_health
    if dice_roll_sound:
        dice_roll_sound.play()
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2
    if total == 7:
        power_up_active = True
        player_health = min(player_health + 30, 100)
        return d1, d2, total, "Lucky Seven! +30 Health + Shield!"
    else:
        return d1, d2, total, "No bonus."

def damage_player(dmg):
    global player_health, game_mode, power_up_active, damage_values
    if power_up_active:
        power_up_active = False
        return
    player_health -= dmg
    damage_values.append(dmg)
    if player_health <= 0:
        game_mode = GAME_OVER

def show_stats():
    if damage_values:
        stats_texts = [
            f"Total Hits Taken: {len(damage_values)}",
            f"Mean Damage: {statistics.mean(damage_values):.1f}",
            f"Max Damage: {max(damage_values)}",
            f"Min Damage: {min(damage_values)}",
            f"Damage Range: {max(damage_values) - min(damage_values)}",
        ]
        for i, text in enumerate(stats_texts):
            draw_text(text, WIDTH // 2, 400 + i * 30, font_size=24)

def check_collisions():
    global enemies, bullets, score, boss_health, game_mode, boss, boss_bullets

    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if enemy.colliderect(bullet['rect']):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 10
                if explosion_sound:
                    explosion_sound.play()
                break
        if enemy.colliderect(player):
            enemies.remove(enemy)
            damage_player(20)

    if boss:
        for bullet in bullets[:]:
            if boss and boss.colliderect(bullet['rect']):
                bullets.remove(bullet)
                boss_health -= 10 if power_up_active else 5
                if explosion_sound:
                    explosion_sound.play()
                if boss_health <= 0:
                    score += 100
                    boss = None
                    game_mode = VICTORY
                    return

        for bb in boss_bullets[:]:
            if player.colliderect(bb):
                boss_bullets.remove(bb)
                damage_player(15)

def draw_menu():
    screen.blit(background_img, (0, 0))
    draw_text("GALACTIC FORTUNE", WIDTH // 2, 150, PURPLE, 64)
    draw_text("Press SPACE to Start", WIDTH // 2, 300, YELLOW, 36)
    draw_text("Press ESC to Exit", WIDTH // 2, 350, WHITE, 36)
    draw_text("Arrow Keys to Move", WIDTH // 2, 420, CYAN, 24)
    draw_text("SPACE to Shoot", WIDTH // 2, 450, CYAN, 24)
    draw_text("Roll 7 for bonus power-ups!", WIDTH // 2, 500, GREEN, 24)

def main():
    global bullets, last_bullet_time, enemies, score, boss, boss_health, boss_direction
    global last_boss_attack_time, game_mode, dice_result, dice_timer_start, power_up_active
    global last_dice_draw

    running = True
    while running:
        screen.blit(background_img, (0, 0))
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_mode in [SPACE_MODE, DICE_MODE, GAME_OVER, VICTORY]:
                        game_mode = MENU
                        reset_game()
                    elif game_mode == MENU:
                        running = False

        if game_mode == MENU:
            draw_menu()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                game_mode = SPACE_MODE

        elif game_mode == SPACE_MODE:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += player_speed

            if keys[pygame.K_SPACE] and current_time - last_bullet_time > bullet_cooldown:
                bullet_rect = pygame.Rect(player.centerx - 5, player.top - 15, 10, 25) if power_up_active else pygame.Rect(player.centerx - 2, player.top - 10, 4, 20)
                color = RED if power_up_active else CYAN
                bullets.append({'rect': bullet_rect, 'color': color})
                if shoot_sound:
                    shoot_sound.play()
                last_bullet_time = current_time

            for bullet in bullets:
                bullet['rect'].y -= bullet_speed
            bullets = [b for b in bullets if b['rect'].y > 0]

            if random.random() < 0.02:
                enemies.append(spawn_enemy())
            for enemy in enemies:
                enemy.y += 3
            enemies = [e for e in enemies if e.y < HEIGHT]

            if score >= 1000:
                if not boss:
                    boss = pygame.Rect(WIDTH // 2 - 50, 50, 100, 100)
                    boss_health = 100
                    last_boss_attack_time = current_time
                else:
                    boss.x += boss_direction * boss_speed
                    if boss.left <= 0 or boss.right >= WIDTH:
                        boss_direction *= -1
                    if current_time - last_boss_attack_time > boss_attack_cooldown:
                        laser = pygame.Rect(boss.centerx - 5, boss.bottom, 10, 25)
                        boss_bullets.append(laser)
                        last_boss_attack_time = current_time



            draw_player()
            for bullet in bullets:
                pygame.draw.rect(screen, bullet['color'], bullet['rect'])
            for enemy in enemies:
                screen.blit(enemy_img, enemy)
            for bb in boss_bullets:
                pygame.draw.rect(screen, BOSS_LASER_COLOR, bb)

            if boss:
                screen.blit(boss_img, boss)
                draw_health_bar(boss.x, boss.y - 10, boss_health, 100)

            draw_text(f"Score: {score}", 20, 20, color=YELLOW, center=False, font_size=48)
            draw_health_bar(WIDTH - 120, 20, player_health, 100)
            draw_text("ESC: Menu", WIDTH - 80, HEIGHT - 20, WHITE, 20)

            check_collisions()

            if score >= last_dice_draw + 250:
                game_mode = DICE_MODE
                dice_result = handle_dice_roll()
                last_dice_draw = score
                dice_timer_start = time.time()

        elif game_mode == DICE_MODE:
            draw_text("🎲 LUCKY SEVEN BONUS 🎲", WIDTH // 2, 80, font_size=48)
            if dice_result:
                d1, d2, total, reward = dice_result
                screen.blit(dice_images[d1 - 1], (WIDTH // 2 - 80, 150))
                screen.blit(dice_images[d2 - 1], (WIDTH // 2 + 20, 150))
                draw_text(f"{d1} + {d2} = {total}", WIDTH // 2, 230)
                draw_text(reward, WIDTH // 2, 300)
                draw_text("Returning to game...", WIDTH // 2, 450)
            if time.time() - dice_timer_start > 3:
                game_mode = SPACE_MODE

        elif game_mode == GAME_OVER:
            draw_text("💀 GAME OVER 💀", WIDTH // 2, HEIGHT // 2, font_size=64)
            draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2 + 50, font_size=48)
            draw_text("Press ESC to return to Menu", WIDTH // 2, HEIGHT - 50, WHITE, 24)
            show_stats()

        elif game_mode == VICTORY:
            draw_text("🎉 YOU'VE CONQUERED THE GALAXY! 🎉", WIDTH // 2, HEIGHT // 2, font_size=48)
            draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2 + 50, font_size=36)
            draw_text("Press ESC to return to Menu", WIDTH // 2, HEIGHT - 50, WHITE, 24)
            show_stats()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
