#Gabrielle Levy
#2102215
#Battle Arena Game

import pygame
import random
import statistics
import sys
import time

# Initialize Pygame
pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/background.mp3")
pygame.mixer.music.play(-1)  

magic_sound = pygame.mixer.Sound("assets/sounds/magic.mp3")
sword_sound = pygame.mixer.Sound("assets/sounds/sword.mp3")
shield_sound = pygame.mixer.Sound("assets/sounds/shield.mp3")

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena")
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()


background = pygame.image.load("assets/images/Background.png")  
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE = (255,255,255), (0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (128,0,128)

warrior_image = pygame.transform.scale(pygame.image.load("assets/images/warrior.png"), (50, 50))
mage_image = pygame.transform.scale(pygame.image.load("assets/images/mage.png"), (50, 50))
knight_image = pygame.transform.scale(pygame.image.load("assets/images/knight.png"), (50, 50))
orc_image = pygame.transform.scale(pygame.image.load("assets/images/orc.png"), (50, 50))
elf_image = pygame.transform.scale(pygame.image.load("assets/images/elf.png"), (50, 50))
necromancer_image = pygame.transform.scale(pygame.image.load("assets/images/necromancer.png"), (50, 50))

# Fighter class
class Fighter:
    def __init__(self, name, color, atk_range, def_range, special_range, hp=100):
        self.name = name
        self.color = color
        self.original_color = color
        self.hp = hp
        self.atk_range = atk_range
        self.def_range = def_range
        self.special_range = special_range
        self.special_used = False

    def attack(self):
        return random.randint(*self.atk_range)

    def defend(self):
        return random.randint(*self.def_range)

    def special(self):
        if not self.special_used:
            self.special_used = True
            return random.randint(*self.special_range)
        return 0

    def level_up(self):
        self.hp = min(100, self.hp + 20)
        self.atk_range = (self.atk_range[0] + 2, self.atk_range[1] + 2)
        self.def_range = (self.def_range[0] + 1, self.def_range[1] + 1)
        self.special_range = (self.special_range[0] + 5, self.special_range[1] + 5)

class Enemy(Fighter):
    def __init__(self, name, color, atk_range, def_range, special_range, enemy_type, hp=100):
        super().__init__(name, color, atk_range, def_range, special_range, hp)
        self.enemy_type = enemy_type

    def attack(self):
        if self.enemy_type == "Archer":
            return random.randint(self.atk_range[0], self.atk_range[1] + 5)
        elif self.enemy_type == "Mage":
            return random.randint(self.atk_range[0], self.atk_range[1] + 3)
        else:
            return super().attack()

# Draw functions
def draw_text(text, x, y):
    outline = font.render(text, True, BLACK)
    message = font.render(text, True, WHITE)
    screen.blit(outline, (x-1, y))
    screen.blit(outline, (x+1, y))
    screen.blit(outline, (x, y-1))
    screen.blit(outline, (x, y+1))
    screen.blit(message, (x, y))

def draw_fighter(x, y, fighter):
    if hasattr(fighter, "character_type"):
        if fighter.character_type == "Warrior":
            image = warrior_image
        elif fighter.character_type == "Mage":
            image = mage_image
        elif fighter.character_type == "Knight":
            image = knight_image
        else:
            image = warrior_image
    elif hasattr(fighter, "enemy_type"):
        if fighter.enemy_type == "Orc":
            image = orc_image
        elif fighter.enemy_type == "Elf":
            image = elf_image
        elif fighter.enemy_type == "Necromancer":
            image = necromancer_image
        else:
            image = orc_image
    else:
        image = warrior_image

    
    border_thickness = 3
    border_rect = pygame.Rect(x - border_thickness, y - border_thickness,
                              image.get_width() + 2 * border_thickness,
                              image.get_height() + 2 * border_thickness)
    pygame.draw.rect(screen, WHITE, border_rect)

    # Draw the image on top of the white border
    screen.blit(image, (x, y))

def draw_health_bar(x, y, hp, name):
    pygame.draw.rect(screen, BLACK, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, max(0, hp), 10))
    text = font.render(f"{name} HP: {hp}", True, WHITE)
    screen.blit(text, (x, y - 20))

