import bots
from cmu_112_graphics import *
'''
This file defines the arena environment
''' 
lines = 5

class Arena():
    def __init__(self):
        self.friendlyBots = []
        self.enemyBots = []

    def update(self, app):
        for bot in self.friendlyBots:
            bot.update(app, self.enemyBots, lines)

        for bot in self.enemyBots:
            bot.update(app, self.friendlyBots, lines)

    def draw(self, app, canvas):
        canvas.create_rectangle(0,0, app.arenaWidth, app.arenaHeight, fill="grey")

        for bot in self.friendlyBots:
            bot.draw(app, canvas)
            for eq in bot.equipment:
                for projectile in eq.projectiles:
                    projectile.draw(app, canvas)


#####Temp stuff!!!!!

def appStarted(app):
    app.timerDelay = 0
    app.arena = Arena()
    app.arenaWidth = app.arenaHeight = 500
    script = '''
    gunFire = True
    gunDirection = gunDirection + (2*pi*D_TIME)

    if FIRST_CALL
        xMov = 1
        yMov = 1
        num $totalCalls = 1
        num $dTimeSum = 0
    endif

    else
        if bot.x > 400
            xMov = 0-1
        endif
        if bot.x < 100
            xMov = 1
        endif
        if bot.y>400
            yMov = 0-1
        endif
        if bot.y < 100
            yMov = 1
        endif
        $totalCalls = $totalCalls+1
    endelse
    $dTimeSum = $dTimeSum + D_TIME
    log: $totalCalls / $dTimeSum
    '''
    gun = bots.Equipment("gun", 100, 100, None, 3, 2)
    bot = bots.Bot([gun], script, 5, (250,250), 10, 50)
    
    bot.equipment.append(gun)

    app.arena.friendlyBots.append(bot)

def timerFired(app):
    app.arena.update(app)

def redrawAll(app, canvas):
    app.arena.draw(app, canvas)

runApp(width=700, height=700)
