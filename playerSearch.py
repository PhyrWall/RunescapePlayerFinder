import requests
from bs4 import BeautifulSoup

# Ask for skill and target XP
skill = input(
    "What skill do you want to search?\n1. Herblore\n2. Farming\n3. Runecrafting\n4. Agility\n5. Crafting\nSelect a skill: ")
target_xp = int(input("Enter the target XP: "))
rank = int(input("What is the current rank? "))

# Calculate the starting page based on the rank
page = int(rank / 25) - 1 - 5  # Adjusted to start from a more accurate page based on rank


# Function to select URL based on skill
def url_select(skill, page):
    if skill == '1':
        return f'https://secure.runescape.com/m=hiscore_oldschool/overall?table=16&page={page}'  # Herblore
    elif skill == '2':
        return f'https://secure.runescape.com/m=hiscore_oldschool/overall?table=20&page={page}'  # Farming
    elif skill == '3':
        return f'https://secure.runescape.com/m=hiscore_oldschool/overall?table=21&page={page}'  # Runecrafting
    elif skill == '4':
        return f'https://secure.runescape.com/m=hiscore_oldschool/overall?table=17&page={page}'  # Runecrafting
    elif skill == '5':
        return f'https://secure.runescape.com/m=hiscore_oldschool/overall?table=13&page={page}' # Crafting
    else:
        return ""


# Function to search the webpage
def search_webpage(skill, target_xp, start_page):
    print("Searching for player...")
    for page in range(start_page, start_page + 20):  # Loop through 10 pages after the starting page
        url = url_select(skill, page)
        if not url:
            print("Invalid skill number or page. Please try again.")
            return

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            player_rows = soup.find_all('tr', class_='personal-hiscores__row')

            for row in player_rows:
                name_link = row.find('td', class_='left').find('a')
                if name_link:  # Ensure there's a link
                    name = name_link.text.replace('\xa0', ' ')
                    xp_cells = row.find_all('td', class_='right')
                    if xp_cells and len(xp_cells) > 1:
                        xp_text = xp_cells[-1].text.replace(',', '').strip()
                        xp = int(xp_text) if xp_text.isdigit() else None

                        if xp and xp == target_xp:
                            print(f"Found {name} with target XP")
        else:
            print(f"Failed to fetch the high scores page. Status code: {response.status_code}")
            break  # Exit the loop if a page fails to load


# Call the function with the selected skill, target XP, and starting page
if __name__ == '__main__':
    search_webpage(skill, target_xp, page)