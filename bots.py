import scriptables
import time
import math
'''
This file contains classes defining bots, equipment for bots, projectiles, and
their associated behaviours. It also includes some helper functions for this
purpose
'''
SCRIPT_UPDATE_SPEED = 0.02 #Min time interval between script updates, increase this if performance issues

def pointDistance(x0, y0, x1, y1):
    return (((x0-x1)**2)+((y0-y1)**2))**(1/2)

def getClosestBot(pos, bots):
    nearest = None
    nearestDist = None
    for bot in bots:
        d = pointDistance(pos[0], pos[1], bot.pos[0], bot.pos[1])
        if  nearestDist == None or d < nearest:
            nearest = bot
    return nearest, nearestDist

#Take a tuple position and ensure its with 0 and the point bounds
def boundPosition(pos, bounds):
    newX = pos[0]
    newY = pos[1]
    newX = max(0, newX)
    newX = min(newX, bounds[0])
    newY = max(0, newY)
    newU = min(newY, bounds[1])
    return newX, newY


def getEquipmentExternals(equipment):
    externals = dict()
    for item in equipment:
        for external in item.externals:
            externals[external] = item.externals[external]
    return externals

def cleanseLocals(locs):
    newLocs = dict()
    for var in locs:
        if var[0] == '$': #preserve persistent variables
            newLocs[var] = locs[var]
    return newLocs

