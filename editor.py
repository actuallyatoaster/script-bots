'''
This file defines the editor that opens when the player edits a bot.
It more or less functions like a standalone app
'''
import subprocess, os#This is just for opening the file in default program,
# From: https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os

import UIElems
import loader

class Editor():
    def __init__(self, bot, margin=20):
        self.bot = bot
        self.botJson = loader.loadJsonFromFile("bots/bots.json")[bot]
        
        self.margin = margin
        self.container = UIElems.UIContainer(margin,margin)

        #Create UI for weapons
        self.weapons, self.buffs = loader.makeEquipmentList()
        self.titleOffset, self.horzOffset, self.checkMargin = 50, 350, 40


        for i in range(len(self.weapons)):
            weapon = self.weapons[i]
            checked = loader.botHasEquipment(self.bot, weapon[0])
            box = EquipmentCheckbox(0, self.titleOffset + self.checkMargin*i, 
            weapon, self.bot, checked=checked)
            self.container.add(box)
        
        for i in range(len(self.buffs)):
            buff = self.buffs[i]
            checked = loader.botHasEquipment(self.bot, buff[0])
            box = EquipmentCheckbox(self.horzOffset, self.titleOffset + self.checkMargin*i, 
            buff, self.bot, checked=checked)
            self.container.add(box)
        
        buttonsOffset = 2.5*self.titleOffset + max(len(self.weapons), len(self.buffs))*self.checkMargin

        scriptEditButton = ScriptEditButton(0, buttonsOffset, 100, 30, "Open Script")
        self.container.add(scriptEditButton)

        backButton = BackButton(0, buttonsOffset+scriptEditButton.height + self.margin+80, 60, 30, "Back")
        self.totalCost = loader.calculateBotCost(self.bot, typeFile = 'bots/bots.json')
        self.container.add(backButton)

    def draw(self, app, canvas):
        self.container.draw(app, canvas)

        #Draw titles
        canvas.create_text(self.margin, self.margin, text="Weapons",
        font="Helvetica 24 bold", anchor = 'nw')

        canvas.create_text(self.margin + self.horzOffset, self.margin, 
        text="Buffs", font="Helvetica 24 bold", anchor = 'nw')

        #show the bot cost
        costOffset = 2*self.titleOffset + max(len(self.weapons), len(self.buffs))*self.checkMargin
        canvas.create_text(self.margin, costOffset, text=f"Total cost: ${self.totalCost}",
        anchor='nw', font = "Helvetica 18 bold")

    def onClick(self, app, event):
        self.container.onClick(app, event)

class EquipmentCheckbox(UIElems.UILabeledCheckbox):
    #Equipment is a tuple of the form (name, display name, cost)
    def __init__(self, x, y, equipment, bot, checked=False):
        self.eqName, self.eqLabel, self.eqCost = equipment
        self.bot = bot
        super().__init__(x,y, f"{self.eqLabel}: ${self.eqCost}", checked=checked)
        self.eqJson = loader.loadJsonFromFile('bots/equipment.json')
        
        #this is a bit hacky, but it works
        def onCheck(app):
            if self.eqName in self.eqJson["weapons"]:
                app.editor.botJson["weapons"].append(self.eqName)
            else:
                app.editor.botJson["buffs"].append(self.eqName)
            
        def onUnCheck(app):
            if self.eqName in self.eqJson["weapons"]:
                app.editor.botJson["weapons"].remove(self.eqName)
            else:
                app.editor.botJson["buffs"].remove(self.eqName)

        self.checkButton.onCheck = onCheck
        self.checkButton.onUnCheck = onUnCheck
    
    def onClick(self, app, event):
        super().onClick(app, event)
        app.editor.totalCost = loader.calculateBotCost(self.bot, botJson=app.editor.botJson)
        #print(self.totalCost)

        

class BackButton(UIElems.UIButton):
    def onClick(self, app):
        loader.saveBotToFile(app.editor.bot, app.editor.botJson)

        app.state = "ARENA"
        #app.arena.resume(app)
        for botContainer in app.arena.bottomBar.elems:
            botContainer.refresh()

        

class ScriptEditButton(UIElems.UIButton):
    def onClick(self, app):
        openFileInDefaultProgram(app.editor.bot)

    def draw(self, app, canvas):
        super().draw(app, canvas)
        containerX, containerY = self.container.positionOffset()
        #position is relative to container
        bX = self.x + containerX
        bY = self.y + containerY


        if app.editor.bot.startswith("user"):
            path = f"bots/scripts/user/{app.editor.bot}.bot"
        else:
            path = f"bots/scripts/presets/{app.editor.bot}.bot"
        canvas.create_text(bX, bY+40, anchor='nw', font="Arial 12", 
        text=f"The above button may not work on all platforms.")
        canvas.create_text(bX, bY+60, anchor='nw', font="Arial 12", 
        text=f"If it doesn't, try setting a default program for '.bot' files.")
        canvas.create_text(bX, bY+80, anchor='nw', font="Arial 12", 
        text=f"Or, open the file manually at {path}")

def openFileInDefaultProgram(path):
    s= os.sep
    if path.startswith("user"):
        filepath = f"bots{s}scripts{s}user{s}{path}.bot"
    else:
        filepath = f"bots{s}scripts{s}presets{s}{path}.bot"
    print(filepath)
    #From https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
    #I did not write this !!!
    try:
        os.system("start " + filepath)
    except err: print(err)
    try:
        os.system("open " + filepath)
    except:pass
