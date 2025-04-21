#Adrian Lawrence
#Gabrielle Levy
#Flloyd Mullings
#Javanve Roberts


import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import random
import statistics
import time
import sys
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from itertools import cycle
from collections import Counter
from abc import ABC, abstractmethod
import ctypes  # For Windows focus handling


class GameAnalytics:
    def __init__(self):
        self.scores = {}
        self.game_plays = {}
    
    def record_score(self, game_name, score):
        if game_name not in self.scores:
            self.scores[game_name] = []
            self.game_plays[game_name] = 0
        self.scores[game_name].append(score)
        self.game_plays[game_name] += 1
    
    def get_stats(self, game_name):
        if game_name not in self.scores or not self.scores[game_name]:
            return None
        
        scores = self.scores[game_name]
        stats = {
            'count': len(scores),
            'total': sum(scores),
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'mode': statistics.mode(scores) if scores else 0,
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
            'range': max(scores) - min(scores) if scores else 0,
            'last': scores[-1] if scores else 0,
            'plays': self.game_plays[game_name]
        }
        return stats


class BaseGame(ABC):
    def __init__(self, analytics):
        self.analytics = analytics
        self.game_name = self.__class__.__name__
    
    @abstractmethod
    def play(self):
        pass
    
    def record_score(self, score):
        self.analytics.record_score(self.game_name, score)
    
    def roll_dice(self, sides=6, num_dice=1):
        return [random.randint(1, sides) for _ in range(num_dice)] if num_dice > 1 else random.randint(1, sides)
    
    def get_random_number(self, min_val=1, max_val=100):
        return random.randint(min_val, max_val)
    
    def display_stats(self):
        stats = self.analytics.get_stats(self.game_name)
        if stats:
            print(f"\n--- {self.game_name} Statistics ---")
            print(f"Plays: {stats['plays']}")
            print(f"Last Score: {stats['last']}")
            print(f"Average Score: {stats['mean']:.2f}")
            print(f"High Score: {stats['max']}")
            print(f"Low Score: {stats['min']}")
            print(f"Score Range: {stats['range']}")
            print(f"Median Score: {stats['median']}")
            print(f"Most Common Score: {stats['mode']}")

