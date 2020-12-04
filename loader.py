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

def calculateBotCost(name, typeFile = 'bots/enemies.json', baseCost=350, botJson=None):
    if botJson == None:
        botJson = loadJsonFromFile(typeFile)[name]
    costSum = baseCost
    eqJson = loadJsonFromFile('bots/equipment.json')
    for weapon in botJson["weapons"]:
        costSum += eqJson["weapons"][weapon]["cost"]
    
    for buff in botJson["buffs"]:
        costSum += eqJson["buffs"][buff]["cost"]
    
    return costSum



def createBotFromFile(name, arena, position, baseHealth = 60, baseColRad=5, baseSpeed = 75, typeFile = "bots/enemies.json", isEnemy=False):
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


    newBot = bots.Bot(arena, equipment, script, baseColRad, position, baseHealth*mod, baseSpeed, isEnemy=isEnemy, reward=reward,name=name )

    return newBot

def saveBotToFile(bot, botJson, typeFile = 'bots/bots.json'):
    fileJson = loadJsonFromFile(typeFile)
    fileJson[bot] = botJson
    jsonStr = json.dumps(fileJson, indent=4)

    with open(typeFile, 'w') as f:
        f.write(jsonStr)
        print("wrote to file")
        f.close()


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

#Returns weapons, buffs
# Where each is a list of 3-tuples taking the form
# (name, Display Name, Cost)
def makeEquipmentList():
    equipmentJson = loadJsonFromFile('bots/equipment.json')
    weapons, buffs = [], []

    for weapon in equipmentJson["weapons"]:
        weapons.append((weapon, equipmentJson["weapons"][weapon]["displayName"],
            equipmentJson["weapons"][weapon]["cost"]))
    
    for buff in equipmentJson["buffs"]:
        buffs.append((buff, equipmentJson["buffs"][buff]["displayName"],
            equipmentJson["buffs"][buff]["cost"]))
    
    return weapons, buffs

def botHasEquipment(botName, equipmentName, typeFile='bots/bots.json'):
    fileJson = loadJsonFromFile(typeFile)
    return(equipmentName in fileJson[botName]["weapons"] or
           equipmentName in fileJson[botName]["buffs"])

def loadJsonFromFile(path):

    with open(path, 'r') as f:
        data = f.read()
        f.close()
    #print(data)
    parsed = json.loads(data)
    return parsed