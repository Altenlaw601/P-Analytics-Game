#Adrian
import pygame
import random
import sys
import time

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

# Load Images
player_img = pygame.image.load("assets/images/player.png")
enemy_img = pygame.image.load("assets/images/enemy.png")
bullet_img = pygame.image.load("assets/images/bullet.png")
boss_img = pygame.image.load("assets/images/boss.png")
background_img = pygame.image.load("assets/images/background.jpg")

# Resize images
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
boss_img = pygame.transform.scale(boss_img, (150, 150))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Load Sounds
shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.mp3")
explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
dice_roll_sound = pygame.mixer.Sound("assets/sounds/dice_roll.wav")
pygame.mixer.music.load("assets/sounds/background_music.mp3")
pygame.mixer.music.play(-1)

# Player setup
player = pygame.Rect(WIDTH // 2, HEIGHT - 60, 50, 50)
player_speed = 5
bullets = []
bullet_speed = 7
bullet_cooldown = 0.3
last_shot = 0
player_health = 5

# Enemy setup
enemies = []
enemy_speed = 2

# Boss setup
boss = None
boss_health = 30
boss_speed = 3
boss_direction = 1
boss_spawned = False
boss_attack_timer = 0

# Score
score = 0
next_bonus_score = 500

# Upgrades
upgrades = {"speed": 0, "weapon": 1, "shield": 0}

def spawn_enemy():
    x = random.randint(0, WIDTH - 50)
    y = random.randint(-100, -40)
    return pygame.Rect(x, y, 50, 50)

def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, 100 * (health / max_health), 10))

def roll_dice():
    dice_roll_sound.play()
    return random.randint(1, 6), random.randint(1, 6)

def handle_dice_roll():
    d1, d2 = roll_dice()
    total = d1 + d2
    reward = ""
    if total == 7:
        reward = "JACKPOT! Mega Upgrade!"
        upgrades["speed"] += 2
        upgrades["weapon"] += 1
    elif total in [5, 6, 8, 9]:
        reward = "Nice! Medium Upgrade!"
        upgrades["speed"] += 1
        upgrades["shield"] += 1
    else:
        reward = "Basic Bonus Collected."
        upgrades["speed"] += 1
    return d1, d2, total, reward

def check_collisions():
    global enemies, bullets, score, boss_health, boss, player_health
    for enemy in enemies[:]:
        if player.colliderect(enemy):
            enemies.remove(enemy)
            player_health -= 1
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                bullets.remove(bullet)
                if enemy in enemies:
                    enemies.remove(enemy)
                explosion_sound.play()
                score += 10

    if boss:
        for bullet in bullets[:]:
            if boss.colliderect(bullet):
                bullets.remove(bullet)
                boss_health -= 1
                score += 20
                explosion_sound.play()
        if boss_health <= 0:
            boss = None


def main():
    global boss, boss_health, boss_direction, boss_spawned, boss_attack_timer
    global bullets, last_shot, enemies, score, next_bonus_score
    global player_health

    running = True
    last_dice_time = time.time()

    while running:
        screen.blit(background_img, (0, 0))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed + upgrades["speed"]
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed + upgrades["speed"]

        # Shooting
        if keys[pygame.K_SPACE] and time.time() - last_shot > bullet_cooldown:
            for i in range(upgrades["weapon"]):
                offset = (i - upgrades["weapon"] // 2) * 10
                bullet = pygame.Rect(player.centerx + offset, player.top, 10, 20)
                bullets.append(bullet)
            shoot_sound.play()
            last_shot = time.time()

        # Bullet movement
        for bullet in bullets:
            bullet.y -= bullet_speed
        bullets = [b for b in bullets if b.y > 0]

        # Spawn enemies
        if random.random() < 0.02 and len(enemies) < 5:
            enemies.append(spawn_enemy())

        for enemy in enemies:
            enemy.y += enemy_speed
        enemies = [e for e in enemies if e.y < HEIGHT]

        # Boss logic
        if score >= 1000 and not boss_spawned:
            boss = pygame.Rect(WIDTH//2 - 75, 50, 150, 150)
            boss_health = 30
            boss_spawned = True

        if boss:
            boss.x += boss_direction * boss_speed
            if boss.left <= 0 or boss.right >= WIDTH:
                boss_direction *= -1
            boss_attack_timer += 1
            if boss_attack_timer > 60:
                boss_attack_timer = 0
                if random.random() < 0.5:
                    enemies.append(pygame.Rect(boss.centerx - 25, boss.bottom, 50, 50))

        # Check collisions
        check_collisions()

        # Lucky Seven Bonus every 500 pts
        if score >= next_bonus_score:
            handle_dice_roll()
            next_bonus_score += 500

        # Drawing
        screen.blit(player_img, player)
        for bullet in bullets:
            screen.blit(bullet_img, bullet)
        for enemy in enemies:
            screen.blit(enemy_img, enemy)
        if boss:
            screen.blit(boss_img, boss)
            draw_health_bar(boss.x, boss.y - 15, boss_health, 30)

        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Health: {player_health}", 10, 40)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
