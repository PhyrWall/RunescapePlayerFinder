"""
GUI tool to search for Old School RuneScape players (based on their rank/xp), track their rank and XP in specific skills,
and interact with the Wise Old Man API for player updates. Developed by PhyrWall
All Images were pulled from the WiseOldMan GitHub
https://github.com/wise-old-man/wise-old-man/tree/master/app/public/img/metrics
"""

import os
import threading
import sys
import time
import csv
from io import StringIO
from tkinter import *
from webbrowser import open

import requests
import wom as wom
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

# Function to find the correct path to assets
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller's onefile mode """
    try:
        # PyInstaller creates a temporary folder named _MEIPASS where bundled files are stored
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = Tk()
root.title("Runescape Player Finder")
root.iconbitmap(resource_path('assets\\icon.ico'))
root.minsize(height=530, width=430)
root.configure(background='#0f2b5a')

client_wom = wom.Client(api_base_url="https://api.wiseoldman.net/v2")

def get_details():
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
    else:
        print(f"Failed to retrieve data. Status code: {data.status_code}")
        error_label.grid(row=0, column=2)

def clear_console():
    # Clear all the text
    console_output.delete(1.0, END)

# Start searching for player (getting data from widgets)
def search_player(rank, skil_xp):
    clear_console()
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


    # Starting page is 6 pages sooner for page differences, this is where it will start web scraping
    page = int(rank / 25) -  6
    if page <= 0:
        page = 1
    if mode == 1: # Ironman
        url = f'https://secure.runescape.com/m=hiscore_oldschool_ironman/overall?table={runescape_skills[clicked.get()]}&page='
    elif mode == 2: # HC Ironman
        url = f'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/overall?table={runescape_skills[clicked.get()]}&page='
    else: # Main
        url = f'https://secure.runescape.com/m=hiscore_oldschool/overall?table={runescape_skills[clicked.get()]}&page='

    # Run the search in a daemon thread
    thread = threading.Thread(target=hiscore_webscrape, args=(url, skil_xp, page, rank))
    thread.daemon = True
    thread.start()

# webscrape the hiscores
def hiscore_webscrape(url, target_xp, page, rank):

    found_players.clear()

    # Disable buttons while running
    disable_buttons()

    # Determine starting page number
    if page-10 <= 1:
        start_page = 1
    else:
        start_page = int(rank/25)-2

    end_page = start_page + 7

    # Declare account type
    account_type = mode
    if account_type == 0:
        account_type = "Main"
    elif account_type == 1:
        account_type = "Ironman"
    else:
        account_type = "Hardcore Ironman"


    root.after(0, console_output.insert, END, f"Searching for player\nSkill: {clicked.get()}\nTarget XP: {target_xp}\nEstimated Rank: {rank}\nAccount type: {account_type}\n--------------------\n")
    for page in range(start_page, end_page):

        print(page)
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
        time.sleep(0.2)
    root.after(0, console_output.insert, END, f"\nFinished searching ({len(found_players)} players found)\n")

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

# Starts as main account (0 = Main, 1 = Ironman, 2 = Hardcore Ironman)
mode = 0
def toggle_ironman():
    global mode

    mode = (mode + 1) % 3

    # Button text and appearance based on the current mode
    if mode == 0:
        ironman_button.config(text="Main", bg='#4169E1', activebackground='#4169E1')
    elif mode == 1:
        ironman_button.config(text="Ironman", bg='#7A7977', activebackground='#7A7977')
    elif mode == 2:
        ironman_button.config(text="Hardcore Ironman", bg='#FF4500', activebackground='#FF4500')

found_players = []

skill_choices = [
    'Agility', 'Attack', 'Construction', 'Cooking', 'Crafting', 'Defence',
    'Farming', 'Firemaking', 'Fishing', 'Fletching', 'Herblore', 'Hitpoints',
    'Hunter', 'Magic', 'Mining', 'Prayer', 'Ranged', 'Runecrafting',
    'Slayer', 'Smithing', 'Strength', 'Thieving', 'Woodcutting'
]
clicked = StringVar()
clicked.set(skill_choices[1])