def wait_for_key(keys=["space"], allow_menu=False):
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) in keys:
                    waiting = False
                if allow_menu and event.key == pygame.K_m:  # M for menu
                    return "menu"
    return None

# Projectiles
def projectile_animation(start_x, start_y, end_x, end_y, color):
    projectile = pygame.Rect(start_x, start_y, 10, 5)
    dx = (end_x - start_x) / 20
    dy = (end_y - start_y) / 20
    for _ in range(20):
        screen.blit(background, (0,0))
        draw_fighter(100, 200, player)
        draw_fighter(400, 200, enemy)
        draw_health_bar(100, 180, player.hp, player.name)
        draw_health_bar(400, 180, enemy.hp, enemy.name)
        pygame.draw.rect(screen, color, projectile)
        projectile.x += dx
        projectile.y += dy
        pygame.display.flip()
        clock.tick(60)

# Lucky Guess Heal
def lucky_guess(player):
    target = random.randint(1,5)
    guessed = None
    guessing = True
    while guessing:
        screen.blit(background, (0,0))
        draw_text("Lucky Guess! Pick a number (1-5)", 150, 160)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_5:
                    guessed = event.key - pygame.K_0
                    guessing = False
    if guessed == target:
        heal = 20
        player.hp = min(100, player.hp + heal)
        result = f"Correct! +{heal} HP!"
    else:
        result = f"Wrong! It was {target}. No HP gained."
    screen.blit(background, (0,0))
    draw_text(result, 220, 180)
    draw_text("Press SPACE to continue", 200, 220)
    draw_text("Press M for Menu", 200, 250)
    pygame.display.flip()
    result = wait_for_key(["space"], allow_menu=True)
    return result

# Word scramble mini game
def scramble_word_challenge():
    words = [
        "shield", "armor", "block", "defend", "parry", "sword", "enemy", "battle", "attack", 
        "defense", "strength", "victory", "warrior", "mage", "knight", "wizard", "archer", 
        "sorcery", "elixir", "spell", "monster", "dragon", "giant", "clash", "hero", "villain",
        "sorcerer", "fury", "rage", "power", "charge", "tactics", "summon", "cast", "potion", 
        "crusader", "blade", "axe", "dagger", "lance", "mystic", "darkness", "light", "shuriken", 
        "sorceress", "frost", "flame", "storm", "magic", "heal", "curse", "dungeon", "arena", 
        "shielding", "tournament", "caster", "summoner", "deflector", "phantom", "skeleton", 
        "golem", "medic", "trap", "enchanted", "scout", "berserker", "thunder", "empowered", 
        "battlefield", "archery", "stealth", "assassin", "illusion", "thief", "monk", "warrior", 
        "paladin", "knighthood", "valor", "rage", "pillage", "retribution", "combat", "swordsmanship", 
        "tactical", "healing", "summoning", "resurrect", "mysticism", "relic", "fortress", "cavalry"
    ]
    word = random.choice(words)
    scrambled = ''.join(random.sample(word, len(word)))

    start_time = time.time()
    input_word = ""
    success = False
    while time.time() - start_time < 15:  
        screen.blit(background, (0,0))
        draw_text(f"Unscramble to block: {scrambled}", 140, 160)
        draw_text(f"Type: {input_word}", 140, 200)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_word = input_word[:-1]
                elif event.key == pygame.K_RETURN:
                    if input_word == word:
                        success = True
                    return success
                elif event.key == pygame.K_m:  # M for menu
                    return "menu"
                else:
                    input_word += event.unicode
    return success

