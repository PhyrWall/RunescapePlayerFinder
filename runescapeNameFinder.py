"""
GUI tool to search for Old School RuneScape players (based on their rank/xp), track their rank and XP in specific skills,
and interact with the Wise Old Man API for player updates. Developed by PhyrWall
"""

import asyncio
import csv
import os
import threading
import time
from io import StringIO
from tkinter import *
import webbrowser

import requests
import wom as wom
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

root = Tk()
root.title("Runescape Player Finder")
root.iconbitmap('assets\\icon.ico')
root.minsize(height=530, width=430)
root.configure(background='#0f2b5a')

client_wom = wom.Client(api_base_url="https://api.wiseoldman.net/v2")

def get_details():
    error_label_502.grid_forget()
    error_label.grid_forget()
    error_label_rsn.grid_forget()
    runescape_name = rsn_search.get()

    data = requests.get("https://api.wiseoldman.net/v2/players/"+runescape_name)

    # Check if the request was successful
    if data.status_code == 200:

        try:
            response_json = data.json()

            player_data = response_json.get('latestSnapshot', {})
            player_skills = player_data.get('data', {}).get('skills', {})

            selected_skill = clicked.get()
            selected_skill_lower = selected_skill.lower()

            skill_details = player_skills.get(selected_skill_lower, None)
            # If skill exists get data
            if skill_details:
                # Get rank from WOM
                skill_rank = skill_details.get('rank', 'Rank not found')
                player_rank_input.delete(0, END)
                player_rank_input.insert(0,f'{skill_rank}')

                # Get rank from WOM
                skill_experience = skill_details.get('experience', 'Rank not found')
                skill_xp_input.delete(0,END)
                skill_xp_input.insert(0,f'{skill_experience}')
            else:
                print(f"{clicked.get()} skill data not found.")
        except Exception as e:
            print(f"An error occurred while processing the data: {e}")
            error_label_rsn.grid(row=0, column=2)
    elif data.status_code == 502:
        error_label_502.grid(row=0, column=2)
        print(f"Failed to retrieve data. Status code(s): {data.status_code}")
        error_label.grid(row=0, column=2)
    else:
        print(f"Failed to retrieve data. Status code: {data.status_code}")
        error_label.grid(row=0, column=2)

# Start search player
def search_player(rank, skil_xp):

    # All skills
    runescape_skills = {'Attack': 1,
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
                   'Runecrafting': 21,
                   'Hunter': 22,
                   'Construction': 23}

    rank = rank
    xp = skil_xp


    # Starting page is 6 pages sooner for page differences, this is where it will start web scraping
    starting_page = int(rank / 25) + 1 - 6
    if starting_page < 0:
        starting_page = 1
    if ironman == True:
        url = f'https://secure.runescape.com/m=hiscore_oldschool_ironman/overall?table={runescape_skills[clicked.get()]}&page='
    else:
        url = f'https://secure.runescape.com/m=hiscore_oldschool/overall?table={runescape_skills[clicked.get()]}&page='
    print(url)

    # Run the search in a daemon thread
    thread = threading.Thread(target=hiscore_webscrape, args=(url, xp, starting_page, rank))
    thread.daemon = True  # Set the thread as a daemon so it will exit when the main program exits
    thread.start()

# Function to webscrape the hiscores
def hiscore_webscrape(url, target_xp, page, rank):

    found_players.clear()

    # Disable buttons while running
    disable_buttons()
    start_page = page - 10
    end_page = page + 25
    root.after(0, console_output.insert, END, f"Searching for player\nSkill: {clicked.get()}\nTarget XP: {target_xp}\nEstimated Rank: {rank}\nStart: {start_page}, End: {end_page}\n--------------------\n")
    for page in range(start_page, end_page):
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
    enable_buttons()

def check_boxes():

    error_label.grid_forget()  # Hide error label
    try:
        xp = int(skill_xp_input.get().replace(",", "").strip())
        rank = int(player_rank_input.get().replace(",", "").strip())
        search_player(rank, xp)
    except ValueError as e:
        error_label.grid(row=0, column=2)  # Show error label on input error
        print(f"Input error: {e}")


ironman = False  # Starts as False (main account)


