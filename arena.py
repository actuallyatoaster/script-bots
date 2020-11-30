import bots
import loader
import time
import UIElems

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

        self.sidebar = self.buildSidebar()
        self.bottomBar = self.buildBottomBar()

    def update(self, app):

        if len(self.enemyBots) == 0 and self.waveStarted:
            self.waveStarted = False
            self.endOfLastWave = time.time()
            self.money += 200 * self.wave

        elif ((not self.waveStarted) and 
                time.time() > self.endOfLastWave + self.waveInterval + app.pausedTime):
            self.waveStarted = True
            self.wave += 1
            loader.createEnemyWave(self, self.wave)
            app.pausedTime = 0

        for bot in self.friendlyBots:
            bot.update(app, self.enemyBots)

        for bot in self.enemyBots:
            bot.update(app, self.friendlyBots)

    def resume(self, app):
        app.paused = False
        resumeTime = time.time()

        for bot in self.enemyBots + self.friendlyBots:
            bot.lastTime = resumeTime
            bot.lastScriptUpdate = resumeTime

            for eq in bot.equipment:
                eq.lastFire = resumeTime
                
                for projectile in eq.projectiles:
                    projectile.lastTime = resumeTime
        
        

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
        self.sidebar.draw(app, canvas)
        self.bottomBar.draw(app, canvas)
    
    def onClick(self, app, event):
        self.sidebar.onClick(app, event)
        self.bottomBar.onClick(app, event)
    
    def buildSidebar(self, vertOffset = 120,margin = 20):
        container = UIElems.UIContainer(self.dims[0], vertOffset)
        
        pauseButton = PauseButton(margin, margin)
        resumeButton = ResumeButton(2*margin + pauseButton.width, margin)
        
        container.add(pauseButton)
        container.add(resumeButton)
        return container
    
    def buildBottomBar(self):
        return UIElems.UIContainer(0,0)
    
        
    def createArenaStats(self, app, canvas, margin=20):
        canvas.create_text(self.dims[1]+ margin, margin, anchor='nw',
            font = 'Arial 24 bold', text = f"Wave {self.wave}")
        coolDownOffset = 35
        timeRemaining = round(app.pausedTime + self.endOfLastWave + self.waveInterval - time.time())
        if not self.waveStarted:
            canvas.create_text(self.dims[1]+ margin, margin + coolDownOffset, anchor='nw',
                font = 'Arial 18', text = f"Next wave in {timeRemaining}")
        
        moneyOffset = coolDownOffset + 45
        canvas.create_text(self.dims[1]+ margin, margin + moneyOffset, anchor='nw',
            font = 'Arial 18', text = f"Money: ${self.money}")

class PauseButton(UIElems.UIButton):
    def __init__(self, x,y):
        super().__init__(x,y,60, 30, label="Pause")
    
    def onClick(self, app):
        if not app.paused:
            app.paused = True
            app.pauseStart = time.time()
            app.pausedTime = 0

class ResumeButton(UIElems.UIButton):
    def __init__(self, x, y):
        super().__init__(x,y, 70, 30, label = "Resume")
    
    def onClick(self, app):
        if app.paused: app.arena.resume(app)
        
    