# Battle logic
def battle(player, enemy):
    lucky_used = False
    message = "Press A (attack), D (defend), S (special), M (Menu)"
    while player.hp > 0 and enemy.hp > 0:
        screen.blit(background, (0,0))
        draw_fighter(100, 200, player)
        draw_fighter(400, 200, enemy)
        draw_health_bar(100, 180, player.hp, player.name)
        draw_health_bar(400, 180, enemy.hp, enemy.name)
        draw_text(message, 130, 320)
        pygame.display.flip()
        clock.tick(30)

        action = None
        while action is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: action = "attack"
                    elif event.key == pygame.K_d: action = "defend"
                    elif event.key == pygame.K_s: action = "special"
                    elif event.key == pygame.K_m:  # M for menu
                        return "menu"

        symbol = ""
        if action == "attack":
            sword_sound.play()
            dmg = player.attack()
            projectile_animation(120, 220, 400, 220, YELLOW)
            enemy.hp -= dmg
            enemy.color = RED
            message = f"You attack for {dmg}!"
            symbol = "[⚔️]"
        elif action == "defend":
            shield_sound.play()
            block = player.defend()
            scramble_result = scramble_word_challenge()
            if scramble_result == "menu":
                return "menu"
            if scramble_result:
                block += 20
                message = f"Perfect block! +20 bonus block!"
            edmg = max(enemy.attack() - block, 0)
            projectile_animation(420, 220, 100, 220, RED)
            player.hp -= edmg
            player.color = RED
            message = f"You block {block}, enemy hits for {edmg}!"
            symbol = "[🛡️]"
        elif action == "special":
            magic_sound.play()
            sdmg = player.special()
            if sdmg:
                projectile_animation(120, 220, 400, 220, PURPLE)
                enemy.hp -= sdmg
                enemy.color = RED
                message = f"Special attack! {sdmg} damage!"
                symbol = "[💥]"
            else:
                message = "Special already used!"

        screen.blit(background, (0,0))
        draw_fighter(100, 200, player)
        draw_fighter(400, 200, enemy)
        draw_health_bar(100, 180, player.hp, player.name)
        draw_health_bar(400, 180, enemy.hp, enemy.name)
        if symbol:
            x = 120 if action != "defend" else 420
            y = 140
            draw_text(symbol, x, y)
        draw_text(message, 150, 320)
        pygame.display.flip()
        pygame.time.wait(800)

        player.color = player.original_color
        enemy.color = enemy.original_color

        if player.hp <= 50 and not lucky_used:
            result = lucky_guess(player)
            if result == "menu":
                return "menu"
            lucky_used = True

        if enemy.hp > 0 and action != "defend":
            projectile_animation(420, 220, 100, 220, RED)
            scramble_result = scramble_word_challenge()
            if scramble_result == "menu":
                return "menu"
            if scramble_result:
                message = "You blocked perfectly!"
            else:
                edmg = enemy.attack()
                player.hp -= edmg
                player.color = RED
                message = f"Enemy hits for {edmg}!"

            screen.blit(background, (0,0))
            draw_fighter(100, 200, player)
            draw_fighter(400, 200, enemy)
            draw_health_bar(100, 180, player.hp, player.name)
            draw_health_bar(400, 180, enemy.hp, enemy.name)
            draw_text(message, 150, 320)
            pygame.display.flip()
            pygame.time.wait(500)
            player.color = player.original_color

    return player.hp > 0

# Other screens
def show_stats(results):
    screen.blit(background, (0,0))
    wins = results.count(1)
    losses = results.count(0)
    avg = sum(results) / len(results)
    median = statistics.median(results)
    mode = statistics.mode(results)
    draw_text("📊 Game Stats:", 220, 80)
    draw_text(f"Rounds: {len(results)}", 200, 120)
    draw_text(f"Wins: {wins}  Losses: {losses}", 200, 150)
    draw_text(f"Average Score: {avg:.2f}", 200, 180)
    draw_text(f"Median: {median}  Mode: {mode}", 200, 210)
    draw_text("Press SPACE to continue", 200, 260)
    draw_text("Press M for Menu", 200, 290)
    pygame.display.flip()
    result = wait_for_key(["space"], allow_menu=True)
    return result

def select_rounds():
    while True:
        screen.blit(background, (0,0))
        draw_text("Select number of rounds:", 180, 100)
        draw_text("1) One   2) Three   3) Five", 180, 140)
        draw_text("Press M for Menu", 180, 180)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: return 1
                elif event.key == pygame.K_2: return 3
                elif event.key == pygame.K_3: return 5
                elif event.key == pygame.K_m: return "menu"

