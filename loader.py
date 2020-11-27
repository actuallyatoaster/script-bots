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
    fireRate = weaponsJson["fireRate"]
    texture = None #TODO: image loading here
    damage = weaponsJson["damage"]
    rad = weaponsJson["projColRad"]

    return bots.Equipment(sName, projSpeed,  fireRate, texture, damage, rad)


def calculateBotCost(name):
    pass

def createBotFromFile(name, arena, baseColRad=5, baseSpeed = 75, typeFile = "bots/enemies.json"):
    #Need: arena, equipment, script, colRad, position, health, speed

    pass

def createRandomEnemy(name, arena, position)
    pass

def createEnemyWave(arena, amount):
    pass

def loadJsonFromFile(path, cache):
    if path in cache:
        return cache[path]

    with open(path, 'r') as f:
        data = f.read()
    #print(data)
    parsed = json.loads(data)
    cache[path] = parsed
    return parsed