'''
This file defines the editor that opens when the player edits a bot.
It more or less functions like a standalone app
'''

import UIElems
import loader

def appStarted(app):
    app.editorContainer = UIElems.UIContainer(0,0)

def redrawAll(app):

def mousePressed(event):

class backButton(UIElems.UIButton):
    def onClick(app):
        app.state = "ARENA"
        app.arena.resume()
        for botContainer in app.arena.bottomBar:
            botContainer.refresh()

        #TODO:Write bot changes to file...