# GalacticFortune Game
class GalacticFortune(BaseGame):
    def __init__(self, analytics):
        super().__init__(analytics)
        self.game_name = "Galactic Fortune"
    
    def play(self):
        pygame.init()
        WIDTH, HEIGHT = 800, 600
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Galactic Fortune")

        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        CYAN = (0, 255, 255)
        YELLOW = (255, 255, 0)
        BOSS_LASER_COLOR = (255, 100, 100)

        def load_image(path, size=None):
            try:
                img = pygame.image.load(path)
                if size:
                    img = pygame.transform.scale(img, size)
                return img
            except pygame.error as e:
                print(f"Error loading image {path}: {e}")
                return pygame.Surface((50, 50))

        def load_sound(path):
            try:
                return pygame.mixer.Sound(path)
            except pygame.error as e:
                print(f"Error loading sound {path}: {e}")
                return None

        player_img = load_image("assets/images/player.png", (50, 50))
        enemy_img = load_image("assets/images/enemy.png", (50, 50))
        bullet_img = load_image("assets/images/bullet.png", (5, 10))
        boss_img = load_image("assets/images/enemy.png", (100, 100))
        background_img = load_image("assets/images/background.jpg", (WIDTH, HEIGHT))

        dice_images = [load_image(f"assets/images/dice_{i}.png", (60, 60)) for i in range(1, 7)]

        shoot_sound = load_sound("assets/sounds/shoot.mp3")
        explosion_sound = load_sound("assets/sounds/explosion.wav")
        dice_roll_sound = load_sound("assets/sounds/dice_roll.wav")
        try:
            pygame.mixer.music.load("assets/sounds/background_music.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Background music failed to load.")

        player = pygame.Rect(WIDTH // 2, HEIGHT - 60, 50, 50)
        player_speed = 5
        bullet_speed = 7
        bullet_cooldown = 0.3
        last_bullet_time = 0

        bullets = []
        enemies = []
        score = 0
        player_health = 100
        boss = None
        boss_health = 100
        boss_direction = 1
        boss_speed = 3
        boss_bullets = []
        boss_attack_cooldown = 1.5
        last_boss_attack_time = 0

        power_up_active = False
        last_dice_draw = 0
        dice_result = None
        dice_timer_start = 0
        damage_values = []

        font = pygame.font.SysFont("arial", 32)


        clock = pygame.time.Clock()


        SPACE_MODE = "space"
        DICE_MODE = "dice"
        GAME_OVER = "over"
        VICTORY = "victory"
        game_mode = SPACE_MODE

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
            nonlocal power_up_active, player_health, dice_result, dice_timer_start
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
            nonlocal player_health, game_mode, power_up_active, damage_values
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
            nonlocal enemies, bullets, score, boss_health, game_mode, boss, boss_bullets

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

        running = True
        while running:
            screen.blit(background_img, (0, 0))
            keys = pygame.key.get_pressed()
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return score  # Changed: Just return score without quitting pygame

            if game_mode == SPACE_MODE:
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

                for bb in boss_bullets:
                    bb.y += 5
                boss_bullets = [b for b in boss_bullets if b.y < HEIGHT]

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
                show_stats()
                
                draw_text("Press ESC to return to menu", WIDTH // 2, HEIGHT - 50, font_size=24)
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                waiting = False
                                running = False
                return score

            elif game_mode == VICTORY:
                draw_text("🎉 YOU'VE CONQUERED THE GALAXY! 🎉", WIDTH // 2, HEIGHT // 2, font_size=48)
                draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2 + 50, font_size=36)
                show_stats()
                
                draw_text("Press ESC to return to menu", WIDTH // 2, HEIGHT - 50, font_size=24)
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                waiting = False
                                running = False
                return score

            pygame.display.flip()
            clock.tick(60)

        return score

# TicTacToe Game
class Player:
    def __init__(self, label, color):
        self.label = label
        self.color = color
        self.wins = 0
        self.name = f"Player {label}"

class Move:
    def __init__(self, row, col, label=""):
        self.row = row
        self.col = col
        self.label = label

class TicTacToeGame:
    def __init__(self, players=None, board_size=3):
        if players is None:
            players = [Player("X", "red"), Player("O", "green")]
        self.original_players = players
        self.players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self.players)
        self._has_winner = False
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def reset_game(self):
        self.players = cycle(self.original_players)
        self.current_player = next(self.players)
        self._has_winner = False
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                for player in self.original_players:
                    if player.label == move.label:
                        player.wins += 1
                        break
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (move.label for row in self._current_moves for move in row)
        return no_winner and all(played_moves)

    def toggle_player(self):
        self.current_player = next(self.players)

    def ai_move(self):
        for row in range(3):
            for col in range(3):
                if self._current_moves[row][col].label == "":
                    self._current_moves[row][col].label = "O"
                    if self.has_winner():
                        self._current_moves[row][col].label = ""
                        return Move(row, col, "O")
                    self._current_moves[row][col].label = ""
        
        for row in range(3):
            for col in range(3):
                if self._current_moves[row][col].label == "":
                    self._current_moves[row][col].label = "X"
                    if self.has_winner():
                        self._current_moves[row][col].label = ""
                        return Move(row, col, "O")
                    self._current_moves[row][col].label = ""
        
        if self._current_moves[1][1].label == "":
            return Move(1, 1, "O")
        
        corners = [(0,0), (0,2), (2,0), (2,2)]
        random.shuffle(corners)
        for row, col in corners:
            if self._current_moves[row][col].label == "":
                return Move(row, col, "O")
        
        empty_cells = [
            (row, col)
            for row in range(3)
            for col in range(3)
            if self._current_moves[row][col].label == ""
        ]
        if empty_cells:
            row, col = random.choice(empty_cells)
            return Move(row, col, "O")
        
        return None

class Leaderboard:
    def __init__(self, filename='leaderboard.json'):
        self.filename = filename
        self.leaderboard = []
        self.load_leaderboard()
        
    def load_leaderboard(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.leaderboard = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.leaderboard = []
            
    def save_leaderboard(self):
        with open(self.filename, 'w') as f:
            json.dump(self.leaderboard, f, indent=2)
            
    def add_score(self, player_name, score):
        self.leaderboard.append({
            'name': player_name,
            'score': score
        })
        self.leaderboard.sort(key=lambda x: x['score'], reverse=True)
        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()
        
    def get_leaderboard(self):
        return self.leaderboard

class TicTacToe(BaseGame):
    def __init__(self, analytics):
        super().__init__(analytics)
        self.game_name = "Tic-Tac-Toe"
        self.total_score = 0
    
    def play(self):
        root = tk.Tk()
        root.withdraw()
        
        home_page = tk.Toplevel(root)
        home_page.title("Tic-Tac-Toe - Main Menu")
        home_page.geometry("400x300")
        home_page.resizable(False, False)
        
        container = tk.Frame(home_page, bg="lightblue")
        container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(container, 
                text="Tic-Tac-Toe", 
                font=("Arial", 24, 'bold'),
                bg="lightblue").pack(pady=10)
        
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, 
                text="Player vs AI", 
                command=lambda: self.start_game(home_page, True, root),
                width=15,
                font=("Arial", 12)).pack(pady=5)
        
        tk.Button(btn_frame, 
                text="Player vs Player", 
                command=lambda: self.start_game(home_page, False, root),
                width=15,
                font=("Arial", 12)).pack(pady=5)
        
        tk.Button(btn_frame, 
                text="Exit to Main Menu", 
                command=lambda: self.return_to_main_menu(home_page, root),
                width=15,
                font=("Arial", 12),
                bg="lightgray",
                activebackground="gray",
                highlightbackground="lightblue").pack(pady=5)
        
        home_page.protocol("WM_DELETE_WINDOW", lambda: self.return_to_main_menu(home_page, root))
        
        self.root = root
        self.home_page = home_page
        
        root.mainloop()
        
        return self.total_score
    
    def start_game(self, home_page, ai_mode, root):
        home_page.withdraw()
        game_window = tk.Toplevel(root)
        TicTacToeUI(game_window, home_page, ai_mode, self)
    
    def return_to_main_menu(self, window, root):
        window.destroy()
        root.quit()

class TicTacToeUI:
    def __init__(self, game_window, home_page, ai_mode, game_instance):
        self.root = game_window
        self.home_page = home_page
        self.ai_mode = ai_mode
        self.game_instance = game_instance
        self.leaderboard = Leaderboard()
        
        self.target_score = 5
        self.series_scores = {"Player X": 0, "Player O": 0}
        self.ties = 0
        self.total_score = 0
        
        self._game = TicTacToeGame()
        self._buttons = {}
        
        self._setup_ui()
        self._get_player_names()
        self._setup_target_score()
        
        self._update_display(f"{self._game.current_player.name}'s turn ({self._game.current_player.label})")
        
        if self.ai_mode and self._game.current_player.label == "O":
            self.root.after(300, self.ai_move)

    def _setup_ui(self):
        self.root.configure(bg="lightyellow")
        
        top_bar = tk.Frame(self.root, bg="lightyellow")
        top_bar.pack(fill=tk.X, padx=10, pady=5)
        
        if self.ai_mode:
            tk.Button(
                top_bar,
                text="Leaderboard",
                command=self.show_leaderboard,
                font=("Arial", 10)
            ).pack(side=tk.RIGHT)
        
        self.series_display = tk.Label(
            self.root,
            text=f"First to {self.target_score} wins",
            font=("Arial", 12),
            pady=5,
            bg="lightyellow"
        )
        self.series_display.pack()
        
        self.display = tk.Label(
            self.root,
            text="Ready?",
            font=("Arial", 16, "bold"),
            pady=10,
            bg="lightyellow"
        )
        self.display.pack()
        
        self.score_display = tk.Label(
            self.root,
            text="",
            font=("Arial", 12),
            pady=5,
            bg="lightyellow"
        )
        self.score_display.pack()
        
        grid_frame = tk.Frame(self.root, bg="lightyellow")
        grid_frame.pack(pady=10)
        
        for row in range(3):
            for col in range(3):
                button = tk.Button(
                    grid_frame,
                    text="",
                    font=("Arial", 36, "bold"),
                    fg="black",
                    width=3,
                    height=1,
                    highlightbackground="lightblue",
                    command=lambda r=row, c=col: self.play(r, c)
                )
                self._buttons[(row, col)] = button
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_board)
        game_menu.add_command(label="New Series", command=self.new_series)
        game_menu.add_command(label="Change Target", command=self.change_target_score)
        game_menu.add_command(label="Switch Mode", command=self.switch_modes)
        game_menu.add_separator()
        game_menu.add_command(label="Main Menu", command=self.return_to_home)
        game_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="Game", menu=game_menu)

    def _get_player_names(self):
        human_player = self._game.original_players[0]
        human_player.name = simpledialog.askstring(
            "Player Name", 
            "Enter your name:",
            parent=self.root
        ) or "Player 1"
        
        if self.ai_mode:
            self._game.original_players[1].name = "Computer"
        else:
            friend_name = simpledialog.askstring(
                "Friend's Name", 
                "Enter friend's name:",
                parent=self.root
            ) or "Player 2"
            self._game.original_players[1].name = friend_name
        
        self.series_scores = {
            self._game.original_players[0].name: 0,
            self._game.original_players[1].name: 0
        }

    def _setup_target_score(self):
        self.target_score = simpledialog.askinteger(
            "Target Score",
            "First to how many wins?",
            parent=self.root,
            minvalue=1,
            maxvalue=10,
            initialvalue=5
        ) or 5
        self.series_display.config(text=f"First to {self.target_score} wins")

    def play(self, row, col):
        button = self._buttons.get((row, col))
        if not button:
            return
            
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            button.config(text=self._game.current_player.label, fg=self._game.current_player.color)
            self._game.process_move(move)
            
            if self._game.is_tied():
                self.ties += 1
                self._update_display("Game Tied!", "red")
                self._update_scores()
                self.handle_series_progress()
            elif self._game.has_winner():
                self._highlight_cells()
                winner = self._game.current_player
                self.series_scores[winner.name] += 1
                self.total_score += 10  # Add 10 points per win
                
                msg = f'{winner.name} ({winner.label}) wins!'
                color = winner.color
                self._update_display(msg, color)
                self._update_scores()
                self.handle_series_progress()
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.name}'s turn ({self._game.current_player.label})"
                self._update_display(msg)
                if self.ai_mode and self._game.current_player.label == "O":
                    self.root.after(300, self.ai_move)

    def ai_move(self):
        ai_move = self._game.ai_move()
        if ai_move is None:
            return
            
        button = self._buttons.get((ai_move.row, ai_move.col))
        if button:
            button.config(text="O", fg=self._game.original_players[1].color)
            self._game.process_move(ai_move)
            
            if self._game.is_tied():
                self.ties += 1
                self._update_display("Game Tied!", "red")
                self._update_scores()
                self.handle_series_progress()
            elif self._game.has_winner():
                self._highlight_cells()
                winner = self._game.current_player
                self.series_scores[winner.name] += 1
                self.total_score += 10  # Add 10 points per win
                
                msg = f'{winner.name} ({winner.label}) wins!'
                color = winner.color
                self._update_display(msg, color)
                self._update_scores()
                self.handle_series_progress()
            else:
                self._game.toggle_player()
                self._update_display(f"{self._game.current_player.name}'s turn ({self._game.current_player.label})")

    def handle_series_progress(self):
        winner = self._game.current_player
        other_player = next(p for p in self._game.original_players if p != winner)
        
        if self.series_scores[winner.name] >= self.target_score:
            msg = (f"{winner.name} wins the series {self.series_scores[winner.name]}"
                  f" to {self.series_scores[other_player.name]}!")
            messagebox.showinfo("Series Winner", msg)
            
            if self.ai_mode and winner.label == "X":
                self.leaderboard.add_score(winner.name, self.series_scores[winner.name])
            
            self.game_instance.record_score(self.total_score)
            self.return_to_home()
        else:
            self.root.after(1500, self.reset_board)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color
        
    def _update_scores(self):
        player_x = next(p for p in self._game.original_players if p.label == "X")
        player_o = next(p for p in self._game.original_players if p.label == "O")
        
        game_score = f"Game: {player_x.name} (X): {player_x.wins}  |  {player_o.name} (O): {player_o.wins}  |  Ties: {self.ties}"
        series_score = (f"Series: {player_x.name} {self.series_scores[player_x.name]} - "
                      f"{self.series_scores[player_o.name]} {player_o.name} (First to {self.target_score})")
        
        self.score_display["text"] = f"{game_score}\n{series_score}"

    def _highlight_cells(self):
        for (row, col), button in self._buttons.items():
            button.config(highlightbackground="lightblue")
            for combo in self._game._winning_combos:
                if (row, col) in combo:
                    button.config(highlightbackground="red")

    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard - Player vs AI")
        
        scores = self.leaderboard.get_leaderboard()
        
        tk.Label(leaderboard_window, 
                text="Top Scores - Player vs AI",
                font=("Arial", 14, 'bold')).pack(pady=10)
        
        if not scores:
            tk.Label(leaderboard_window, text="No scores yet!").pack()
        else:
            for i, entry in enumerate(scores, 1):
                tk.Label(leaderboard_window,
                       text=f"{i}. {entry['name']}: {entry['score']} wins",
                       font=("Arial", 12)).pack(pady=2)

    def new_series(self):
        if messagebox.askyesno("New Series", "Start a new series?"):
            self._setup_target_score()
            self.series_scores = {
                self._game.original_players[0].name: 0,
                self._game.original_players[1].name: 0
            }
            self._game.original_players[0].wins = 0
            self._game.original_players[1].wins = 0
            self.ties = 0
            self.reset_board()

    def change_target_score(self):
        new_target = simpledialog.askinteger(
            "Change Target Score",
            f"Current target: {self.target_score}\nNew target:",
            parent=self.root,
            minvalue=1,
            maxvalue=10,
            initialvalue=self.target_score
        )
        if new_target and new_target != self.target_score:
            self.target_score = new_target
            self.series_display.config(text=f"First to {self.target_score} wins")
            self._update_scores()

    def switch_modes(self):
        if messagebox.askyesno("Switch Mode", "Switch game modes? This will end current series."):
            self.ai_mode = not self.ai_mode
            self._get_player_names()
            self.new_series()

    def return_to_home(self):
        self.game_instance.record_score(self.total_score)
        self.root.destroy()
        self.home_page.deiconify()

    def reset_board(self):
        self._game.reset_game()
        self._update_display(f"{self._game.current_player.name}'s turn ({self._game.current_player.label})")
        self._update_scores()
        
        for (row, col), button in self._buttons.items():
            button.config(
                highlightbackground="lightblue",
                text="",
                fg="black"
            )
        
        if self.ai_mode and self._game.current_player.label == "O":
            self.root.after(300, self.ai_move)

