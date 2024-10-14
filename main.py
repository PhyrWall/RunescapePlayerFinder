"""
This program is a GUI tool to search for Old School RuneScape players (based on their rank/xp), track their rank and XP in specific skills,
and interact with the Wise Old Man API for player updates. Developed by PhyrWall
"""

import asyncio
import os
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import *

import requests
import wom
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

root = tk.Tk()
root.title("Find Runescape Player")
root.iconbitmap('assets\\search.ico')
root.minsize(height=450, width=400)
root.configure(background='#0f2b5a')

# Start search player
def search_player(rank, skil_xp):

    # All skills
    dict_skills = {'Attack': 1,
                   'Defence': 2,
                   'Strength': 3,
                   'Hitpoints': 4,
                   'Ranged': 5,
                   'Prayer': 6,
                   'Magic': 7,
                   'Cooking': 8,
                   'Woodcutting': 9,
                   'Fletching': 10,
                   'Fishing': 11,
                   'Firemaking': 12,
                   'Crafting': 13,
                   'Smithing': 14,
                   'Mining': 15,
                   'Herblore': 16,
                   'Agility': 17,
                   'Thieving': 18,
                   'Slayer': 19,
                   'Farming': 20,
                   'Runecraft': 21,
                   'Hunter': 22,
                   'Construction': 23}

    rank = rank
    xp = skil_xp

    # Starting page is 6 pages sooner for page differences, this is where it will start web scraping
    starting_page = int(rank / 25) + 1 - 6
    url = f'https://secure.runescape.com/m=hiscore_oldschool/overall?table={dict_skills[clicked.get()]}&page='

    # Run the search in a daemon thread
    thread = threading.Thread(target=hiscore_webscrape, args=(url, xp, starting_page, rank))
    thread.daemon = True  # Set the thread as a daemon so it will exit when the main program exits
    thread.start()

# Function to webscrape the hiscores
def hiscore_webscrape(url, target_xp, start_page, rank):
    found_players.clear()

    # Disable buttons while running
    update_button.configure(state=DISABLED)
    highscore_button.configure(state=DISABLED)
    search_button.configure(state=DISABLED)
    root.after(0, console_output.insert, END, f"Searching for player\nSkill: {clicked.get()}\nTarget XP: {target_xp}\nEstimated Rank: {rank}\n--------------------\n")

    # Loop through pages, start page is ((rank / 25) + 1) - 6
    for page in range(start_page, start_page + 10):
        response = requests.get(url + str(page))
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            player_rows = soup.find_all('tr', class_='personal-hiscores__row')

            # For each row in table, search for xp
            for row in player_rows:
                name_row = row.find('td', class_='left').find('a')
                if name_row:
                    name = name_row.text.replace('\xa0', ' ')
                    xp_cells = row.find_all('td', class_='right')
                    if xp_cells and len(xp_cells) > 1:
                        xp_text = xp_cells[-1].text.replace(',', '').strip()
                        xp = int(xp_text) if xp_text.isdigit() else None

                        # if xp good, output player in console
                        if xp and xp == target_xp:
                            found_players.append(name)
                            root.after(0, console_output.insert, END, f"Found {name} with target XP\n")
                            root.after(0, console_output.see, END)  # Scroll to the end of the text box

        else:
            root.after(0, console_output.insert, END, f"Failed to fetch the high scores page. Status code: {response.status_code}\n")
            root.after(0, console_output.see, END)
            break
    root.after(0, console_output.insert, END, f"\nFinished searching\n")

    # Scroll to the end of the text widget
    root.after(0, console_output.see, END)
    root.after(0, console_output.insert, END, f"\n")

    # Return usage to buttons
    search_button.configure(state=NORMAL)
    highscore_button.configure(state=NORMAL)
    update_button.configure(state=NORMAL)

def check_boxes():

    error_label.grid_forget()  # Hide error label
    try:
        xp = int(skill_xp_input.get().replace(",", "").strip())
        rank = int(player_rank_input.get().replace(",", "").strip())
        search_player(rank, xp)
    except ValueError as e:
        error_label.grid(row=0, column=2)  # Show error label on input error
        print(f"Input error: {e}")

found_players = []

skill_choices = [
    'Agility', 'Attack', 'Construction', 'Cooking', 'Crafting', 'Defence',
    'Farming', 'Firemaking', 'Fishing', 'Fletching', 'Herblore', 'Hitpoints',
    'Hunter', 'Magic', 'Mining', 'Prayer', 'Ranged', 'Runecraft',
    'Slayer', 'Smithing', 'Strength', 'Thieving', 'Woodcutting'
]
clicked = StringVar()
clicked.set(skill_choices[1])

