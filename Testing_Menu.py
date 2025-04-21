import tkinter as tk
from tkinter import messagebox
import multiprocessing
import warnings
import os
import json


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings("ignore", category=UserWarning, module='pygame')


SCORE_FILE = "game_scores.json"

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return {"Tik Tok Toe": 0, "Galactic Fortune": 0, "Battle Arena": 0, "Dice Rolling": 0}
    with open(SCORE_FILE, "r") as f:
        return json.load(f)

def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)

def update_score(game_name, score):
    scores = load_scores()
    scores[game_name] += score
    save_scores(scores)

def show_statistics():
    scores = load_scores()
    stats_msg = "\n".join([f"{game}: {score}" for game, score in scores.items()])
    messagebox.showinfo("Game Statistics", f"Your Scores:\n\n{stats_msg}")


def run_tiktoktoe():
    import Tik_Tok_Toe
    Tik_Tok_Toe.tictoktoe_start()
    update_score("Tik Tok Toe", 1) 

def run_galactic_fortune():
    import Lucky_Shooter1
    Lucky_Shooter1.main()
    update_score("Galactic Fortune", 1)  

def run_battlearena():
    import Official_Battle_Arena_Game
    Official_Battle_Arena_Game.battle_arena_start()
    update_score("Battle Arena", 1) 

def run_dicerolling():
    import Dice_Rolling
    Dice_Rolling.diceroll()
    update_score("Dice Rolling", 1)  




def start_tiktoktoe():
    multiprocessing.Process(target=run_tiktoktoe).start()

def galactic_fortune_start():
    multiprocessing.Process(target=run_galactic_fortune).start()

def start_battlearena():
    multiprocessing.Process(target=run_battlearena).start()

def start_dicerolling():
    multiprocessing.Process(target=run_dicerolling).start()



def create_main_menu():
    root = tk.Tk()
    root.title("Master Mind Menu")
    root.geometry("400x400")
    root.config(bg="#F0E68C")  

    menu_frame = tk.Frame(root, bg="#FAF0E6", padx=20, pady=20)
    menu_frame.pack(pady=20, padx=20)

    title_bar_frame = tk.Frame(menu_frame)
    title_bar_frame.pack(fill="x")

    title_icon = tk.Label(title_bar_frame, text="🎮", font=("Arial", 16), bg="#ADD8E6")
    title_icon.pack(side="left", padx=5)

    title = tk.Label(
        title_bar_frame, text="Game Menu",
        font=("Helvetica", 16, "bold"),
        bg="#ADD8E6", fg="black"
    )
    title.pack(pady=10, fill="x")

    btn_charades = tk.Button(menu_frame, text="Tik Tok Toe", width=20, command=start_tiktoktoe,
                             bg="#FF8C00", fg="white", font=("Arial", 12, "bold"))
    btn_mole = tk.Button(menu_frame, text="Galactic Fortune", width=20, command=galactic_fortune_start,
                         bg="#FFFF00", fg="black", font=("Arial", 12, "bold"))
    btn_card = tk.Button(menu_frame, text="Battle Arena", width=20, command=start_battlearena,
                         bg="#3CB371", fg="white", font=("Arial", 12, "bold"))
    btn_RPC = tk.Button(menu_frame, text="Dice Rolling", width=20, command=start_dicerolling,
                        bg="#DC143C", fg="white", font=("Arial", 12, "bold"))
    btn_stats = tk.Button(menu_frame, text="Statistics", width=20, command=show_statistics,
                          bg="#1E90FF", fg="white", font=("Arial", 12, "bold"))

    btn_charades.pack(pady=5, fill="x")
    btn_mole.pack(pady=5, fill="x")
    btn_card.pack(pady=5, fill="x")
    btn_RPC.pack(pady=5, fill="x")
    btn_stats.pack(pady=5, fill="x")

    root.mainloop()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    create_main_menu()