def toggle_ironman():
    global ironman
    ironman = not ironman  # Toggle the ironman variable

    # Update the button text to reflect the new state
    if ironman:
        ironman_button.config(text="Ironman: ON", bg='#e74c3c', activebackground='#c0392b')
    else:
        ironman_button.config(text="Ironman: OFF", bg='#3498db', activebackground='#2980b9')


found_players = []

skill_choices = [
    'Agility', 'Attack', 'Construction', 'Cooking', 'Crafting', 'Defence',
    'Farming', 'Firemaking', 'Fishing', 'Fletching', 'Herblore', 'Hitpoints',
    'Hunter', 'Magic', 'Mining', 'Prayer', 'Ranged', 'Runecrafting',
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
rsn_search = Entry(root, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
rsn_search.grid(row=1, column=0)
# rsn_search.insert(0, "Insert RSN")
rsn_search.insert(0, "PhyrWall")
rsn_search_button = Button(root, text="Search WiseOldMan.net", command=get_details, width=20)
rsn_search_button.grid(row=1, column=1)
rsn_search_button.configure(background="#c19a6b", foreground="#ffffff", activebackground="#a6805e", activeforeground="#ffffff")


# Entry fields/labels for player rank
player_rank = Label(root, text="Player Rank: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
player_rank.grid(row=2, column=0)
player_rank_input = Entry(root, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
player_rank_input.grid(row=2, column=1)
player_rank_input.insert(0, "")

# Entry fields/labels for skill Xp
skill_xp = Label(root, text="Skill Xp: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
skill_xp.grid(row=3, column=0)
skill_xp_input = Entry(root, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
skill_xp_input.insert(0, "")
skill_xp_input.grid(row=3, column=1)

# Style the button
search_button = Button(root, text="Offical Hiscores\nSearch", command=check_boxes, width=20)
search_button.grid(row=4, column=1, columnspan=1)
search_button.configure(background="#c19a6b", foreground="#ffffff", activebackground="#a6805e", activeforeground="#ffffff")

# Style the button


# Button to toggle ironman status
ironman_button = Button(root, text="Ironman: OFF", width=20, bg='#3498db', fg='#ffffff',
                        activebackground='#2980b9', activeforeground='#ffffff', command=toggle_ironman)
ironman_button.grid(row=4, column=0)

# Style for Command Console Label Frame
console_frame = LabelFrame(root, text="Command Console", padx=5, pady=5, bg='#0f2b5a', fg='#ffffff')
console_frame.grid(row=5, column=0, columnspan=3, rowspan=4, sticky="nsew")

# Text widget for console output
console_output = Text(console_frame, height=20, width=50, wrap=WORD, bg='#d9d9d9', fg='#000000', padx=5)
console_output.pack(fill=BOTH, expand=True)

# Button setup with your custom styles
update_button = Button(root,
                       text="Update Players on\n"
                            "WiseOldMan.net",
                       command=lambda: update_wom(found_players),  # Trigger update_wom with found_players when clicked
                       width=20)
update_button.grid(row=9, column=0, padx=5)  # Adjust the row, column, and span as needed
update_button.configure(background="#c19a6b", foreground="#ffffff",
                        activebackground="#a6805e", activeforeground="#ffffff")

# Button setup with your custom styles
verify_search = Button(root,
                          text="Verify\nUsers",
                          command=lambda: open_popup(),  # Open highscores for all players
                          width=20)
verify_search.grid(row=9, column=1)  # Adjust the row, column, and span as needed
verify_search.configure(background="#c19a6b", foreground="#ffffff",
                           activebackground="#a6805e", activeforeground="#ffffff")

# Button setup with your custom styles
highscore_button = Button(root,
                       text="Open Offical\n Hiscores",
                       command=lambda: open_highscores(found_players),  # Open highscores for all players
                       width=20)
highscore_button.grid(row=9, column=2)  # Adjust the row, column, and span as needed
highscore_button.configure(background="#c19a6b", foreground="#ffffff",
                        activebackground="#a6805e", activeforeground="#ffffff")

discord = Label(root, text="Discord: jhandeeee", fg='#ffffff', bg='#0f2b5a', width=20)
discord.grid(row=10, column=0, sticky="SW")  # Aligns the label to the left (west)

rsn = Label(root, text="RSN: PhyrWall, ShinyRedDino",fg='#ffffff', bg='#0f2b5a')
rsn.grid(row=10, column=2, sticky="SE")  # Aligns the label to the left (west)

# Open hiscores for all players found
def open_highscores(players):
    base_url = f'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1='
    for player in players:
        if len(players) > 20:
            time.sleep(0.2)
        webbrowser.open(base_url + str(player))

# Update players on wiseoldman
async def update_wom_async(players):
    update_button.configure(state=DISABLED)
    search_button.configure(state=DISABLED)
    highscore_button.configure(state=DISABLED)
    # await client_wom.start()
    root.after(0, console_output.insert, END, f"Updating {len(players)} players on Wiseoldman.net\n"
                                              f"There will be a 3 second delay between each player being updated")
    for player in players:
        await client_wom.players.update_player(player)
        time.sleep(3)
        root.after(0, console_output.insert, END, f"{player} updated\n")
    # await client_wom.close()
    update_button.configure(state=NORMAL)
    search_button.configure(state=NORMAL)
    highscore_button.configure(state=NORMAL)

def update_wom(players):
    def run_update():
        asyncio.run(update_wom_async(players))  # Run the async function in the thread

    thread = threading.Thread(target=run_update)
    thread.daemon = True  # Daemon threads will exit when the main program exits
    thread.start()

def open_popup():
    verify_win = Toplevel(root)
    verify_win.geometry("800x300")
    verify_win.title("Verify Player")
    verify_win.config(bg="#0f2b5a")

    title = Label(verify_win, text="Deep Search", font=("Arial",18), bg="#0f2b5a",fg="BLACK")
    title.grid(row=0, column=0, columnspan=6, sticky="n")

    # Images pulled from WiseOldMan.net
    # Load the image and keep a reference
    attack_image = PhotoImage(file="assets/metrics/attack.png")
    strength_image = PhotoImage(file="assets/metrics/strength.png")
    defence_image = PhotoImage(file="assets/metrics/defence.png")
    ranged_image = PhotoImage(file="assets/metrics/ranged.png")
    prayer_image = PhotoImage(file="assets/metrics/prayer.png")
    magic_image = PhotoImage(file="assets/metrics/magic.png")
    runecrafting_image = PhotoImage(file="assets/metrics/runecrafting.png")
    construction_image = PhotoImage(file="assets/metrics/construction.png")
    hitpoints_image = PhotoImage(file="assets/metrics/hitpoints.png")
    agility_image = PhotoImage(file="assets/metrics/agility.png")
    herblore_image = PhotoImage(file="assets/metrics/herblore.png")
    thieving_image = PhotoImage(file="assets/metrics/thieving.png")
    crafting_image = PhotoImage(file="assets/metrics/crafting.png")
    fletching_image = PhotoImage(file="assets/metrics/fletching.png")
    slayer_image = PhotoImage(file="assets/metrics/slayer.png")
    hunter_image = PhotoImage(file="assets/metrics/hunter.png")
    mining_image = PhotoImage(file="assets/metrics/mining.png")
    smithing_image = PhotoImage(file="assets/metrics/smithing.png")
    fishing_image = PhotoImage(file="assets/metrics/fishing.png")
    cooking_image = PhotoImage(file="assets/metrics/cooking.png")
    firemaking_image = PhotoImage(file="assets/metrics/firemaking.png")
    woodcutting_image = PhotoImage(file="assets/metrics/woodcutting.png")
    farming_image = PhotoImage(file="assets/metrics/farming.png")


    # Column 1
    attack_label = Label(verify_win, image=attack_image, bg="#0f2b5a")
    attack_label.grid(row=1, column=0)  # Adjust the grid as needed
    attack_label.image = attack_image

    attack_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    attack_level_entry.grid(row=1,column=1)

    strength_label = Label(verify_win, image=strength_image, bg="#0f2b5a")
    strength_label.grid(row=2, column=0)  # Adjust the grid as needed
    strength_label.image = strength_image

    strength_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    strength_level_entry.grid(row=2,column=1)

    defence_label = Label(verify_win, image=defence_image, bg="#0f2b5a")
    defence_label.grid(row=3, column=0)  # Adjust the grid as needed
    defence_label.image = defence_image

    defence_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    defence_level_entry.grid(row=3,column=1)

    # Create the label with the image inside the popup (verify_win)
    ranged_label = Label(verify_win, image=ranged_image, bg="#0f2b5a")
    ranged_label.grid(row=4, column=0)  # Adjust the grid as needed
    ranged_label.image = ranged_image

    ranged_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    ranged_level_entry.grid(row=4,column=1)

    prayer_label = Label(verify_win, image=prayer_image, bg="#0f2b5a")
    prayer_label.grid(row=5, column=0)  # Adjust the grid as needed
    prayer_label.image = prayer_image

    prayer_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    prayer_level_entry.grid(row=5   ,column=1)

    magic_label = Label(verify_win, image=magic_image, bg="#0f2b5a")
    magic_label.grid(row=6, column=0)  # Adjust the grid as needed
    magic_label.image = magic_image

    magic_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    magic_level_entry.grid(row=6,column=1)

    runecrafting_label = Label(verify_win, image=runecrafting_image, bg="#0f2b5a")
    runecrafting_label.grid(row=7, column=0)  # Adjust the grid as needed
    runecrafting_label.image = runecrafting_image

    runecrafting_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    runecrafting_level_entry.grid(row=7,column=1)

    construction_label = Label(verify_win, image=construction_image, bg="#0f2b5a")
    construction_label.grid(row=8, column=0)  # Adjust the grid as needed
    construction_label.image = construction_image

    construction_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    construction_level_entry.grid(row=8,column=1)


    # Column 2
    hitpoints_label = Label(verify_win, image=hitpoints_image, bg="#0f2b5a")
    hitpoints_label.grid(row=1, column=2)  # Adjust the grid as needed
    hitpoints_label.image = hitpoints_image

    hitpoints_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    hitpoints_level_entry.grid(row=1,column=3)

    agility_label = Label(verify_win, image=agility_image, bg="#0f2b5a")
    agility_label.grid(row=2, column=2)  # Adjust the grid as needed
    agility_label.image = agility_image

    agility_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    agility_level_entry.grid(row=2,column=3)

    herblore_label = Label(verify_win, image=herblore_image, bg="#0f2b5a")
    herblore_label.grid(row=3, column=2)  # Adjust the grid as needed
    herblore_label.image = herblore_image

    herblore_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    herblore_level_entry.grid(row=3,column=3)

    # Create the label with the image inside the popup (verify_win)
    thieving_label = Label(verify_win, image=thieving_image, bg="#0f2b5a")
    thieving_label.grid(row=4, column=2)  # Adjust the grid as needed
    thieving_label.image = thieving_image

    thieving_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    thieving_level_entry.grid(row=4,column=3)

    crafting_label = Label(verify_win, image=crafting_image, bg="#0f2b5a")
    crafting_label.grid(row=5, column=2)  # Adjust the grid as needed
    crafting_label.image = crafting_image

    crafting_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    crafting_level_entry.grid(row=5   ,column=3)

    fletching_label = Label(verify_win, image=fletching_image, bg="#0f2b5a")
    fletching_label.grid(row=6, column=2)  # Adjust the grid as needed
    fletching_label.image = fletching_image

    fletching_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    fletching_level_entry.grid(row=6,column=3)

    slayer_label = Label(verify_win, image=slayer_image, bg="#0f2b5a")
    slayer_label.grid(row=7, column=2)  # Adjust the grid as needed
    slayer_label.image = slayer_image

    slayer_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    slayer_level_entry.grid(row=7,column=3)

    hunter_label = Label(verify_win, image=hunter_image, bg="#0f2b5a")
    hunter_label.grid(row=8, column=2)  # Adjust the grid as needed
    hunter_label.image = hunter_image

    hunter_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    hunter_level_entry.grid(row=8,column=3)

    # Column 3
    mining_label = Label(verify_win, image=mining_image, bg="#0f2b5a")
    mining_label.grid(row=1, column=4)  # Adjust the grid as needed
    mining_label.image = mining_image

    mining_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    mining_level_entry.grid(row=1,column=5)

    smithing_label = Label(verify_win, image=smithing_image, bg="#0f2b5a")
    smithing_label.grid(row=2, column=4)  # Adjust the grid as needed
    smithing_label.image = smithing_image

    smithing_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    smithing_level_entry.grid(row=2,column=5)

    fishing_label = Label(verify_win, image=fishing_image, bg="#0f2b5a")
    fishing_label.grid(row=3, column=4)  # Adjust the grid as needed
    fishing_label.image = fishing_image

    fishing_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    fishing_level_entry.grid(row=3,column=5)

    # Create the label with the image inside the popup (verify_win)
    cooking_label = Label(verify_win, image=cooking_image, bg="#0f2b5a")
    cooking_label.grid(row=4, column=4)  # Adjust the grid as needed
    cooking_label.image = cooking_image

    cooking_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    cooking_level_entry.grid(row=4,column=5)

    firemaking_label = Label(verify_win, image=firemaking_image, bg="#0f2b5a")
    firemaking_label.grid(row=5, column=4)  # Adjust the grid as needed
    firemaking_label.image = firemaking_image

    firemaking_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    firemaking_level_entry.grid(row=5   ,column=5)

    woodcutting_label = Label(verify_win, image=woodcutting_image, bg="#0f2b5a")
    woodcutting_label.grid(row=6, column=4)  # Adjust the grid as needed
    woodcutting_label.image = woodcutting_image

    woodcutting_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    woodcutting_level_entry.grid(row=6,column=5)

    farming_label = Label(verify_win, image=farming_image, bg="#0f2b5a")
    farming_label.grid(row=7, column=4)  # Adjust the grid as needed
    farming_label.image = farming_image

    farming_level_entry = Entry(verify_win, width=15, bg='#d9d9d9', fg='#000000')  # Light gray input box with black text
    farming_level_entry.grid(row=7,column=5)

    verify_button = Button(verify_win,
                              text="Player Search",
                              command=verify_players,
                              width=20)
    verify_button.grid(row=9, column=3, columnspan=3)
    verify_button.configure(background="#c19a6b", foreground="#ffffff",
                               activebackground="#a6805e", activeforeground="#ffffff")


    # # Command Console setup
    # console_frame = LabelFrame(verify_win, text="Command Console", padx=5, pady=5, bg='#0f2b5a', fg='#ffffff')
    #
    # # Position the console on the right side spanning all rows
    # console_frame.grid(row=1, column=6, rowspan=9, sticky="nsew", padx=5, pady=5)
    #
    # # Configure the grid so that the console expands
    # verify_win.grid_columnconfigure(6, weight=1)
    # verify_win.grid_rowconfigure(1, weight=1)
    #
    # # Text widget for console output inside the console frame
    # console_output = Text(console_frame, height=20, width=40, wrap=WORD, bg='#d9d9d9', fg='#000000')
    # console_output.pack(fill=BOTH, expand=True)

def verify_players():
    print(found_players)
    hiscore_player_dict()

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



def disable_buttons():
    update_button.configure(state=DISABLED)
    highscore_button.configure(state=DISABLED)
    search_button.configure(state=DISABLED)
    rsn_search_button.configure(state=DISABLED)
    ironman_button.configure(state=DISABLED)
    verify_search.configure(state=DISABLED)
    drop.config(state=DISABLED)

def enable_buttons():
    update_button.configure(state=NORMAL)
    highscore_button.configure(state=NORMAL)
    search_button.configure(state=NORMAL)
    rsn_search_button.configure(state=NORMAL)
    ironman_button.configure(state=NORMAL)
    verify_search.configure(state=NORMAL)
    drop.config(state=NORMAL)

def hiscore_player_dict():
    for player_name in found_players:
        url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={player_name}"

        response = requests.get(url)
        if response.status_code != 200:
            return None

        hiscore_dict = {}
        skills = [
            'Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer', 'Magic', 'Cooking',
            'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 'Herblore',
            'Agility', 'Thieving', 'Slayer', 'Farming', 'Runecrafting', 'Hunter', 'Construction'
        ]

        player_data = StringIO(response.text)
        reader = csv.reader(player_data)

        for i, row in enumerate(reader):
            if i < len(skills):
            # Assign data to the corresponding skill
             hiscore_dict[skills[i]] = {
                'rank': int(row[0]),
                'level': int(row[1]),
                'experience': int(row[2])
            }
        print(hiscore_dict)
        return hiscore_dict


# Label for when error occurs in the check_boxes function
error_label = Label(text="Please verify your entries", fg='red')
error_label_rsn = Label(text="No skill data for RSN", fg='red')
error_label_502 = Label(text="Please wait to send another request", fg='red')

if __name__ == '__main__':
    root.mainloop()
