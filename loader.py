'''
This file contains functions that parse the json and scripts in the bots folder
to generate actual Bot objects for the game to use
'''
import bots
import json
import random

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

def createBotFromFile(name, arena, position, baseHealth = 25, baseColRad=5, baseSpeed = 75, typeFile = "bots/enemies.json", isEnemy=False):
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

    if "reward" in botJson:
        reward = botJson["reward"]
    else: reward = 0

    newBot = bots.Bot(arena, equipment, script, baseColRad, position, baseHealth*mod, baseSpeed, isEnemy=isEnemy, reward=reward)

    return newBot

def createRandomEnemy(arena, position):
    enemyData = loadJsonFromFile('bots/enemies.json')#this would be bad if it weren't cached
    #sum up the frequencies of each bot, choose a number between
    #0 and the sum, and create the corresponding bot
    freqSum = 0
    for enemyBot in enemyData:
        freqSum += enemyData[enemyBot]["frequency"]
    choice = random.randint(1, freqSum)
    choiceSum = 0
    for enemyBot in enemyData:
        choiceSum += enemyData[enemyBot]["frequency"]
        if choiceSum >= choice:
            return createBotFromFile(enemyBot, arena, position, isEnemy=True)
    
#returns whether position is within bounds
def withinBounds(position, minBound, maxBound):
    return (minBound[0] <= position[0] <= maxBound[0] and
            minBound[1] <= position[1] <= maxBound[1])

def createEnemyWave(arena, amount):
    for i in range(amount):
        
        #Requires arena size greater than 200x200
        botPosition = (arena.dims[0]//2, arena.dims[1]//2)

        #choose a position on outer 100 margin of arena
        while withinBounds(botPosition, (100,100), (arena.dims[0]-100, arena.dims[1]-100)):
            botPosition = (random.randint(0, arena.dims[0]), random.randint(0, arena.dims[1]))
        newBot = createRandomEnemy(arena, botPosition)
        arena.enemyBots.append(newBot)

def loadJsonFromFile(path, cache=dict()):
    if path in cache: #This abuses the fact that the dict acts like a global variable
        return cache[path]

    with open(path, 'r') as f:
        data = f.read()
    #print(data)
    parsed = json.loads(data)
    cache[path] = parsed
    return parsed