'''
This file contains functions that parse the json and scripts in the bots folder
to generate actual Bot objects for the game to use
'''
import bots
import json

def loadWeapon(name, arena):
    weaponJson = loadJsonFromFile('bots/equipment.json')["weapons"][name]
    sName = weaponJson["scriptName"]
    projSpeed = weaponJson["projectileSpeed"]
    fireRate = weaponJson["fireRate"]
    texture = None #TODO: image loading here
    damage = weaponJson["damage"]
    rad = weaponJson["projColRad"]

    return bots.Equipment(sName, projSpeed,  fireRate, texture, damage, rad)


def calculateBotCost(name):
    pass

def createBotFromFile(name, arena, position, baseHealth = 25, baseColRad=5, baseSpeed = 75, typeFile = "bots/enemies.json"):
    #Need: arena, equipment, script, colRad, position, health, speed
    botJson = loadJsonFromFile(typeFile)[name]
    #TODO: speed buffs
    equipment = [loadWeapon(eq, arena) for eq in botJson["weapons"]]

    with open(botJson["script"], 'r') as f:
        script = f.read()
        f.close()
    if "health" in botJson:
        mod = botJson["health"]
    else: mod = 1
    newBot = bots.Bot(arena, equipment, script, baseColRad, position, baseHealth*mod, baseSpeed)

    return newBot

def createRandomEnemy(name, arena, position):
    pass

def createEnemyWave(arena, amount):
    pass

def loadJsonFromFile(path, cache=dict()):
    if path in cache: #This abuses the fact that the dict acts like a global variable
        return cache[path]

    with open(path, 'r') as f:
        data = f.read()
    #print(data)
    parsed = json.loads(data)
    cache[path] = parsed
    return parsed