from cmu_112_graphics import * #From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
import arena
import loader
import time

def appStarted(app):
    app.state = "ARENA"
    app.substate = "DEFAULT" #Used to track when player is creating new bot
    app.selectedBot = None
    
    app.toastDelay = 1.8
    app.toast = None
    app.toastTime = 0
    app.toastColor = None
    #Want everything as smooth as possible, all the other timing is manual anyway
    app.timerDelay = 1

    app.botBoundsMargin=2
    app.arenaWidth , app.arenaHeight = 500,500
    app.arena = arena.Arena((500,500))

    app.paused = True #Start off paused
    app.pausedTime = 0
    app.pauseStart = time.time()

    #Testing stuff
    app.arena.money += 5000

def timerFired(app):
    if app.paused:
        app.pausedTime = time.time() - app.pauseStart
    else:
        if app.state == "ARENA":app.arena.update(app)

def redrawAll(app, canvas):
    if app.state == "ARENA":app.arena.draw(app, canvas)
    elif app.state == "EDITOR": editor.draw(app, canvas)

    if app.toast and time.time() <= app.toastTime + app.toastDelay:
        canvas.create_text(10,10, anchor = 'nw', text=app.toast,\
            fill=app.toastColor, font = "arial 16 bold")
    

def mousePressed(app, event):
    if app.state == "ARENA":app.arena.onClick(app, event)
    elif app.state == "EDITOR": editor.mousePressed(app, event)


runApp(width=700, height=700)