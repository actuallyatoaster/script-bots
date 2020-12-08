from cmu_112_graphics import * #From https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
import arena
import loader
import time
import editor
import menu


def appStarted(app):
    app.state = "MENU"
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
    app.arena = None

    app.paused = True #Start off paused
    app.pausedTime = 0
    app.pauseStart = time.time()

    #Error logging; we create a function to override the default scriptError function
    app.errs = []
    def scriptError(err):
        app.errs.append(err)
        raise arena.bots.scriptables.ScriptError
    arena.bots.scriptables.scriptError = scriptError
    app.errorBot = None

    #Now, override the scriptLog function
    def scriptLog(msg):
        app.toastTime = time.time()
        app.toast = f"{app.errorBot}: {msg}"
        app.toastColor = "green"
    arena.bots.scriptables.scriptLog = scriptLog

    #Initialize menu stuff
    menu.appStarted(app)

def timerFired(app):
    if app.paused:
        app.pausedTime = time.time() - app.pauseStart
    else:
        if app.state == "ARENA" and app.acknowledged:
            try:
                app.arena.update(app)
            except arena.bots.scriptables.ScriptError:
                #Error handling: pause the game and display the error
                app.paused = True
                app.pauseStart = time.time()
                app.pausedTime = 0
                print("ERR: " + app.errorBot)
                for i in range(len(app.errs), 0, -1):
                    print("---- "+app.errs[i-1])
                app.toastTime = time.time() + 5#5 sec longer than default toast
                app.toast = f"Script error: {app.errs[0]}. Check console for info."
                app.toastColor = "red"
                app.errs = []
            
def redrawAll(app, canvas):
    if app.state == "ARENA":
        app.arena.draw(app, canvas)
        if not app.acknowledged:
            cx, cy = app.width/2, app.height/2
            canvas.create_text(cx, cy-30, text="You are playing Preset Mode",
                fill="red", font="Arial 24 bold")
            canvas.create_text(cx, cy+5, 
                text="Bot scripts are already written for you, but you can still edit them if you like",
                fill="red")
            canvas.create_text(cx, cy+20, text="Click anywhere to continue",
                fill="red")
    elif app.state == "EDITOR": app.editor.draw(app, canvas)
    elif app.state == "MENU": menu.redrawAll(app, canvas)
    elif app.state == "GAMEOVER": menu.drawGameOver(app, canvas)
    if app.toast and time.time() <= app.toastTime + app.toastDelay:
        canvas.create_text(10,10, anchor = 'nw', text=app.toast,\
            fill=app.toastColor, font = "arial 16 bold")
    

def mousePressed(app, event):
    if app.state == "ARENA":
        if app.acknowledged:
            app.arena.onClick(app, event)
        else:
            app.acknowledged = True
    elif app.state == "EDITOR": app.editor.onClick(app, event)
    elif app.state == "MENU": menu.mousePressed(app, event)
    elif app.state == "GAMEOVER":
        appStarted(app)
        app.state = "MENU"


runApp(width=700, height=700)