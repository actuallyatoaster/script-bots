import bots
import loader
import time

'''
This file defines the arena environment
''' 


class Arena():
    def __init__(self, dims):
        self.wave = 0
        self.waveInterval = 10
        self.endOfLastWave = 0
        self.waveStarted = False

        self.dims = dims
        self.friendlyBots = []
        self.enemyBots = []
        self.objective = bots.Objective(self, 40, (dims[0]/2, dims[1]/2), 500)
        self.money = 1000

    def update(self, app):

        if len(self.enemyBots) == 0 and self.waveStarted:
            self.waveStarted = False
            self.endOfLastWave = time.time()
            self.money += 200 * self.wave

        elif ((not self.waveStarted) and time.time() > self.endOfLastWave + self.waveInterval):
            self.waveStarted = True
            self.wave += 1
            loader.createEnemyWave(self, self.wave)

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

        self.createArenaStats(app, canvas)
        
    def createArenaStats(self, app, canvas, margin=20):
        canvas.create_text(self.dims[1]+ margin, margin, anchor='nw',
            font = 'Arial 24 bold', text = f"Wave {self.wave}")
        coolDownOffset = 35
        timeRemaining = round(self.endOfLastWave + self.waveInterval - time.time())
        if not self.waveStarted:
            canvas.create_text(self.dims[1]+ margin, margin + coolDownOffset, anchor='nw',
                font = 'Arial 18', text = f"Next wave in {timeRemaining}")
        
        moneyOffset = coolDownOffset + 45
        canvas.create_text(self.dims[1]+ margin, margin + moneyOffset, anchor='nw',
            font = 'Arial 18', text = f"Money: ${self.money}")