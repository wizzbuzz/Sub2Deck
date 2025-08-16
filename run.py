import pick
import os
import txt_to_csv
import csv_to_anki


print(" _______  __   __  _______  _______  ______   _______  _______  ___   _ \n|       ||  | |  ||  _    ||       ||      | |       ||       ||   | | |\n|  _____||  | |  || |_|   ||____   ||  _    ||    ___||       ||   |_| |\n| |_____ |  |_|  ||       | ____|  || | |   ||   |___ |       ||      _|\n|_____  ||       ||  _   | | ______|| |_|   ||    ___||      _||     |_ \n _____| ||       || |_|   || |_____ |       ||   |___ |     |_ |    _  |\n|_______||_______||_______||_______||______| |_______||_______||___| |_|\n")
input("Press Enter to continue...")
options = ["[Convert subtitles to csv word list]", "[Convert csv word list to anki deck]","[Exit]"]
option, index = pick.pick(options, "\nPlease select an action:", indicator='=>', default_index=0)


match option:
    case "[Convert subtitles to csv word list]":
        txt_to_csv.main()
    case "[Convert csv word list to anki deck]":
        csv_to_anki.main()
    case "[Exit]":
        print("Exit")