# RuneScape Player Search Tool

A GUI tool for searching Old School RuneScape players based on their rank and XP, with the ability to interact with the 
Wise Old Man API for updating player data. It's particularly useful when you have player information from recent hiscores 
or other sources and need to find their RSN after a double name change.

## Features

### 1. Search Players by Skill Rank and XP
- Select a skill, input a target XP, and an estimated rank then click search.

### 2. Scraping Hiscores
- Checks multiple pages for players that match the XP criteria provided.
  - **Rank and Xp is required**

### 3. Display Player Search Results
- Players found are listed in the command console.

### 4. Update Players on Wise Old Man
- Update player data on the Wise Old Man (WOM) website via its API.
- There will be a 3-second delay between each "Found player" to avoid Wise Old Man's 20 requests per minute
  - Edit to the code can be made for use of API key

### 5. Open Hiscores in Web Browser
- Optional to open the hiscores page of any player found directly in the default web browser by clicking a button.
  - Searching again will erase the last found players

### 6. GUI Features
- Users can select a skill from a dropdown menu, input the player’s rank and XP, and search for that player.
- A command console displays output messages and search results.
- Buttons to search, update players on WOM, and open hiscores are styled and integrated into the GUI.
  
![img](https://github.com/user-attachments/assets/8db3099c-e33d-4023-b20a-2eadfec1723b)

## Requirements

To run this program, you need to install the following Python packages:
- `python 3.10`: Required to run the program.
- `requests`: for making HTTP requests to scrape data from the RuneScape hiscores.
- `BeautifulSoup`: for parsing HTML and extracting player information.
- `PIL` (Pillow): for image manipulation and resizing.
- `wom`: for interacting with the Wise Old Man API.

You can install the dependencies via 
```bash
pip install -r requirements.txt
```
Developer:
Discord: jhandeeee
RSN: PhyrWall, ShinyRedDino

