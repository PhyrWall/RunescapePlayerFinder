from tkinter import ttk,Tk,Label,Entry
import requests


root = Tk()

root.minsize(height=100, width=300)
root.title("Find Runescape Player")

label_SkillSearch = Label(text="Player "
                               "Skill: ")
label_SkillSearch.grid(row=0,column=0)

combo = ttk.Combobox(
    state="readonly",
    values=["Agility", "Fishing", "Herblore"],width=15
)
combo.grid(row=0,column=1)

label_PlayerRank = Label(text="Player Rank: ")
label_PlayerRank.grid(row=1,column=0)
input_playerRank = Entry(width=15)
input_playerRank.grid(row=1,column=1)

label_SkillXp = Label(text="Player Xp: ")
label_SkillXp.grid(row=2,column=0)
input_SkillXp = Entry(width=15)
input_SkillXp.grid(row=2,column=1)

root.mainloop()