def select_character():
    while True:
        screen.blit(background, (0,0))
        draw_text("Select Your Character:", 170, 100)
        draw_text("1) Warrior   2) Mage   3) Knight", 170, 140)
        draw_text("Press M for Menu", 170, 180)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    f = Fighter("Warrior", YELLOW, (15, 25), (5, 12), (30, 40))
                    f.character_type = "Warrior"
                    return f
                elif event.key == pygame.K_2:
                    f = Fighter("Mage", PURPLE, (10, 20), (4, 8), (35, 50))
                    f.character_type = "Mage"
                    return f
                elif event.key == pygame.K_3:
                    f = Fighter("Knight", BLUE, (12, 18), (8, 14), (20, 30))
                    f.character_type = "Knight"
                    return f
                elif event.key == pygame.K_m:
                    return "menu"

def show_storyline(character):
    screen.blit(background, (0, 0))
    
    if character.name == "Warrior":
        storyline = (
            "In the land of Eldoria, the Warrior sets out on a journey to defeat the Dark Legion. "
            "With his sword raised high, he seeks to restore peace to the realm. The battle ahead is fierce, "
            "but the Warrior is determined to face the greatest challenges, wielding strength and courage as his allies."
        )
    elif character.name == "Mage":
        storyline = (
            "In the ancient citadel of Arcanis, the Mage uncovers the lost secrets of the magical arts. "
            "Armed with spells of fire and ice, the Mage must overcome the forces of darkness that threaten the land. "
            "With each battle, the Mage grows stronger, unlocking new powers and uncovering the truth of their destiny."
        )
    elif character.name == "Knight":
        storyline = (
            "The Knight, a protector of the kingdom, embarks on a quest to reclaim the Sacred Relic stolen by a ruthless foe. "
            "With honor and duty in his heart, the Knight faces monsters and adversaries on a journey to restore peace. "
            "Every battle won brings him closer to his goal, but the road ahead is fraught with danger."
        )
    
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            width, _ = font.size(test_line)
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
                
        if current_line:
            lines.append(current_line)
        return lines

    max_width = WIDTH - 40  
    lines = wrap_text(storyline, font, max_width)
    
    y_offset = 100
    for line in lines:
        draw_text(line, 20, y_offset)
        y_offset += 30  

    draw_text("Prepare yourself for battle!", 180, y_offset + 20)
    draw_text("Press SPACE to continue", 180, y_offset + 50)
    draw_text("Press M for Menu", 180, y_offset + 80)
    pygame.display.flip()
    result = wait_for_key(["space"], allow_menu=True)
    return result

# Main function 
def mains():
    global player, enemy
    running = True
    while running:
        player = select_character()
        if player == "menu":
            continue
        
        rounds = select_rounds()
        if rounds == "menu":
            continue
        
        result = show_storyline(player)
        if result == "menu":
            continue
 
        results = []
        for r in range(rounds):
            enemy_type = random.choice(["Warrior", "Archer", "Mage"])
            if enemy_type == "Warrior":
                enemy = Enemy("Orc", RED, (12, 22), (6, 10), (0, 0), "Orc")
            elif enemy_type == "Archer":
                enemy = Enemy("Elf", GREEN, (10, 20), (5, 8), (0, 0), "Elf")
            else:
                enemy = Enemy("Necromancer", PURPLE, (8, 15), (5, 10), (10, 30), "Necromancer")
            
            result = battle(player, enemy)
            if result == "menu":
                break
            
            results.append(1 if result else 0)
            screen.blit(background, (0, 0))
            draw_text("You Won!" if result else "You Lost!", 250, 180)
            draw_text("Press SPACE to continue", 200, 220)
            draw_text("Press M for Menu", 200, 250)
            pygame.display.flip()
            
            menu_choice = wait_for_key(["space"], allow_menu=True)
            if menu_choice == "menu":
                break
            
            player.level_up()
        
        if len(results) > 0:
            result = show_stats(results)
            if result == "menu":
                continue

        # Play again?
        asking = True
        while asking:
            screen.blit(background, (0, 0))
            draw_text("Play again? Y/N", 220, 180)
            draw_text("Press M for Menu", 220, 210)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        asking = False
                    elif event.key == pygame.K_n:
                        asking = False
                        running = False
                    elif event.key == pygame.K_m:
                        asking = False
                        break

    pygame.quit()

def battle_arena_start():
    mains()

if __name__ == "__main__":
    mains()

