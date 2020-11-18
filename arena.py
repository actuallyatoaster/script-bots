import bots
from cmu_112_graphics import *
'''
This file defines the arena environment
''' 


class Arena():
    def __init__(self):
        self.friendlyBots = []
        self.enemyBots = []

    def update(self, app):
        for bot in self.friendlyBots:
            bot.update(app, self.enemyBots)

        for bot in self.enemyBots:
            bot.update(app, self.friendlyBots)

    def draw(self, app, canvas):
        canvas.create_rectangle(0,0, app.arenaWidth, app.arenaHeight, fill="grey")

        for bot in self.friendlyBots:
            bot.draw(app, canvas)
            for eq in bot.equipment:
                for projectile in eq.projectiles:
                    projectile.draw(app, canvas)


#####Temp stuff!!!!!

def appStarted(app):
    app.timerDelay = 1
    app.arena = Arena()
    app.arenaWidth , app.arenaHeight = 500,500
    script = '''
    gunFire = True
    gunDirection = gunDirection + (2*pi*D_TIME)
    #initialize everything
    if FIRST_CALL
        #initialize movement
        xMov = 1 
        yMov = 0-(8/10)

        #timing stuff
        num $totalCalls = 1 
        num $dTimeSum = 0 #total time elapsed
    endif

    #normal loop case
    else 
        #movement
        if (bot.x > 400) || (bot.x < 100)
            xMov = 0-xMov
        endif

        if (bot.y>400) || (bot.y < 100)
            yMov = 0-yMov
        endif

        #track total calls
        $totalCalls = $totalCalls+1
        
        #only shoot every other second
        if ((round:$dTimeSum) % 2) == 0 #test comment, this shouldn't crash
            gunFire = False # test comment#2
        endif
    endelse

    #log average script calls per second
    $dTimeSum = $dTimeSum + D_TIME
    log: round:($totalCalls / $dTimeSum)
    '''
    gun = bots.Equipment("gun", 100, 100, None, 3, 2)
    bot = bots.Bot([gun], script, 5, (300,250), 10, 50)
    
    gun2 = bots.Equipment("gun", 100, 100, None, 3, 2)
    bot2 = bots.Bot([gun2], script, 5, (250,300), 10, 50)

    app.arena.friendlyBots.append(bot)
    app.arena.friendlyBots.append(bot2)

def timerFired(app):
    app.arena.update(app)

def redrawAll(app, canvas):
    app.arena.draw(app, canvas)

runApp(width=700, height=700)
