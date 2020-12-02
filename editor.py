'''
This file defines the editor that opens when the player edits a bot.
It more or less functions like a standalone app
'''

import UIElems
import loader

class Editor():
    def __init__(self, bot, margin=20):
        self.bot = bot
        self.botJson = loader.loadJsonFromFile("bots/bots.json")[bot]
        
        self.margin = margin
        self.container = UIElems.UIContainer(margin,margin)

        self.container.add(UIElems.UILabeledCheckbox(10,10, "label"))

        #Create UI for weapons

    def draw(self, app, canvas):
        self.container.draw(app, canvas)

    def onClick(self, app, event):
        self.container.onClick(app, event)

class EquipmentCheckbox(UIElems.UILabeledCheckbox):
    #Equipment is a tuple of the form (name, display name, cost)
    def __init__(x, y, equipment, bot):
        self.eqName, self.eqLabel, self.eqCost = equipment
        super().__init__(x,y, f"{self.eqLabel}: ${self.eqCost}")
        

class backButton(UIElems.UIButton):
    def onClick(app):
        app.state = "ARENA"
        app.arena.resume()
        for botContainer in app.arena.bottomBar:
            botContainer.refresh()

        #TODO:Write bot changes to file...
