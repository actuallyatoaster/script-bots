from cmu_112_graphics import * #From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
import arena
import loader

def appStarted(app):
    app.state = "ARENA"
    #Want everything as smooth as possible, all the other timing is manual anyway
    app.timerDelay = 1
    app.arenaWidth , app.arenaHeight = 500,500
    app.arena = arena.Arena((500,500))

    for i in range(6):
        bot = loader.createBotFromFile("demo", app.arena, (i*50, i*30), baseHealth = 1000, typeFile='bots/bots.json')
        app.arena.friendlyBots.append(bot)

def timerFired(app):
    if app.state == "ARENA":app.arena.update(app)

def redrawAll(app, canvas):
    if app.state == "ARENA":app.arena.draw(app, canvas)

runApp(width=700, height=700)