# Dice Rolling Lottery
class DiceRollingLottery(BaseGame):
    def __init__(self, analytics):
        super().__init__(analytics)
        self.game_name = "Dice Rolling Lottery"
        self.total_score = 0
        self.rounds_played = 0
        self.scores = []
        self.high_score = 0
        self.pygame_initialized = False
        self.background = None
        self.dice_images = []
        self.sounds = {}
        self.font = None
        self.title_font = None
        self.screen = None

    def initialize_pygame(self):
        """Initialize pygame components for this game"""
        if not self.pygame_initialized:
            pygame.init()
            pygame.mixer.init()
            self.screen = pygame.display.set_mode((630, 360))
            pygame.display.set_caption("Dice Rolling Lottery")
            self.font = pygame.font.SysFont("Arial", 24)
            self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
            self.load_assets()
            self.pygame_initialized = True

    def load_assets(self):
        """Load all game assets with fallbacks"""

        try:
            bg_path = os.path.join("assets", "images", "game_bg.png")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (630, 360))
        except:
            self.background = pygame.Surface((630, 360))
            self.background.fill((50, 50, 100))  
            

        try:
            self.dice_images = [
                pygame.image.load(f'assets/images/dice_{i}.png') 
                for i in range(1, 7)
            ]
            self.dice_images = [pygame.transform.scale(img, (60, 60)) for img in self.dice_images]
        except:

            self.dice_images = []
            for i in range(1, 7):
                surf = pygame.Surface((60, 60))
                surf.fill((255, 255, 255))
                text = self.font.render(str(i), True, (0, 0, 0))
                surf.blit(text, (30 - text.get_width()//2, 30 - text.get_height()//2))
                self.dice_images.append(surf)
                

        sound_files = {
            'win': 'win.wav',
            'lose': 'lose.wav',
            'roll': 'dice_roll.wav',
            'start': 'game_start.mp3'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                sound_path = f'assets/sounds/{filename}'
                if sound_name == 'start':
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play(-1)
                else:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
            except:
                self.sounds[sound_name] = None

    def cleanup(self):
        """Clean up pygame resources without quitting display"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()


    def play(self):
        """Main game loop that integrates with the menu system"""
        try:
            self.initialize_pygame()
            running = True
            
            while running:
                choice = self.show_main_menu()
                
                if choice == 1:  
                    if self.sounds.get('roll'):
                        self.sounds['roll'].play()
                    
                    guess = self.get_user_guess()
                    if guess is None: 
                        running = False
                        break
                    
                    total, dice_values = self.roll_dice()
                    self.show_dice_animation(dice_values)
                    if not self.show_result(guess, total, dice_values):
                        running = False
                        break
                    
                elif choice == 2:
                    if not self.show_stats_screen():
                        running = False
                        break
                    
                elif choice == 3:
                    running = False
                
                else:
                    running = False
            
            return self.total_score
        except Exception as e:
            print(f"Error in Dice Rolling Lottery: {e}")
            return 0
        finally:
            self.cleanup()

    def roll_dice(self):
        """Rolls dice and returns the sum and individual dice values"""
        dice_values = [random.randint(1, 6) for _ in range(3)]
        return sum(dice_values), dice_values

    def draw_text(self, text, x, y, color=(255, 255, 255), font=None, center=True):
        """Helper method to draw text on screen"""
        font = font or self.font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def show_dice_animation(self, dice_values):
        """Show animated dice rolling effect"""
        for i in range(10):
            self.screen.blit(self.background, (0, 0))
            self.draw_text("Rolling...", 315, 100, (255, 255, 0), self.title_font)
            

            for j in range(3):
                random_dice = random.randint(0, 5)
                self.screen.blit(self.dice_images[random_dice], (200 + j*80, 150))
            
            pygame.display.flip()
            pygame.time.delay(100)
        

        self.screen.blit(self.background, (0, 0))
        self.draw_text("Results:", 315, 100, (255, 255, 0), self.title_font)
        for j in range(3):
            self.screen.blit(self.dice_images[dice_values[j]-1], (200 + j*80, 150))
        pygame.display.flip()

    def get_user_guess(self):
        """Get user input through pygame interface"""
        guess = ""
        input_active = True
        input_rect = pygame.Rect(200, 200, 200, 40)
        color_active = pygame.Color('lightskyblue3')
        color_passive = pygame.Color('gray15')
        color = color_passive
        
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        color = color_active
                    else:
                        color = color_passive
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if guess.isdigit() and 3 <= int(guess) <= 18:
                            input_active = False
                        else:
                            guess = ""
                    elif event.key == pygame.K_BACKSPACE:
                        guess = guess[:-1]
                    else:
                        if event.unicode.isdigit() and len(guess) < 2:
                            guess += event.unicode
            
            self.screen.blit(self.background, (0, 0))
            self.draw_text("Guess the sum (3-18):", 315, 150, (255, 255, 255), self.title_font)
            
            pygame.draw.rect(self.screen, color, input_rect, 2)
            text_surface = self.font.render(guess, True, (255, 255, 255))
            self.screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
            
            submit_rect = self.draw_text("Submit", 315, 270, (0, 255, 0), self.title_font)
            pygame.display.flip()
            

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if submit_rect.collidepoint(mouse_pos) and mouse_click[0]:
                if guess.isdigit() and 3 <= int(guess) <= 18:
                    input_active = False
        
        return int(guess) if guess else None

    def show_result(self, guess, total, dice_values):
        """Display game results with visual feedback"""
        result = guess == total
        if result:
            result_text = f"Congratulations! You won J$1000!"
            result_color = (0, 255, 0)
            if self.sounds['win']:
                self.sounds['win'].play()
            self.score = 1000
        else:
            result_text = f"Sorry! The sum was {total}. You guessed {guess}."
            result_color = (255, 0, 0)
            if self.sounds['lose']:
                self.sounds['lose'].play()
            self.score = 0
        
        self.total_score += self.score
        self.rounds_played += 1
        self.scores.append(self.score)
        self.high_score = max(self.high_score, self.score)
        self.record_score(self.score)
        
        waiting = True
        while waiting:
            self.screen.blit(self.background, (0, 0))
            

            for j in range(3):
                self.screen.blit(self.dice_images[dice_values[j]-1], (200 + j*80, 150))
            
            self.draw_text(f"Sum: {total}", 315, 220, (255, 255, 0))
            self.draw_text(result_text, 315, 250, result_color, self.title_font)
            
            continue_rect = self.draw_text("Continue", 315, 320, (255, 255, 255), self.title_font)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_rect.collidepoint(event.pos):
                        waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
        
        return True

    def show_stats_screen(self):
        """Display game statistics screen"""
        waiting = True
        while waiting:
            self.screen.blit(self.background, (0, 0))
            
            self.draw_text("Game Statistics", 315, 50, (255, 255, 0), self.title_font)
            
            y_pos = 100
            stats = [
                f"Rounds Played: {self.rounds_played}",
                f"Total Score: J${self.total_score}",
                f"High Score: J${self.high_score}",
                f"Average Score: J${self.total_score/self.rounds_played:.2f}" if self.rounds_played > 0 else "Average Score: N/A"
            ]
            
            for stat in stats:
                self.draw_text(stat, 315, y_pos)
                y_pos += 40
            
            back_rect = self.draw_text("Back to Game", 315, 300, (0, 255, 255), self.title_font)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos):
                        waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
        
        return True

    def show_main_menu(self):
        """Display in-game menu options"""
        waiting = True
        choice = None
        
        while waiting:
            self.screen.blit(self.background, (0, 0))
            
            self.draw_text("Dice Rolling Lottery", 315, 50, (255, 255, 0), self.title_font)
            
            play_rect = self.draw_text("1. Play Round", 315, 150, (255, 255, 255), self.title_font)
            stats_rect = self.draw_text("2. View Statistics", 315, 200, (255, 255, 255), self.title_font)
            quit_rect = self.draw_text("3. Exit to Main Menu", 315, 250, (255, 255, 255), self.title_font)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect.collidepoint(event.pos):
                        choice = 1
                        waiting = False
                    elif stats_rect.collidepoint(event.pos):
                        choice = 2
                        waiting = False
                    elif quit_rect.collidepoint(event.pos):
                        choice = 3
                        waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        choice = 1
                        waiting = False
                    elif event.key == pygame.K_2:
                        choice = 2
                        waiting = False
                    elif event.key == pygame.K_3:
                        choice = 3
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        choice = 3
                        waiting = False
        
        return choice



# Battle Arena
class Fighter:
    def __init__(self, name, color, atk_range, def_range, special_range, character_type):
        self.name = name
        self.color = color
        self.original_color = color
        self.hp = 100
        self.max_hp = 100
        self.atk_range = atk_range
        self.def_range = def_range
        self.special_range = special_range
        self.special_used = False
        self.character_type = character_type

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
        self.max_hp += 20
        self.hp = self.max_hp
        self.atk_range = (self.atk_range[0] + 2, self.atk_range[1] + 2)
        self.def_range = (self.def_range[0] + 1, self.def_range[1] + 1)
        self.special_range = (self.special_range[0] + 5, self.special_range[1] + 5)
        self.special_used = False

class Enemy(Fighter):
    def __init__(self, name, color, atk_range, def_range, special_range, enemy_type):
        super().__init__(name, color, atk_range, def_range, special_range, enemy_type)
        self.enemy_type = enemy_type

    def attack(self):
        bonus = 5 if self.enemy_type == "Archer" else 3 if self.enemy_type == "Mage" else 0
        return random.randint(self.atk_range[0], self.atk_range[1] + bonus)

class BattleArena(BaseGame):

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (128, 0, 128)

    def __init__(self, analytics):
        super().__init__(analytics)
        self.game_name = "Battle Arena"
        self.screen = None
        self.background = None
        self.font = None
        self.character_images = {}
        self.sounds = {}
        self.clock = pygame.time.Clock()
        self.pygame_initialized = False

    def initialize_pygame(self):
        """Initialize pygame resources"""
        if not self.pygame_initialized:
            pygame.init()

            pygame.mixer.init()
            self.screen = pygame.display.set_mode((600, 400))
            pygame.display.set_caption("Battle Arena")
            self.font = pygame.font.SysFont("Arial", 20)
            self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
            self.pygame_initialized = True

    def load_assets(self):
        """Load all game assets with fallbacks"""

        try:
            bg_path = os.path.join("assets", "images", "Background.png")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (600, 400))
        except pygame.error:
            self.background = pygame.Surface((600, 400))
            self.background.fill(self.BLACK)
            print("Background image not found - using solid color")


        sound_files = {
            'magic': "magic.mp3",
            'sword': "sword.mp3", 
            'shield': "shield.mp3",
            'background': "background.mp3"
        }
        
        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join("assets", "sounds", filename)
                if sound_name == 'background':
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play(-1)
                else:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
            except pygame.error:
                self.sounds[sound_name] = None
                print(f"Sound {filename} not found - continuing without sound")


        character_files = {
            'warrior': "warrior.png",
            'mage': "mage.png",
            'knight': "knight.png",
            'orc': "orc.png",
            'elf': "elf.png",
            'necromancer': "necromancer.png"
        }
        
        for char_type, filename in character_files.items():
            try:
                img_path = os.path.join("assets", "images", filename)
                img = pygame.image.load(img_path)
                self.character_images[char_type] = pygame.transform.scale(img, (50, 50))
            except pygame.error:
                self.character_images[char_type] = None
                print(f"Character image {filename} not found - using colored rectangle")

    def cleanup(self):
        """Clean up pygame resources"""
        if self.pygame_initialized:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            pygame.quit()
            self.pygame_initialized = False

    def play(self):
        """Main entry point that shows menu first"""
        root = tk.Tk()
        root.withdraw()
        

        menu_window = tk.Toplevel(root)
        menu_window.title("Battle Arena - Menu")
        menu_window.geometry("400x300")
        menu_window.resizable(False, False)
        

        frame = tk.Frame(menu_window, padx=20, pady=20)
        frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(frame, text="BATTLE ARENA", font=("Arial", 24, "bold")).pack(pady=10)
        tk.Label(frame, text="Defeat enemies in epic combat!", font=("Arial", 12)).pack(pady=5)
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=20)
        

        tk.Button(button_frame, text="Start Game", command=lambda: self.start_game(menu_window, root),
                 font=("Arial", 14), width=15, bg="#4CAF50", fg="white").pack(pady=10)
        

        tk.Button(button_frame, text="Exit to Menu", command=lambda: self.return_to_main(menu_window, root),
                 font=("Arial", 14), width=15, bg="#f44336", fg="white").pack(pady=10)
        

        menu_window.protocol("WM_DELETE_WINDOW", lambda: self.return_to_main(menu_window, root))
        
        root.mainloop()
        return 0

    def start_game(self, menu_window, root):
        """Start the actual game"""
        menu_window.destroy()
        root.quit()
        
        try:
            self.initialize_pygame()
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.load_assets()
            score = self.run_game_loop()
            self.record_score(score)
            return score
        except Exception as e:
            print(f"Error in Battle Arena: {e}")
            return 0
        finally:

            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()


    def return_to_main(self, menu_window, root):
        """Return to main menu"""
        menu_window.destroy()
        root.quit()

    def run_game_loop(self):
        """Main game logic"""
        try:
            results = []
            player = self.select_character()
            if not player:
                return 0
                
            rounds = self.select_rounds()
            if not rounds:
                return 0
                
            self.show_storyline(player)
            
            for _ in range(rounds):
                enemy = self.create_random_enemy()
                win = self.run_battle(player, enemy)
                results.append(1 if win else 0)
                
                self.display_result(win)
                if not self.wait_for_input(["space"]):
                    break
                    
                player.level_up()
            
            if results:
                self.show_stats(results)
                self.wait_for_input(["space"])
            
            return sum(results) * 100
        except pygame.error:

            pygame.display.init()
            self.screen = pygame.display.set_mode((600, 400))
            return 0
        finally:

            pygame.mixer.music.stop()
            pygame.mixer.quit()

    def create_random_enemy(self):
        """Create a random enemy fighter"""
        enemy_type = random.choice(["Warrior", "Archer", "Mage"])
        if enemy_type == "Warrior":
            return Enemy("Orc", self.RED, (12, 22), (6, 10), (0, 0), "Orc")
        elif enemy_type == "Archer":
            return Enemy("Elf", self.GREEN, (10, 20), (5, 8), (0, 0), "Elf")
        else:
            return Enemy("Necromancer", self.PURPLE, (8, 15), (5, 10), (10, 30), "Necromancer")

    def select_character(self):
        """Character selection screen"""
        while True:
            self.screen.blit(self.background, (0, 0))
            self.draw_text("Select Your Character:", 300, 100, center=True)
            self.draw_text("1) Warrior - High Attack", 300, 140, center=True)
            self.draw_text("2) Mage - Powerful Special", 300, 170, center=True)
            self.draw_text("3) Knight - Balanced", 300, 200, center=True)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return Fighter("Warrior", self.YELLOW, (15, 25), (5, 12), (30, 40), "Warrior")
                    elif event.key == pygame.K_2:
                        return Fighter("Mage", self.PURPLE, (10, 20), (4, 8), (35, 50), "Mage")
                    elif event.key == pygame.K_3:
                        return Fighter("Knight", self.BLUE, (12, 18), (8, 14), (20, 30), "Knight")

    def select_rounds(self):
        """Round selection screen"""
        while True:
            self.screen.blit(self.background, (0, 0))
            self.draw_text("Select number of rounds:", 300, 100, center=True)
            self.draw_text("1) One Round (Quick Game)", 300, 140, center=True)
            self.draw_text("2) Three Rounds (Standard)", 300, 170, center=True)
            self.draw_text("3) Five Rounds (Marathon)", 300, 200, center=True)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: return 1
                    elif event.key == pygame.K_2: return 3
                    elif event.key == pygame.K_3: return 5

    def show_storyline(self, player):
        """Show character backstory"""
        self.screen.blit(self.background, (0, 0))
        
        if player.character_type == "Warrior":
            story = [
                "As a mighty Warrior from the Northern Wastes,",
                "you seek glory in battle against the dark forces",
                "that threaten your homeland. Your strength and",
                "courage will be tested in the arena!"
            ]
        elif player.character_type == "Mage":
            story = [
                "Trained in the arcane arts at the Crystal Spire,",
                "you wield powerful magic. The arena calls to test",
                "your spells against worthy opponents. Show them",
                "the true power of magic!"
            ]
        else:
            story = [
                "As a sworn Knight of the Silver Order,",
                "you fight with honor and skill. The arena awaits",
                "to prove your worth. May your sword strike true",
                "against these dangerous foes!"
            ]
        
        y = 100
        for line in story:
            self.draw_text(line, 300, y, center=True)
            y += 30

        self.draw_text("Press SPACE to begin your battle...", 300, y + 40, center=True)
        pygame.display.flip()
        self.wait_for_input(["space"])

    def run_battle(self, player, enemy):
        """Execute a battle between player and enemy"""
        while player.hp > 0 and enemy.hp > 0:

            self.screen.blit(self.background, (0, 0))
            self.draw_fighter(100, 200, player)
            self.draw_fighter(400, 200, enemy)
            self.draw_health_bar(100, 180, player.hp, player.name, player.max_hp)
            self.draw_health_bar(400, 180, enemy.hp, enemy.name, enemy.max_hp)
            self.draw_text("A: Attack  D: Defend  S: Special", 300, 350, center=True)
            pygame.display.flip()
            

            action = None
            while action is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: 
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a: action = "attack"
                        elif event.key == pygame.K_d: action = "defend"
                        elif event.key == pygame.K_s: action = "special"
            

            if action == "attack":
                self.play_sound('sword')
                damage = player.attack()
                self.projectile_animation(150, 220, 400, 220, self.YELLOW, player, enemy)
                enemy.hp = max(0, enemy.hp - damage)
                message = f"You hit {enemy.name} for {damage} damage!"
            elif action == "defend":
                self.play_sound('shield')
                block = player.defend()
                if self.word_scramble_challenge():
                    block += 15
                    message = f"Perfect defense! Blocked {block} damage!"
                else:
                    enemy_damage = max(0, enemy.attack() - block)
                    player.hp = max(0, player.hp - enemy_damage)
                    message = f"You blocked {block} damage, took {enemy_damage}!"
                self.projectile_animation(400, 220, 150, 220, self.RED, player, enemy)
            elif action == "special":
                self.play_sound('magic')
                special_damage = player.special()
                if special_damage > 0:
                    self.projectile_animation(150, 220, 400, 220, self.PURPLE, player, enemy)
                    enemy.hp = max(0, enemy.hp - special_damage)
                    message = f"SPECIAL ATTACK! {special_damage} damage!"
                else:
                    message = "Special attack already used this battle!"
            

            self.screen.blit(self.background, (0, 0))
            self.draw_fighter(100, 200, player)
            self.draw_fighter(400, 200, enemy)
            self.draw_health_bar(100, 180, player.hp, player.name, player.max_hp)
            self.draw_health_bar(400, 180, enemy.hp, enemy.name, enemy.max_hp)
            self.draw_text(message, 300, 320, center=True)
            pygame.display.flip()
            pygame.time.wait(1500)
            

            if enemy.hp > 0 and action != "defend":
                enemy_damage = enemy.attack()
                if self.word_scramble_challenge():
                    message = "You dodged the enemy attack!"
                else:
                    player.hp = max(0, player.hp - enemy_damage)
                    message = f"{enemy.name} hits you for {enemy_damage} damage!"
                
                self.projectile_animation(400, 220, 150, 220, self.RED, player, enemy)
                self.screen.blit(self.background, (0, 0))
                self.draw_fighter(100, 200, player)
                self.draw_fighter(400, 200, enemy)
                self.draw_health_bar(100, 180, player.hp, player.name, player.max_hp)
                self.draw_health_bar(400, 180, enemy.hp, enemy.name, enemy.max_hp)
                self.draw_text(message, 300, 320, center=True)
                pygame.display.flip()
                pygame.time.wait(1500)
        
        return player.hp > 0

    def word_scramble_challenge(self):
        """Mini-game for defense"""
        words = ["SHIELD", "ARMOR", "BLOCK", "DEFEND", "SWORD", "DODGE"]
        word = random.choice(words)
        scrambled = ''.join(random.sample(word, len(word)))
        
        input_text = ""
        start_time = time.time()
        success = False
        
        while time.time() - start_time < 10:
            self.screen.blit(self.background, (0, 0))
            self.draw_text("Unscramble the word to defend!", 300, 150, center=True)
            self.draw_text(scrambled, 300, 200, center=True)
            self.draw_text(input_text, 300, 250, center=True)
            self.draw_text("Press ENTER when done", 300, 300, center=True)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        success = (input_text.upper() == word)
                        return success
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode.upper()
        
        return False

    def draw_fighter(self, x, y, fighter):
        """Draw fighter with image or fallback"""
        char_type = fighter.character_type.lower() if hasattr(fighter, "character_type") else fighter.enemy_type.lower()
        image = self.character_images.get(char_type)
        
        if image:

            border_rect = pygame.Rect(x-3, y-3, 56, 56)
            pygame.draw.rect(self.screen, self.WHITE, border_rect)
            self.screen.blit(image, (x, y))
        else:

            pygame.draw.rect(self.screen, fighter.color, (x, y, 50, 50))

    def draw_health_bar(self, x, y, current_hp, name, max_hp=100):
        """Draw health bar with name"""
        bar_width = 100
        health_width = (current_hp / max_hp) * bar_width
        

        pygame.draw.rect(self.screen, self.BLACK, (x, y, bar_width, 15))

        pygame.draw.rect(self.screen, self.GREEN, (x, y, health_width, 15))

        text = self.font.render(f"{name}: {current_hp}/{max_hp}", True, self.WHITE)
        self.screen.blit(text, (x, y - 20))

    def projectile_animation(self, start_x, start_y, end_x, end_y, color, player, enemy):
        """Animate projectile between points"""
        steps = 20
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        for i in range(steps):
            self.screen.blit(self.background, (0, 0))
            self.draw_fighter(100, 200, player)
            self.draw_fighter(400, 200, enemy)
            

            proj_x = start_x + (dx * i)
            proj_y = start_y + (dy * i)
            pygame.draw.circle(self.screen, color, (int(proj_x), int(proj_y)), 5)
            
            pygame.display.flip()
            self.clock.tick(60)

    def play_sound(self, sound_name):
        """Play sound effect if available"""
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def display_result(self, win):
        """Show battle result screen"""
        self.screen.blit(self.background, (0, 0))
        if win:
            self.draw_text("VICTORY!", 300, 150, self.GREEN, center=True)
            self.draw_text("You defeated your opponent!", 300, 200, center=True)
        else:
            self.draw_text("DEFEAT", 300, 150, self.RED, center=True)
            self.draw_text("Better luck next time!", 300, 200, center=True)
        
        self.draw_text("Press SPACE to continue", 300, 300, center=True)
        pygame.display.flip()

    def show_stats(self, results):
        """Display game statistics"""
        wins = results.count(1)
        losses = results.count(0)
        win_rate = (wins / len(results)) * 100 if results else 0
        
        self.screen.blit(self.background, (0, 0))
        self.draw_text("BATTLE STATISTICS", 300, 80, self.YELLOW, center=True)
        self.draw_text(f"Rounds: {len(results)}", 300, 130, center=True)
        self.draw_text(f"Wins: {wins}", 300, 170, self.GREEN, center=True)
        self.draw_text(f"Losses: {losses}", 300, 210, self.RED, center=True)
        self.draw_text(f"Win Rate: {win_rate:.1f}%", 300, 250, center=True)
        self.draw_text("Press SPACE to return", 300, 320, center=True)
        pygame.display.flip()

    def draw_text(self, text, x, y, color=None, center=False):
        """Draw text with optional center alignment"""
        color = color or self.WHITE
        text_surface = self.font.render(text, True, color)
        
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        

        outline_surface = self.font.render(text, True, self.BLACK)
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            outline_rect = text_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy
            self.screen.blit(outline_surface, outline_rect)
        
        self.screen.blit(text_surface, text_rect)

    def wait_for_input(self, keys):
        """Wait for specified key press"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    return False
                if event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) in keys:
                        return True
            self.clock.tick(30)
        return True

    def display_stats(self):
        """Display game statistics from analytics"""
        stats = self.analytics.get_stats(self.game_name)
        if not stats:
            print("\nNo statistics available yet for Battle Arena")
            return
        
        print("\n=== Battle Arena Statistics ===")
        print(f"Total Plays: {stats['plays']}")
        print(f"Average Score: {stats['mean']:.1f}")
        print(f"High Score: {stats['max']}")
        print(f"Low Score: {stats['min']}")
        print(f"Score Range: {stats['range']}")
        print(f"Median Score: {stats['median']}")
        print(f"Most Common Score: {stats['mode']}")

# Pygame Menu System
class PygameMenu:
    def __init__(self, game_collection):
        pygame.init()
        self.screen_width, self.screen_height = 1024, 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Game Collection Menu")
        self.clock = pygame.time.Clock()
        self.game_collection = game_collection
        self.font = pygame.font.SysFont('Arial', 32)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.background = self._load_background()
        self.selected_index = 0
        self.menu_items = [
            "1. Galactic Fortune (Space Shooter)",
            "2. Tic-Tac-Toe (Strategy)",
            "3. Dice Rolling Lottery (Chance Game)",
            "4. Battle Arena (Fighting Game)",
            "S. View Statistics",
            "Q. Quit"
        ]
        self.colors = {
            'normal': (255, 255, 255),
            'selected': (255, 215, 0),
            'title': (0, 191, 255)
        }
        self.original_display_flags = None

    def _load_background(self):
        try:
            bg = pygame.image.load('assets/images/menu_bg.jpg')
            return pygame.transform.scale(bg, (self.screen_width, self.screen_height))
        except:
            bg = pygame.Surface((self.screen_width, self.screen_height))
            bg.fill((30, 30, 60))
            return bg

    def run(self):
        running = True
        while running:
            self._handle_events()
            self._draw_menu()
            pygame.display.flip()
            self.clock.tick(60)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                elif event.key == pygame.K_RETURN:
                    self._select_menu_item()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def _select_menu_item(self):
        choice = self.menu_items[self.selected_index][0].upper()
        
        if choice == 'Q':
            pygame.quit()
            sys.exit()
        elif choice == 'S':
            self._show_statistics()
        else:
            try:
                game_index = int(choice) - 1
                if 0 <= game_index < len(self.game_collection.games):
                    self._launch_game(game_index)
            except ValueError:
                pass

    def _launch_game(self, game_index):
        self.original_display_flags = self.screen.get_flags()
        self.original_display_size = self.screen.get_size()
        
        
        try:
            score = self.game_collection.games[game_index].play()
            
            self._restore_display()
            
            if score is not None:
                self.game_collection.games[game_index].record_score(score)
                self._show_game_result(score, self.game_collection.games[game_index].game_name)
        except Exception as e:
            print(f"Error running game: {e}")
            self._restore_display()

    def _restore_display(self):
        """Restore the pygame display to its original state"""
        try:
            if not pygame.display.get_init():
                pygame.display.init()
            
            current_flags = 0
            current_size = (0, 0)
            try:
                current_flags = self.screen.get_flags()
                current_size = self.screen.get_size()
            except:
                pass
                
            if (current_flags != self.original_display_flags or 
                current_size != self.original_display_size):
                self.screen = pygame.display.set_mode(
                    self.original_display_size, 
                    self.original_display_flags
                )
            
            if sys.platform == 'win32':
                try:
                    ctypes.windll.user32.ShowWindow(pygame.display.get_wm_info()['window'], 9)
                except:
                    pass
            
            pygame.event.clear()
            pygame.display.set_caption("Game Collection Menu")
            
        except Exception as e:
            print(f"Error restoring display: {e}")
            pygame.quit()
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Game Collection Menu")

    def _show_game_result(self, score, game_name):
        self.screen.fill((0, 0, 0))
        result_text = self.title_font.render(f"{game_name} Results", True, (255, 255, 255))
        score_text = self.font.render(f"Your Score: {score}", True, (255, 255, 255))
        continue_text = self.font.render("Press any key to return to menu", True, (200, 200, 200))
        
        self.screen.blit(result_text, (400 - result_text.get_width()//2, 200))
        self.screen.blit(score_text, (400 - score_text.get_width()//2, 300))
        self.screen.blit(continue_text, (400 - continue_text.get_width()//2, 400))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        

        self._restore_display()

    def _show_statistics(self):
        self.screen.fill((0, 0, 0))
        
        stats_font = pygame.font.SysFont('Arial', 24)
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        title = title_font.render("Game Statistics", True, (255, 255, 255))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
        y_offset = 100
        line_height = 30
        
        for game in self.game_collection.games:
            stats = self.game_collection.analytics.get_stats(game.game_name)
            if stats:
                game_text = stats_font.render(f"{game.game_name}:", True, (255, 255, 0))
                self.screen.blit(game_text, (100, y_offset))
                y_offset += line_height
                
                stats_lines = [
                    f"Plays: {stats['plays']}",
                    f"Average: {stats['mean']:.1f}",
                    f"High: {stats['max']}  Low: {stats['min']}",
                    f"Range: {stats['range']}  Last: {stats['last']}"
                ]
                
                for line in stats_lines:
                    text = stats_font.render(line, True, (255, 255, 255))
                    self.screen.blit(text, (120, y_offset))
                    y_offset += line_height
                
                y_offset += line_height // 2
        
        continue_text = stats_font.render("Press Q to return to menu", True, (200, 200, 200))
        self.screen.blit(continue_text, (self.screen_width//2 - continue_text.get_width()//2, self.screen_height - 50))
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        waiting = False
    def _draw_menu(self):
        self.screen.blit(self.background, (0, 0))
        
        title = self.title_font.render("PYTHON GAME COLLECTION", True, self.colors['title'])
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        
        for i, item in enumerate(self.menu_items):
            color = self.colors['selected'] if i == self.selected_index else self.colors['normal']
            text = self.font.render(item, True, color)
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 200 + i * 40))
        

        instructions = self.font.render("Use ↑ ↓ arrows to navigate, ENTER to select", True, (200, 200, 200))
        self.screen.blit(instructions, (self.screen_width//2 - instructions.get_width()//2, self.screen_height - 80))
    # Final GameCollection and main execution
class GameCollection:
    def __init__(self):
        self.analytics = GameAnalytics()
        self.games = [
            GalacticFortune(self.analytics),
            TicTacToe(self.analytics),
            DiceRollingLottery(self.analytics),
            BattleArena(self.analytics)
        ]
    
    def run(self):
        menu = PygameMenu(self)
        menu.run()

if __name__ == "__main__":
    app = GameCollection()
    app.run()