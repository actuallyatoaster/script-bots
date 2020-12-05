'''
Main splash screen and help menu
'''
import UIElems

def appStarted(app):
    cx, cy = app.width/2, app.height/2
    margin = 10

    #Setup splash screen UI
    app.menuSplashContainer = UIElems.UIContainer(0,0)
    splashPlayButton = PlayButton(cx - 60-margin, cy, 60, 30, label="Play!")
    app.menuSplashContainer.add(splashPlayButton)

    splashHelpButton = HelpButton(cx+margin, cy, 60, 30, label="Help")
    app.menuSplashContainer.add(splashHelpButton)

    #Setup help screen UI
    helpMargin = 30
    app.helpContainer = UIElems.UIContainer(0,0)
    app.helpPage = 0
    backButton = HelpButton(helpMargin, app.height-helpMargin-30, 60, 30, label="Back")
    nextButton = PageButton(app.width - helpMargin - 90, app.height-helpMargin-30, 90,30,
        1, label="Next Page")
    prevButton = PageButton(app.width-helpMargin*2-90-nextButton.width, 
    app.height-helpMargin-30, 110, 30, -1, label = "Previous Page")

    app.helpContainer.add(backButton)
    app.helpContainer.add(nextButton)
    app.helpContainer.add(prevButton)

    #Load help menu text data
    with open('help.txt', 'r') as f:
        app.helpLines = f.read().splitlines()
        f.close()

    app.helpLinesPerPage = 33 #How many lines of text to show per page


def mousePressed(app, event):
    if app.substate == "DEFAULT":
        app.menuSplashContainer.onClick(app, event)
    elif app.substate == "HELP":
        app.helpContainer.onClick(app,event)

def redrawAll(app, canvas):
    if app.substate == "DEFAULT": drawSplash(app, canvas)
    elif app.substate == "HELP": drawHelp(app, canvas)

def drawSplash(app, canvas):
    cx, cy = app.width/2, app.height/2
    canvas.create_text(cx, cy*0.7, text="BotArena!", font = 'Helvetica 32 bold')
    app.menuSplashContainer.draw(app, canvas)


def drawHelp(app, canvas):
    cx, cy = app.width/2, app.height/2
    app.helpContainer.draw(app, canvas)

    #Page number
    canvas.create_text(cx, app.height - 45, font="Helvetica 16 bold",
    text=f"Page {app.helpPage+1}")

    drawHelpText(app, canvas)

def drawHelpText(app, canvas, margin = 30, lineSpacing = 18):
    
    for i in range(app.helpLinesPerPage):
        line = app.helpPage * app.helpLinesPerPage + i
        if line >= len(app.helpLines): break
        text = app.helpLines[line]
        canvas.create_text(margin, margin + lineSpacing*i,
        text = text, font = 'Arial 12', anchor='nw')

def drawGameOver(app, canvas):
    cx, cy = app.width/2, app.height/2
    canvas.create_text(cx, cy, text="Game Over!", font="Arial 24 bold",
    fill="red")
    canvas.create_text(cx, cy+30, text="Click anywhere to play again",
    font="Arial 18")


class PlayButton(UIElems.UIButton):
    def onClick(self, app):
        app.state = "ARENA"

class HelpButton(UIElems.UIButton):
    def onClick(self, app):
        if app.substate == "DEFAULT":
            app.substate = "HELP"
        else:
            app.substate = "DEFAULT"
        
class PageButton(UIElems.UIButton):
    def __init__(self, x, y, width, height, pageIncrement, label=""):
        super().__init__(x, y, width, height, label=label)
        self.pageIncrement  =pageIncrement
    
    def onClick(self, app):
        if self.pageIncrement > 0 or (abs(self.pageIncrement) <= app.helpPage):
            app.helpPage += self.pageIncrement
