import scriptables
import time
import math
'''
This file contains classes defining bots, equipment for bots, projectiles, and
their associated behaviours. It also includes some helper functions for this
purpose
'''
SCRIPT_UPDATE_SPEED = 0.2

def pointDistance(x0, y0, x1, y1):
    return (((x0-x1)**2)+((y0-y1)**2))**(1/2)

def getEquipmentExternals(equipment):
    externals = dict()
    for item in equipment:
        for external in item.externals:
            externals[external] = item.externals[external]
    return externals

def cleanseLocals(locs):
    newLocs = dict()
    for var in locs:
        if var[0] == '$':
            newLocs[var] = locs[var]
    return newLocs

class Bot():

    def __init__(self, equipment, script, collisionRadius, position, health, speed):
        self.equipment = equipment
        for eq in self.equipment:
            eq.bot = self

        self.env = scriptables.ScriptEnvironment(script)
        self.pos = position
        self.health = health
        self.collisionRadius = collisionRadius
        self.lastScriptUpdate = 0
        self.speed = speed

        #Set up environment externals
        self.env.externals = getEquipmentExternals(self.equipment)
        self.env.externals["xMov"] = scriptables.ScriptNumber(0)
        self.env.externals["yMov"] = scriptables.ScriptNumber(0)

        self.env.constants["firstCall"] = scriptables.ScriptBoolean(True)
    
    def updateScriptConstants(self):
        self.env.constants["botX"] = scriptables.ScriptNumber(self.pos[0])
        self.env.constants["botY"] = scriptables.ScriptNumber(self.pos[1])


    def update(self, app, enemyBots, lines):
        
        if time.time() >= self.lastScriptUpdate + SCRIPT_UPDATE_SPEED:
            #Inject new variables into script environment
            self.env.locs = cleanseLocals(self.env.locs)
            self.updateScriptConstants()
            self.env.executeAll()
            self.lastScriptUpdate = time.time()
            self.env.constants["firstCall"] = scriptables.ScriptBoolean(False)

        #Update weapons
        for eq in self.equipment:
            #self.externals = {"direction":0, "fire":True}
            eq.update(self.env.externals)
            for projectile in eq.projectiles:
                projectile.update(app, enemyBots)

        #Update movement
        xVel, yVel = self.env.externals["xMov"].value, self.env.externals["yMov"].value
        if abs(xVel) > 1: xVel = xVel/abs(xVel)
        if abs(yVel) > 1: yVel = yVel/abs(xVel)
        self.pos = (self.pos[0] + self.speed*xVel,
                    self.pos[1] + self.speed*yVel)

    def draw(self, app, canvas):
        canvas.create_oval(self.pos[0] - self.collisionRadius, self.pos[1] - self.collisionRadius,
                           self.pos[0] + self.collisionRadius, self.pos[1] + self.collisionRadius,
                           fill = "blue")
    def damage(self, dmg):
        self.health -= dmg


class Projectile():

    def __init__(self, origin, projectileSpeed, projectileTexture, 
                 position, direction, collisionRadius, damage):
        self.origin = origin
        self.speed = projectileSpeed
        self.texture = projectileTexture
        self.pos = position
        self.direction = direction
        self.collisionRadius = collisionRadius
        self.damage = damage
    
    #Move the projectile and deal damage if needed
    def update(self, app, bots):
        xVel = self.speed * math.cos(self.direction)
        yVel = -1 * self.speed * math.sin(self.direction)
        self.pos = (self.pos[0] + xVel, self.pos[1] + yVel)

        #Outside arena
        if(self.pos[0] < 0 or self.pos[1] < 0 or
           self.pos[0] > app.arenaWidth or self.pos[1] > app.arenaHeight):
           self.origin.projectiles.remove(self) #Remove self from equipment projectile list
           return
        
        #Deal damage upon collsion
        collision = self.checkCollisions(bots)
        if collision != None:
            collision.damage(self.damage)
            self.origin.projectiles.remove(self)
    
    #Check if projectile is colliding with a bot in bots
    #If it is, return the bot. Otherwise, return None
    def checkCollisions(self, bots):
        for bot in bots:
            dist = pointDistance(bot.pos[0], bot.pos[1], self.pos[0], self.pos[1])
            if dist < self.collisionRadius:
                return bot
        return None

    #Draw the projectile
    def draw(self, app, canvas):
        canvas.create_oval(self.pos[0] - self.collisionRadius, self.pos[1] - self.collisionRadius,
                           self.pos[0] + self.collisionRadius, self.pos[1] + self.collisionRadius,
                           fill = "red")
        

class Equipment():
    def __init__(self, name, projectileSpeed, fireRate, projectileTexture, damage, projectileColRad):
        self.name = name
        self.projectileSpeed = projectileSpeed
        self.projectileColRad = projectileColRad
        self.fireCooldown = 1/fireRate
        self.projectileTexture = projectileTexture
        self.projectiles = []
        self.externals = {self.name+"Direction": scriptables.ScriptNumber(0),
                         self.name+"Fire": scriptables.ScriptBoolean(False)}
        self.lastFire = 0
        self.bot = None
        self.damage=damage
    
    def update(self, externals):
        if externals[self.name+"Fire"].value:
            if time.time() - self.lastFire >= self.fireCooldown:
                self.lastFire = time.time()
                #Create a new projectile
                newProjectile = Projectile(self, self.projectileSpeed, 
                    self.projectileTexture, self.bot.pos, externals[self.name+"Direction"].value,
                    self.projectileColRad, self.damage)
                self.projectiles.append(newProjectile)

