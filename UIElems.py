'''
This file defines some classes used to create UI elements (mostly buttons)
'''

#Container to hold all the elements used
class UIContainer():
    def __init__(self, x, y, elems = None):
        self.x = x
        self.y = y
        self.elems = [] if elems == None else elems
    
    #Add an element to the container
    def add(self, elem):
        elem.container = self
        self.elems.append(elem)
    
    #Call onClick() of any buttons clicked
    def onClick(self, app, event):
        for elem in self.elems:
            if elem.clickInBounds(event): elem.onClick(app)
    
    def draw(self, app, canvas):
        for elem in self.elems:
            elem.draw(app, canvas)

#Button class
class UIButton():
    def __init__(self, x, y, width, height, label = "", container=None, color = 'grey'):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.container = container
        self.label = label
        self.color = color
    
    def draw(self, app, canvas):
        #position is relative to container
        bX = self.x + self.container.x 
        bY = self.y + self.container.y

        canvas.create_rectangle(bX, bY, bX + self.width, bY + self.height,
            fill=self.color, width=0)

        canvas.create_text((2*bX + self.width)/2, (2*bY + self.height)/2,
            font="Arial 12", text=self.label)
    
    #Return whether a click was on the button
    def clickInBounds(self, event):
        bXMin = self.x + self.container.x
        bXMax = bXMin + self.width

        bYMin = self.y + self.container.y
        bYMax = bYMin + self.height

        return (bXMin <= event.x <= bXMax and
                bYMin <= event.y <= bYMax)

    #Subclasses should make this actually do something
    def onClick(self, app):
        print(f"Button {self.label} clicked.")