class Bot():

    def __init__(self, arena, equipment, script, collisionRadius, position, health, speed):
        self.arena = arena
        self.equipment = equipment
        for eq in self.equipment:
            eq.bot = self #Equipment needs to know what it's attached to

        self.env = scriptables.ScriptEnvironment(script)
        self.pos = position
        self.health = health
        self.collisionRadius = collisionRadius
        self.lastScriptUpdate = time.time()
        self.speed = speed
        #D_TIME for updates
        self.lastTime = time.time()
        #Set up environment externals
        self.env.externals = getEquipmentExternals(self.equipment)
        self.env.externals["move.speed"] = scriptables.ScriptNumber(0)
        self.env.externals["move.direction"] = scriptables.ScriptNumber(0)

        self.env.constants["FIRST_CALL"] = scriptables.ScriptBoolean(True)
        self.env.constants["pi"] = scriptables.ScriptNumber(math.pi)

        self.env.constants["A_WIDTH"] = scriptables.ScriptNumber(self.arena.dims[0])
        self.env.constants["A_HEIGHT"] = scriptables.ScriptNumber(self.arena.dims[1])

        self.env.constants["objective.x"] = scriptables.ScriptNumber(self.arena.objective.pos[0])
        self.env.constants["objective.y"] = scriptables.ScriptNumber(self.arena.objective.pos[1])

    
    def updateScriptConstants(self, enemyBots):
        self.env.constants["bot.x"] = scriptables.ScriptNumber(self.pos[0])
        self.env.constants["bot.y"] = scriptables.ScriptNumber(self.pos[1])
        self.env.constants["objective.health"] = scriptables.ScriptNumber(self.arena.objective.health)
        self.env.constants["D_TIME"] = scriptables.ScriptNumber(time.time() - self.lastScriptUpdate)
        self.env.constants["enemy.count"] = len(enemyBots)
        if len(enemyBots) > 0:
            nearest, nearestDist = getClosestBot(self.pos, enemyBots)
            self.env.constants["enemy.nearest.x"] = \
                scriptables.ScriptNumber(nearest.pos[0])
            self.env.constants["enemy.nearest.y"] = \
                scriptables.ScriptNumber(nearest.pos[1])
            self.env.constants["enemy.nearest.reldir"] = \
                scriptables.ScriptNumber(math.atan2(-1*(nearest.pos[1] - self.pos[1]),
                                         nearest.pos[0] - self.pos[0]))
        self.env.constants["objective.reldir"] = \
            scriptables.ScriptNumber(math.atan2(-1*(self.arena.objective.pos[1] - self.pos[1]),
                                         self.arena.objective.pos[0] - self.pos[0]))


    def update(self, app, enemyBots):
        dTime = time.time() - self.lastTime
        
        #Do script updates
        if time.time() >= self.lastScriptUpdate + SCRIPT_UPDATE_SPEED:
            #Inject new variables into script environment
            self.env.locs = cleanseLocals(self.env.locs)
            self.updateScriptConstants(enemyBots)
            self.env.executeAll()
            self.lastScriptUpdate = time.time()
            self.env.constants["FIRST_CALL"] = scriptables.ScriptBoolean(False) 

        #Update weapons
        isEnemy = self in self.arena.enemyBots
        for eq in self.equipment:
            #self.externals = {"direction":0, "fire":True}
            eq.update(self.env.externals)
            for projectile in eq.projectiles:
                #Don't friendly fire the objective!
                projectile.update(app, (enemyBots + [self.arena.objective] if 
                    isEnemy else enemyBots))
                    # ie don't include the objective in list of potential collisions
                    # if you're a friendly bot
        #Update movement
        mSpeed  = self.env.externals["move.speed"].value 
        mDir = self.env.externals["move.direction"].value
        if abs(mSpeed) > 1: mSpeed = mSpeed/abs(mSpeed)

        xVel = mSpeed * math.cos(mDir)
        yVel = mSpeed * (-1) * math.sin(mDir)

        newPos = (self.pos[0] + self.speed*xVel*dTime,
                    self.pos[1] + self.speed*yVel*dTime)
        self.pos = boundPosition(newPos, self.arena.dims)

        self.lastTime = time.time()
    def draw(self, app, canvas):
        #Draw bot itself
        canvas.create_oval(self.pos[0] - self.collisionRadius, self.pos[1] - self.collisionRadius,
                           self.pos[0] + self.collisionRadius, self.pos[1] + self.collisionRadius,
                           fill = "blue")

        #draw health
        canvas.create_text(self.pos[0], self.pos[1]- 5, text=f"{self.health}")
    def damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            if self in self.arena.friendlyBots: self.arena.friendlyBots.remove(self)
            elif self in self.arena.enemyBots: self.arena.enemyBots.remove(self)


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
        self.lastTime = time.time()
    
    #Move the projectile and deal damage if needed
    def update(self, app, bots):
        dTime = time.time() - self.lastTime
        xVel = self.speed * math.cos(self.direction) * dTime
        yVel = -1 * self.speed * math.sin(self.direction) * dTime
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

        self.lastTime = time.time()
    #Check if projectile is colliding with a bot in bots
    #If it is, return the bot. Otherwise, return None
    def checkCollisions(self, bots):
        for bot in bots:
            dist = pointDistance(bot.pos[0], bot.pos[1], self.pos[0], self.pos[1])
            if dist < self.collisionRadius + bot.collisionRadius:
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
        self.externals = {self.name+".direction": scriptables.ScriptNumber(0),
                         self.name+".fire": scriptables.ScriptBoolean(False)}
        self.lastFire = 0
        self.bot = None
        self.damage=damage
    
    def update(self, externals):
        if externals[self.name+".fire"].value:
            if time.time() - self.lastFire >= self.fireCooldown:
                self.lastFire = time.time()
                #Create a new projectile
                newProjectile = Projectile(self, self.projectileSpeed, 
                    self.projectileTexture, self.bot.pos, externals[self.name+".direction"].value,
                    self.projectileColRad, self.damage)
                self.projectiles.append(newProjectile)

class Objective(Bot): #Objectives are just bots that don't do anything
    def __init__(self, arena, size, position, health):
        self.arena = arena
        self.pos = position
        self.health = health
        self.collisionRadius = size/2
        self.size = size

    def update(self, _): pass #Make it so the update function does nothing

    def draw(self, canvas):
        canvas.create_rectangle(self.pos[0] - self.size/2, self.pos[1] - self.size/2,
            self.pos[0]+self.size/2, self.pos[1] + self.size/2, fill="purple")

        canvas.create_text(self.pos[0], self.pos[1]- 5, text=f"{self.health}")
