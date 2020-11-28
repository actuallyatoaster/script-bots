import bots
import loader
from cmu_112_graphics import *
'''
This file defines the arena environment
''' 


class Arena():
    def __init__(self, dims):
        self.dims = dims
        self.friendlyBots = []
        self.enemyBots = []
        self.objective = bots.Objective(self, 40, (dims[0]/2, dims[1]/2), 500)

    def update(self, app):
        for bot in self.friendlyBots:
            bot.update(app, self.enemyBots)

        for bot in self.enemyBots:
            bot.update(app, self.friendlyBots)

    def draw(self, app, canvas):
        canvas.create_rectangle(0,0, self.dims[0], self.dims[1], fill="grey")

        for bot in self.friendlyBots + self.enemyBots:
            bot.draw(app, canvas)
            for eq in bot.equipment:
                for projectile in eq.projectiles:
                    projectile.draw(app, canvas)

        self.objective.draw(canvas)

        #draw edges to mask things going slightly off the arena area
        canvas.create_rectangle(self.dims[0], 0, app.height, app.width, 
            fill="white", width=0)
        canvas.create_rectangle(0, self.dims[1], app.height, app.width, 
            fill="white", width=0)
        


#####Temp stuff!!!!!

def appStarted(app):
    #Want everything as smooth as possible, all the other timing is manual anyway
    app.timerDelay = 1
    app.arenaWidth , app.arenaHeight = 500,500
    app.arena = Arena((500,500))

    bot = loader.createBotFromFile("demo", app.arena, (400,400), typeFile="bots/bots.json")
    
    bot2 = loader.createBotFromFile("heavy", app.arena, (400,400))

    app.arena.friendlyBots.append(bot)
    app.arena.enemyBots.append(bot2)

def timerFired(app):
    app.arena.update(app)

def redrawAll(app, canvas):
    app.arena.draw(app, canvas)

runApp(width=700, height=700)
