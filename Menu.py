from Tik_Tok_Toe import *

import tkinter as tk
from tkinter import messagebox


# Placeholder functions for your games
def start_tiktoktoe():
    tictoktoe_start()

def galactic_fortune_start():
    import Lucky_Shooter1
    Lucky_Shooter1.main()

def start_battlearena():
    import Official_Battle_Arena_Game
    Official_Battle_Arena_Game.battle_arena_start()
def start_dicerolling():
    import Dice_Rolling
    Dice_Rolling.diceroll()

def show_help():
    messagebox.showinfo("Help", "Instructions or game help goes here.")



# Setup main window
root = tk.Tk()
root.title("Master Mind Menu")
root.geometry("400x400")
root.config(bg="#F0E68C")  # Khaki background (similar to the outer area)

# Main frame to hold the menu with a slightly different background
menu_frame = tk.Frame(root, bg="#FAF0E6", padx=20, pady=20) # Light Goldenrod Yellow (similar to the inner area)
menu_frame.pack(pady=20, padx=20)

# Title label
title_bar_frame = tk.Frame(menu_frame,) # Light Blue for the title bar
title_bar_frame.pack(fill="x")

title_icon = tk.Label(title_bar_frame, text="🎮", font=("Arial", 16), bg="#ADD8E6")
title_icon.pack(side="left", padx=5)

title = tk.Label(title_bar_frame, text="Game Menu", font=("Helvetica", 16, "bold"), bg="#ADD8E6", fg="black")
title.pack(pady=10, fill="x")

btn_charades = tk.Button(menu_frame, text="Tik Tok Toe", width=20, command=start_tiktoktoe, bg="#FF8C00", fg="white", font=("Arial", 12, "bold")) # Dark Orange
btn_mole = tk.Button(menu_frame, text="Galactic Fortune", width=20, command=galactic_fortune_start, bg="#FFFF00", fg="black", font=("Arial", 12, "bold")) # Yellow
btn_card = tk.Button(menu_frame, text="Battle Arena", width=20, command=start_battlearena, bg="#3CB371", fg="white", font=("Arial", 12, "bold")) # Medium Sea Green
btn_RPC = tk.Button(menu_frame, text="Dice Rolling", width=20, command=start_dicerolling, bg="#DC143C", fg="white", font=("Arial", 12, "bold")) # Medium Sea Green
btn_help = tk.Button(menu_frame, text="Help", width=20, command=show_help, bg="#1E90FF", fg="white", font=("Arial", 12, "bold")) # Dodger Blue

btn_charades.pack(pady=5, fill="x")
btn_mole.pack(pady=5, fill="x")
btn_card.pack(pady=5, fill="x")
btn_RPC.pack(pady=5, fill="x")
btn_help.pack(pady=5, fill="x")


root.mainloop()