player_skill = Label(root, text="Player Skill: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
player_skill.grid(row=0, column=0)

# Style for the drop-down menu
drop = OptionMenu(root, clicked, *skill_choices)
drop.config(width=10, bg='#c19a6b', fg='#ffffff', activebackground='#a6805e', activeforeground='#ffffff')
drop.grid(row=0, column=1)

# Entry fields/labels for player rank
rsn_search = Entry(root, width=15, bg='#d9d9d9', fg='#000000')
rsn_search.grid(row=1, column=0)
rsn_search.insert(0, "RSN")
rsn_search_button = Button(root, text="Search WiseOldMan.net", command=get_details, width=20)
rsn_search_button.grid(row=1, column=1)
rsn_search_button.configure(background="#c19a6b", foreground="#ffffff", activebackground="#a6805e", activeforeground="#ffffff")

# Entry fields/labels for player rank
player_rank = Label(root, text="Player Rank: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
player_rank.grid(row=2, column=0)
player_rank_input = Entry(root, width=15, bg='#d9d9d9', fg='#000000')
player_rank_input.grid(row=2, column=1)
player_rank_input.insert(0, "")

# Entry fields/labels for skill Xp
skill_xp = Label(root, text="Skill Xp: ", width=10, fg='#ffffff', bg='#0f2b5a',anchor='w')
skill_xp.grid(row=3, column=0)
skill_xp_input = Entry(root, width=15, bg='#d9d9d9', fg='#000000')
skill_xp_input.insert(0, "")
skill_xp_input.grid(row=3, column=1)

# Style the button
search_button = Button(root, text="Offical Hiscores\nSearch", command=check_boxes, width=20)
search_button.grid(row=4, column=1, columnspan=1)
search_button.configure(background="#c19a6b", foreground="#ffffff", activebackground="#a6805e", activeforeground="#ffffff")

# Style the button


# Button to toggle ironman status
ironman_button = Button(root, text="Main", width=15, bg='#4169E1', fg='#ffffff',
                        activebackground='#4169E1', activeforeground='#ffffff', command=toggle_ironman)
ironman_button.grid(row=4, column=0)

# Style for Command Console Label Frame
console_frame = LabelFrame(root, text="Command Console", padx=5, pady=5, bg='#0f2b5a', fg='#ffffff')
console_frame.grid(row=5, column=0, columnspan=3, rowspan=4, sticky="nsew")

# Text widget for console output
console_output = Text(console_frame, height=20, width=50, wrap=WORD, bg='#d9d9d9', fg='#000000', padx=5)
console_output.pack(fill=BOTH, expand=True)

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
    for runescape_rsn in players:
        if len(players) > 20:
            time.sleep(0.2)
        open(base_url + str(runescape_rsn))

image_path = resource_path('assets/app_logo.png')
if os.path.exists(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((100, 100))  # Resize to 100x100 pixels

    photo = ImageTk.PhotoImage(resized_image)

    # Store the reference to the PhotoImage object to avoid garbage collection
    image_label = Label(root, image=photo)
    image_label.image = photo
    image_label.grid(row=0, column=2, rowspan=4, padx=10, pady=10)
else:
    print(f"Error: {image_path} not found. Please check the file path.")


def disable_buttons():
    highscore_button.configure(state=DISABLED)
    search_button.configure(state=DISABLED)
    rsn_search_button.configure(state=DISABLED)
    ironman_button.configure(state=DISABLED)
    compare_button.configure(state=DISABLED)
    drop.config(state=DISABLED)
    rsn_search.config(state=DISABLED)

def enable_buttons():
    rsn_search.configure(state=NORMAL)
    highscore_button.configure(state=NORMAL)
    search_button.configure(state=NORMAL)
    rsn_search_button.configure(state=NORMAL)
    ironman_button.configure(state=NORMAL)
    compare_button.configure(state=NORMAL)
    drop.config(state=NORMAL)


class PlayerHiscore:
    def __init__(self, player_name, from_wom=False):
        self.player_name = player_name
        self.hiscore_dict = {}
        self.skills = [
            'Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer', 'Magic', 'Cooking',
            'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 'Herblore',
            'Agility', 'Thieving', 'Slayer', 'Farming', 'Runecrafting', 'Hunter', 'Construction'
        ]

        if from_wom:
            self.get_wom_player_hiscores()  # Fetch data from Wise Old Man API
        else:
            self.get_player_hiscores()  # Fetch data from RuneScape Hiscores Using Lite Hiscores

    # Fetch player data from Wise Old Man API
    def get_wom_player_hiscores(self):
        url = f"https://api.wiseoldman.net/v2/players/{self.player_name}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {self.player_name} from WOM. Status code: {response.status_code}")
            return None

        data = response.json()
        skills_data = data.get('latestSnapshot', {}).get('data', {}).get('skills', {})

        for skill in self.skills:
            skill_lower = skill.lower()
            skill_info = skills_data.get(skill_lower, None)

            # If the skill data exists, store it, else set to None
            if skill_info:
                self.hiscore_dict[skill] = {
                    'rank': skill_info.get('rank', None),
                    'level': skill_info.get('level', None),
                    'experience': skill_info.get('experience', None)
                }
            else:
                self.hiscore_dict[skill] = {'rank': None, 'level': None, 'experience': None}

    # Fetch player data from RuneScape Hiscores API
    def get_player_hiscores(self):
        url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={self.player_name}"
        if mode == 1:
            url = f"https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player={self.player_name}"
        elif mode == 2:
            url = f"https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws?player={self.player_name}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {self.player_name}. Status code: {response.status_code}")
            return None

        player_data = StringIO(response.text)
        reader = csv.reader(player_data)

        for i, row in enumerate(reader):
            if i < len(self.skills):
                try:
                    rank = int(row[0])
                    level = int(row[1])
                    experience = int(row[2])
                except (ValueError, IndexError):
                    rank = None
                    level = None
                    experience = None

                self.hiscore_dict[self.skills[i]] = {
                    'rank': rank,
                    'level': level,
                    'experience': experience
                }
        time.sleep(1)

    def get_hiscore_dict(self):
        return self.hiscore_dict

# Compare orininal player and found player(s) and return match percent
def compare_players_skills(original_player, found_player):
    match_score = 0
    skills_compared = 0

    original_skills = original_player.get_hiscore_dict()
    found_skills = found_player.get_hiscore_dict()

    # Compare each skill based on experience
    for skill in original_player.skills:
        original_experience = original_skills.get(skill, {}).get('experience', None)
        found_experience = found_skills.get(skill, {}).get('experience', None)
        original_level = original_skills.get(skill, {}).get('level', None)
        found_level = found_skills.get(skill, {}).get('level', None)



        skills_compared +=1
        # If player level is equal to found level 0.4 points
        if original_level == found_level:
            match_score += 0.4
            # If player xp is equal to found xp 0.6 points (higher points due to not as likely to change varience)
            if original_experience == found_experience:
                match_score += 0.6
            # If level is not same but within 5k xp, give 0.3 points
        # If both experiences are None or invalid (-1), give 1 point
        elif original_experience in [None, -1] or found_experience in [None, -1]:
            match_score += 1
        elif abs(original_experience - found_experience) <= 5000:
            match_score += 0.3

    # If no skills were compared, return 0
    if skills_compared == 0:
        return 0.0

    # Calculate the percentage (23 total skills)
    match_percentage = (match_score / skills_compared) * 100
    return match_percentage


# Find matches between the original player and found players
def find_matches_with_percentage(original_player_name):
    original_player = PlayerHiscore(original_player_name, from_wom=True)  # Original player from WOM

    match_results = {}
    for player_name in found_players:
        found_player = PlayerHiscore(player_name)  # Get hiscores of each found player
        match_percentage = compare_players_skills(original_player, found_player)
        match_results[player_name] = match_percentage

    return match_results


# Fetch names and display results
def fetch_compare_display_matches():
    disable_buttons()
    original_player_name = rsn_search.get()
    match_results = find_matches_with_percentage(original_player_name)

    root.after(0, console_output.insert, END, f"Matches for {original_player_name}:\n")

    # Output names into console
    for player, match_p in match_results.items():
        if match_p >= 75:
            root.after(0, console_output.insert, END, f"{player}: {match_p:.2f}%\n")
            root.after(0, console_output.see, END)  # Scroll to the end of the text box
    enable_buttons()

def fetch_compare_in_thread():
    thread = threading.Thread(target=fetch_compare_display_matches)
    thread.daemon = True  # Set the thread as a daemon so it will exit when the main program exits
    thread.start()

compare_button = Button(root, text="Compare\nPlayers", command=fetch_compare_in_thread, width=20)
compare_button.grid(row=9, column=0)
compare_button.configure(background="#c19a6b", foreground="#ffffff", activebackground="#a6805e", activeforeground="#ffffff")

# Labels for when error occurs in the check_boxes function
error_label = Label(text="Please verify your entries", fg='red')
error_label_rsn = Label(text="No skill data for RSN", fg='red')

if __name__ == '__main__':
    root.mainloop()