# Set up the GUI layout with consistent background color
player_skill = Label(root, text="Player Skill: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')  # White text on dark blue background
player_skill.grid(row=0, column=0)

# Style for the OptionMenu
drop = OptionMenu(root, clicked, *skill_choices)
drop.config(width=10, bg='#c19a6b', fg='#ffffff', activebackground='#a6805e', activeforeground='#ffffff')
drop.grid(row=0, column=1)

# Entry fields/labels for player rank
player_rank = Label(root, text="Player Rank: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
player_rank.grid(row=1, column=0)
player_rank_input = Entry(root, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
player_rank_input.grid(row=1, column=1)
player_rank_input.insert(0, "")

# Entry fields/labels for skill Xp
skill_xp = Label(root, text="Skill Xp: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
skill_xp.grid(row=2, column=0)
skill_xp_input = Entry(root, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
skill_xp_input.insert(0, "")
skill_xp_input.grid(row=2, column=1)

# Style the button
search_button = Button(root, text="Search", command=check_boxes, width=20)
search_button.grid(row=3, column=0, columnspan=2)
search_button.configure(background="#c19a6b", foreground="#ffffff", activebackground="#a6805e", activeforeground="#ffffff")

# Style for Command Console Label Frame
console_frame = LabelFrame(root, text="Command Console", padx=5, pady=5, bg='#0f2b5a', fg='#ffffff')
console_frame.grid(row=4, column=0, columnspan=3, rowspan=4, sticky="nsew")

# Text widget for console output
console_output = Text(console_frame, height=20, width=50, wrap=WORD, bg='#d9d9d9', fg='#000000')
console_output.pack(fill=BOTH, expand=True)

# Button setup with your custom styles
update_button = Button(root,
                       text="Update Players",
                       command=lambda: update_wom(found_players),  # Trigger update_wom with found_players when clicked
                       width=20)
update_button.grid(row=8, column=0, columnspan=1)  # Adjust the row, column, and span as needed
update_button.configure(background="#c19a6b", foreground="#ffffff",
                        activebackground="#a6805e", activeforeground="#ffffff")

# Button setup with your custom styles
highscore_button = Button(root,
                       text="Open Highscores",
                       command=lambda: open_highscores(found_players),  # Open highscores for all players
                       width=20)
highscore_button.grid(row=8, column=2, columnspan=2)  # Adjust the row, column, and span as needed
highscore_button.configure(background="#c19a6b", foreground="#ffffff",
                        activebackground="#a6805e", activeforeground="#ffffff")

discord = Label(root, text="Discord: jhandeeee",fg='#ffffff', bg='#0f2b5a', width=20)
discord.grid(row=9, column=0)

rsn = Label(root, text="RSN: PhyrWall, ShinyRedDino",fg='#ffffff', bg='#0f2b5a')
rsn.grid(row=9, column=2, columnspan=2)

# Open hiscores for all players found
def open_highscores(players):
    base_url = f'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1='
    for player in players:
        webbrowser.open(base_url + str(player))

# Update players on wiseoldman
async def update_wom_async(players):
    update_button.configure(state=DISABLED)
    search_button.configure(state=DISABLED)
    highscore_button.configure(state=DISABLED)
    client_wom = wom.Client(api_base_url="https://api.wiseoldman.net/v2")
    await client_wom.start()
    root.after(0, console_output.insert, END, f"Updating {len(players)} players on Wiseoldman.net\n"
                                              f"There will be a 3 second delay between each player being updated")
    for player in players:
        await client_wom.players.update_player(player)
        time.sleep(3)
        root.after(0, console_output.insert, END, f"{player} updated\n")
    await client_wom.close()
    update_button.configure(state=NORMAL)
    search_button.configure(state=NORMAL)
    highscore_button.configure(state=NORMAL)

def update_wom(players):
    def run_update():
        asyncio.run(update_wom_async(players))  # Run the async function in the thread

    thread = threading.Thread(target=run_update)
    thread.daemon = True  # Daemon threads will exit when the main program exits
    thread.start()


# Handle image loading
image_path = 'assets/Logo.png'
if os.path.exists(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((100, 100))  # Resize to 100x100 pixels

    # Convert the resized image to a PhotoImage
    photo = ImageTk.PhotoImage(resized_image)

    # Store the reference to the PhotoImage object to avoid garbage collection
    image_label = Label(root, image=photo)
    image_label.image = photo  # Keep a reference to avoid being garbage collected
    image_label.grid(row=0, column=2, rowspan=4, padx=10, pady=10)
else:
    print(f"Error: {image_path} not found. Please check the file path.")

# Label for when error occurs in the check_boxes function
error_label = Label(text="Please verify your entries", fg='red')

root.mainloop()