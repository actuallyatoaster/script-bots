# BotArena

Final project for 15-112.

BotArena is a programming-based, tower defense-esque game where the player must defend a central objective from increasingly difficult waves of enemy bots. A “bot” is a character (created either by the player or as an enemy) with two components: a list of equipment/upgrades, and a controlling script. When creating a bot, the player must choose what equipment and upgrades to give the bot, which each cost an amount of money (which is rewarded for destroying enemy bots). Once the loadout is chosen, the player must write a script that will determine how the bot behaves. This script is written in the BotScript language, a minimalist language interpreted in python created specifically for the purpose of controlling these bots. The script allows the player to control the bot’s movement and weapons based on external variables such as its position, the position of nearby enemies, and the number of enemies currently in the Arena. The goal of the game is to maximize your score, which is achieved by surviving as long as possible. 

To play the game, run the main.py file.

 To learn how to use BotScript, open the in-game help screen or the equivalent help.txt file.
