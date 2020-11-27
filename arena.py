import bots
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
        


#####Temp stuff!!!!!

def appStarted(app):
    #Want everything as smooth as possible, all the other timing is manual anyway
    app.timerDelay = 1
    app.arenaWidth , app.arenaHeight = 500,500
    app.arena = Arena((500,500))
    script = '''
    gun.fire = True
    gun.direction = enemy.nearest.reldir #aim at enemy
    #initialize everything
    if FIRST_CALL
        #initialize movement
        move.speed = 1

        #timing stuff
        num $totalCalls = 1 
        num $dTimeSum = 0 #total time elapsed
    endif

    #normal loop case
    else 
        #movement
        move.direction = move.direction + ((2*pi*D_TIME)/10)

        #track total calls
        $totalCalls = $totalCalls+1
        
        #only shoot every other second
        if ((round:$dTimeSum) % 2) == 0 #test comment, this shouldn't crash
            gun.fire = False # test comment#2
        endif
    endelse

    #log average script calls per second
    $dTimeSum = $dTimeSum + D_TIME
    #log: round:($totalCalls / $dTimeSum)
    '''
    gun = bots.Equipment("gun", 100, 100, None, 3, 2)
    bot = bots.Bot(app.arena, [gun], script, 5, (300,250), 10, 50)
    
    gun2 = bots.Equipment("gun", 1000, 2, None, 15, 2)
    bot2 = bots.Bot(app.arena, [gun2], script, 5, (250,300), 10, 75)

    app.arena.friendlyBots.append(bot)
    app.arena.enemyBots.append(bot2)

def timerFired(app):
    app.arena.update(app)

def redrawAll(app, canvas):
    app.arena.draw(app, canvas)

runApp(width=700, height=700)
