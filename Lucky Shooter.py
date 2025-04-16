import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Fortune")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load assets
player_img = pygame.transform.scale(pygame.image.load("assets/images/player.png"), (50, 50))
enemy_img = pygame.transform.scale(pygame.image.load("assets/images/enemy.png"), (50, 50))
bullet_img = pygame.transform.scale(pygame.image.load("assets/images/bullet.png"), (5, 10))
boss_img = pygame.transform.scale(pygame.image.load("assets/images/enemy.png"), (100, 100))
background_img = pygame.transform.scale(pygame.image.load("assets/images/background.jpg"), (WIDTH, HEIGHT))

# Sounds
shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.mp3")
explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
dice_roll_sound = pygame.mixer.Sound("assets/sounds/dice_roll.wav")
pygame.mixer.music.load("assets/sounds/background_music.mp3")
pygame.mixer.music.play(-1)

# Variables
player = pygame.Rect(WIDTH//2, HEIGHT - 60, 50, 50)
player_speed = 5
player_health = 100

bullets = []
bullet_speed = 7
bullet_cooldown = 0.3
last_bullet_time = 0

enemies = []
enemy_speed = 2

score = 0
last_dice_draw = 0

boss = None
boss_health = 100
boss_direction = 1
boss_speed = 2
boss_bullets = []
boss_attack_cooldown = 2
last_boss_attack_time = 0

space_start_time = time.time()

# Game states
SPACE_MODE = "space"
DICE_MODE = "dice"
VICTORY = "victory"
GAME_OVER = "game_over"
game_mode = SPACE_MODE
dice_result = None

def draw_text(text, x, y, color=WHITE, center=True):
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.center = (x, y) if center else rect.topleft
    screen.blit(img, rect)

def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, max(0, 100 * health // max_health), 10))

def spawn_enemy():
    return pygame.Rect(random.randint(0, WIDTH - 50), random.randint(-100, -40), 50, 50)

def roll_dice():
    dice_roll_sound.play()
    return random.randint(1, 6), random.randint(1, 6)

def handle_dice_roll():
    global player_health
    d1, d2 = roll_dice()
    total = d1 + d2
    reward = ""

    if total == 7:
        reward = "LUCKY SEVEN! +30 Health"
        player_health = min(player_health + 30, 100)
    elif total in [5, 6, 8, 9]:
        reward = "Good Roll! +20 Health"
        player_health = min(player_health + 20, 100)
    else:
        reward = "Basic Roll. +10 Health"
        player_health = min(player_health + 10, 100)

    return d1, d2, total, reward

def check_collisions():
    global enemies, bullets, score, boss_health, game_mode

    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 10
                explosion_sound.play()
                break

        if enemy.colliderect(player):
            enemies.remove(enemy)
            damage_player(20)

    if boss:
        for bullet in bullets[:]:
            if boss.colliderect(bullet):
                bullets.remove(bullet)
                boss_health -= 5
                explosion_sound.play()
                if boss_health <= 0:
                    game_mode = VICTORY

        for bb in boss_bullets[:]:
            if player.colliderect(bb):
                boss_bullets.remove(bb)
                damage_player(15)

def damage_player(dmg):
    global player_health, game_mode
    player_health -= dmg
    if player_health <= 0:
        game_mode = GAME_OVER

def main():
    global bullets, last_bullet_time, enemies, score, boss, boss_health, boss_direction, last_dice_draw
    global game_mode, dice_result, boss_bullets, last_boss_attack_time

    running = True
    while running:
        screen.blit(background_img, (0, 0))
        keys = pygame.key.get_pressed()
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_mode == SPACE_MODE:
            # Movement
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += player_speed

            # Shooting
            if keys[pygame.K_SPACE] and current_time - last_bullet_time > bullet_cooldown:
                bullet = pygame.Rect(player.centerx, player.top, 5, 10)
                bullets.append(bullet)
                shoot_sound.play()
                last_bullet_time = current_time

            # Bullet movement
            for bullet in bullets:
                bullet.y -= bullet_speed
            bullets = [b for b in bullets if b.y > 0]

            # Enemy logic
            if random.random() < 0.02:
                enemies.append(spawn_enemy())

            for enemy in enemies:
                enemy.y += enemy_speed
            enemies = [e for e in enemies if e.y < HEIGHT]

            # Boss logic
            if score >= 1000:
                if not boss:
                    boss = pygame.Rect(WIDTH // 2 - 50, 50, 100, 100)
                    boss_health = 100
                    last_boss_attack_time = current_time
                else:
                    boss.x += boss_direction * boss_speed
                    if boss.left <= 0 or boss.right >= WIDTH:
                        boss_direction *= -1

                    # Boss attack
                    if current_time - last_boss_attack_time > boss_attack_cooldown:
                        bullet = pygame.Rect(boss.centerx, boss.bottom, 5, 10)
                        boss_bullets.append(bullet)
                        last_boss_attack_time = current_time

            for bb in boss_bullets:
                bb.y += 5
            boss_bullets = [b for b in boss_bullets if b.y < HEIGHT]

            # Draw
            screen.blit(player_img, player)
            for bullet in bullets:
                screen.blit(bullet_img, bullet)
            for enemy in enemies:
                screen.blit(enemy_img, enemy)
            for bb in boss_bullets:
                screen.blit(bullet_img, bb)
            if boss:
                screen.blit(boss_img, boss)
                draw_health_bar(boss.x, boss.y - 10, boss_health, 100)

            draw_text(f"Score: {score}", 70, 20, WHITE, center=False)
            draw_health_bar(WIDTH - 120, 20, player_health, 100)

            check_collisions()

            # Lucky draw every 500 pts
            if score >= last_dice_draw + 500:
                game_mode = DICE_MODE
                dice_result = handle_dice_roll()
                last_dice_draw = score
                dice_timer_start = time.time()

        elif game_mode == DICE_MODE:
            draw_text("🎲 LUCKY SEVEN BONUS 🎲", WIDTH // 2, 80)
            if dice_result:
                d1, d2, total, reward = dice_result
                draw_text(f"You rolled: {d1} + {d2} = {total}", WIDTH // 2, 200)
                draw_text(reward, WIDTH // 2, 300)
                draw_text("Returning to game...", WIDTH // 2, 450)
            if time.time() - dice_timer_start > 3:
                game_mode = SPACE_MODE

        elif game_mode == GAME_OVER:
            draw_text("💀 GAME OVER 💀", WIDTH // 2, HEIGHT // 2)
            draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2 + 50)
        
        elif game_mode == VICTORY:
            draw_text("🎉 YOU'VE CONQUERED THE GALAXY! 🎉", WIDTH // 2, HEIGHT // 2)
            draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2 + 50)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

main()
