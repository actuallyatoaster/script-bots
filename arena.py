import bots
import loader
import time
import UIElems
import editor

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
        self.objective = bots.Objective(self, 40, (dims[0]/2, dims[1]/2), 2000)
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

        if self.objective.health <= 0:
            app.state = "GAMEOVER"

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
            for eq in bot.equipment:
                for projectile in eq.projectiles:
                    projectile.draw(app, canvas)
            bot.draw(app, canvas)

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

        #Create purchased bot and remove money
        if app.substate == "PURCHASE":
            if event.x <= app.arenaWidth and event.y <= app.arenaHeight:
                newBot = loader.createBotFromFile(app.selectedBot, self,
                    (event.x, event.y), typeFile = 'bots/bots.json')
                self.friendlyBots.append(newBot)

                self.money -= loader.calculateBotCost(app.selectedBot,
                    typeFile = 'bots/bots.json')
                app.substate = "DEFAULT"
                app.selectedBot = None
                app.toast = None

    
    def buildSidebar(self, vertOffset = 120,margin = 20):
        container = UIElems.UIContainer(self.dims[0], vertOffset)
        
        pauseButton = PauseButton(margin, margin)
        resumeButton = ResumeButton(2*margin + pauseButton.width, margin)
        
        container.add(pauseButton)
        container.add(resumeButton)
        return container
    
    def buildBottomBar(self):
        bottomBar = UIElems.UIContainer(0, self.dims[1])
        botContainerWidth = 140

        for userBotID in range(5):
            bottomBar.add(BotContainer(botContainerWidth * userBotID, 0,
                f"user-bot{userBotID+1}", True))

        return bottomBar
    
        
    def createArenaStats(self, app, canvas, margin=20):
        canvas.create_text(self.dims[1]+ margin, margin, anchor='nw',
            font = 'Arial 24 bold', text = f"Wave {self.wave}")
        coolDownOffset = 35
        timeRemaining = round(app.pausedTime + self.endOfLastWave + self.waveInterval - time.time())
        if not self.waveStarted and timeRemaining > 0:
            canvas.create_text(self.dims[1]+ margin, margin + coolDownOffset, anchor='nw',
                font = 'Arial 18', text = f"Next wave in {timeRemaining}")
        
        moneyOffset = coolDownOffset + 45
        canvas.create_text(self.dims[1]+ margin, margin + moneyOffset, anchor='nw',
            font = 'Arial 18', text = f"Money: ${self.money}")

#Buttons that appear for each bot in the bottom bar
class BotContainer(UIElems.UIContainer):
    def __init__(self, x, y, botName, exists, margin=20):
        super().__init__(x,y)
        self.exists = exists
        self.label = botName
        self.margin = margin
        #BotContainer should be a 200x140 rectangle
        width, height= 140, 200

        #Make edit and purchase buttons
        editButton = BotEditButton(margin, height-margin-30, botName)
        purchaseButton = BotPurchaseButton(2*margin+editButton.width,
                height-margin-30, botName)
        self.add(editButton)
        self.add(purchaseButton)
        self.refresh()
        self.botSize = 5 #Only for icon
        self.botDisplayName = loader.loadJsonFromFile("bots/bots.json")[botName]["displayName"]

    def refresh(self):
        self.cost = loader.calculateBotCost(self.label, typeFile = 'bots/bots.json')
    
    def draw(self, app, canvas):
        super().draw(app, canvas)
        posX, posY = self.positionOffset()
        #Make label
        canvas.create_text(posX + self.margin, posY + self.margin,
            text=self.botDisplayName, anchor='nw', font = "Helvetica 16 bold")
        
        #Show price
        canvas.create_text(posX + self.margin, posY + self.margin*2,
            text=f"${self.cost}", anchor = 'nw', font = "Helvetica 13")
        
        #Show "picture"
        cx = posX + 140/2
        cy = posY + 200/2
        scale = 3
        canvas.create_oval(cx - scale*self.botSize, cy - scale*self.botSize,
            cx+scale*self.botSize, cy+scale*self.botSize, fill = "blue", 
            width=0)


class BotEditButton(UIElems.UIButton):

    def __init__(self, x, y, botName):
        super().__init__(x,y, 40, 30, label="Edit")
        self.botName = botName
    
    def onClick(self, app):
        app.state = "EDITOR"
        app.editor = editor.Editor(self.botName)

        #Pause the game
        if not app.paused:
            app.paused = True
            app.pauseStart = time.time()
            app.pausedTime = 0

class BotPurchaseButton(UIElems.UIButton):
    def __init__(self, x, y, botName):
        super().__init__(x, y, 40, 30, label="Buy")
        self.botName = botName

    def onClick(self, app):
        #Let user place new bot if there's sufficient money
        if app.arena.money < loader.calculateBotCost(self.botName, 
                typeFile = 'bots/bots.json'):
            app.toastTime = time.time()
            app.toast = "Not enough money!"
            app.toastColor = "red"

        else: 
            app.substate = "PURCHASE"
            app.selectedBot = self.botName

            app.toastTime = time.time()*2 #This should be long enough to keep it permanently
            app.toast = f"Click to place {loader.loadJsonFromFile('bots/bots.json')[self.botName]['displayName']}"
            app.toastColor = "blue"
            

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
