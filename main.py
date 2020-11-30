from cmu_112_graphics import * #From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
import arena
import loader
import time

def appStarted(app):
    app.state = "ARENA"
    #Want everything as smooth as possible, all the other timing is manual anyway
    app.timerDelay = 1
    app.botBoundsMargin=2
    app.arenaWidth , app.arenaHeight = 500,500
    app.arena = arena.Arena((500,500))
    app.paused = False
    app.pausedTime = 0
    app.pauseStart = None
    
    for i in range(6):
        bot = loader.createBotFromFile("demo", app.arena, (i*50, i*30), 
                baseHealth = 600, typeFile='bots/bots.json')
        app.arena.friendlyBots.append(bot)

def timerFired(app):
    if app.paused:
        app.pausedTime = time.time() - app.pauseStart
    else:
        if app.state == "ARENA":app.arena.update(app)

def redrawAll(app, canvas):
    if app.state == "ARENA":app.arena.draw(app, canvas)
2
def mousePressed(app, event):
    if app.state == "ARENA":app.arena.onClick(app, event)

runApp(width=700, height=700)