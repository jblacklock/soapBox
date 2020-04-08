import tkinter as tk                
from tkinter import font  as tkfont 
from tkinter import *
from soap import rackMaker, testTubeRack, testTube
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        Tk.title(self,"SoapBox")
        self.frames = {}

        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage", "")


    def show_frame(self, page_name: str, formula: str) -> None:
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        if page_name == "PageOne":
            self.frames[page_name].setFormula(formula)
        if page_name == "StartPage":
            self.frames[page_name].fetchFormulas()
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text = "Formula Select", font = controller.title_font).grid(row = 0, column = 0, columnspan = 3)
        ttr = rackMaker()
        xcelFiles = ttr.getNamesOfExcelFiles()
        xcelFiles.insert(0, "Create New Formula")
        self.buttonPositions =[]
        t = 1
        y = 0
        for x in xcelFiles:
            formButton = tk.Button(self, text = x, width = (100//6), height = 3, fg="white", bg ="teal", command=lambda x=x: controller.show_frame("PageOne", x))
            formButton.grid(row = t, column = y)
            y += 1
            self.buttonPositions.append(formButton)
            if y == 6:
                y = 0
                t += 1
        

    def fetchFormulas(self):
        for i in self.buttonPositions:
            i.destroy()

        ttr = rackMaker()
        xcelFiles = ttr.getNamesOfExcelFiles()
        xcelFiles.insert(0, "Create New Formula")
        t = 1
        y = 0
        for x in xcelFiles:
            formButton = tk.Button(self, text = x, width = (100//6), height = 3, fg="white", bg ="teal", command=lambda x=x: self.controller.show_frame("PageOne", x))
            formButton.grid(row = t, column = y)
            y += 1
            self.buttonPositions.append(formButton)
            if y == 6:
                y = 0
                t += 1



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        self.backgroundColor = "#f0f0f0"
        self.pie1 = None
        self.pie2 = None
        self.ListOfWidgets = []
        self.ListOfSolvents = []
        self.ListOfVari = []
        self.lastIngredientRow = 0
        self.ttr = None
        tk.Frame.__init__(self, parent)
        self.controller = controller
        formula = "Error"
        button = tk.Button(self, text="<- Back", command=lambda: controller.show_frame("StartPage", ""))
        button.grid(row = 0, column = 0)
        self.label = tk.Label(self, text = formula, font=controller.title_font)
        self.label.grid(row = 0, column = 1, columnspan = 3, rowspan = 2)
        self.targetPrice = tk.Label(self, text = "Target Price:")
        self.targetPrice.grid(row = 0, column = 4)
        self.currentPrice = tk.Label(self, text = "Current Price:")
        self.currentPrice.grid(row = 1, column = 4)
        self.targetPriceValue = tk.Label(self, text = "0")
        self.targetPriceValue.grid(row = 0, column = 5)
        self.targetPriceValue.bind("<Button-1>",lambda e, targetPriceValue=self.targetPriceValue:self.changeLabel(targetPriceValue, 0, 5))
        self.currentPriceValue = tk.Label(self, text = "0")
        self.currentPriceValue.grid(row = 1, column = 5)
        self.variLabel = tk.Label(self, text= "Vari")
        self.variLabel.grid(row=5, column = 0)
        self.solvLabel = tk.Label(self, text= "Solvent")
        self.solvLabel.grid(row=5, column = 1)
        self.rawNumLabel = tk.Label(self, text= "Raw Material Number")
        self.rawNumLabel.grid(row=5, column = 2)
        self.ingredLabel = tk.Label(self, text= "Ingredient")
        self.ingredLabel.grid(row=5, column = 3)
        self.pplbLabel = tk.Label(self, text= "$/lb.")
        self.pplbLabel.grid(row=5, column = 4)
        self.concentrationLabel = tk.Label(self, text= "Concentration")
        self.concentrationLabel.grid(row=5, column = 5)
        self.concentrationLabel = tk.Label(self, text= "Total Price")
        self.concentrationLabel.grid(row=5, column = 6)
        self.currentPrice2 = tk.Label(self, text= "")
        self.CPriceLabel = tk.Label(self, text= "Total Cost:")
        fillVariToConcentration = tk.Button(self, text="Fill Vari to Concentration", command=lambda: self.fillVariToConcentration())
        fillVariToConcentration.grid(row = 4, column = 2)
        reduceVariToPrice = tk.Button(self, text="Reduce Vari to Price", command=lambda: self.reduceToPrice())
        reduceVariToPrice.grid(row = 4, column = 3)
        fillVariToPrice = tk.Button(self, text="Fill Vari to Price", command=lambda: self.fillVariToPrice())
        fillVariToPrice.grid(row = 4, column = 4)
        addIngred = tk.Button(self, text="Add Ingredient", command = lambda: self.openNewIngredientWindow())
        self.CheckForVaris()
        addIngred.grid(row = 4, column = 1)
        
    def CheckForVaris(self):
        if len(self.ListOfVari) == 0:
            self.grid_slaves(row = 4, column = 2)[0]["state"] = "disabled"
            self.grid_slaves(row = 4, column = 3)[0]["state"] = "disabled"
            self.grid_slaves(row = 4, column = 4)[0]["state"] = "disabled"
        else: 
            self.grid_slaves(row = 4, column = 2)[0]["state"] = "normal"
            self.grid_slaves(row = 4, column = 3)[0]["state"] = "normal"
            self.grid_slaves(row = 4, column = 4)[0]["state"] = "normal"


    def clearGrid(self, list_of_widgets):
        for widget in list_of_widgets:
            widget.destroy()     

    def updatePriceConcentrationCost(self) -> None:
        self.updateCurrentPrice()
        for rowVal in self.dictOfIngredientsAndRows:
            self.updateIngredientConcentration(self.dictOfIngredientsAndRows[rowVal])
            self.updateIngredientCost(self.dictOfIngredientsAndRows[rowVal])


    def fillVariToConcentration(self):
        self.ttr.fillToConcentration(self.ListOfVari)
        self.updatePriceConcentrationCost()
    
    def reduceToPrice(self):
        self.ttr.increaseSolventWhenReduceToPricePoint(self.ListOfSolvents ,self.ListOfVari)
        self.updatePriceConcentrationCost()

    def fillVariToPrice(self):
        self.ttr.reduceSolventWhenFillToPricePoint(self.ListOfSolvents ,self.ListOfVari)
        self.updatePriceConcentrationCost()


    def AddVari(self, rowVal: int):
        vari = self.getIngredientNameFromRow(rowVal) 
        if vari in self.ListOfVari: self.ListOfVari.remove(vari)
        else: self.ListOfVari.append(vari) 
        self.CheckForVaris()

    def AddSolvent(self, rowVal: int):
        solvent = self.getIngredientNameFromRow(rowVal)
        if solvent in self.ListOfSolvents: self.ListOfSolvents.remove(solvent)
        else: self.ListOfSolvents.append(solvent)

    def changeLabel(self, label: Label, rowVal: int, colVal:int):
        pricePointRow = 0
        pricePointColumn = 5 
        labelText = label.cget("text")
        if rowVal != pricePointRow and colVal != pricePointColumn:
            label.destroy()
            # 7 & 8
            self.grid_slaves(row = rowVal, column = 7)[0]["state"] = "disabled"
            self.grid_slaves(row = rowVal, column = 8)[0]["state"] = "disabled"
        self.t = tk.Entry(self) 
        self.t.insert(END, labelText)
        self.t.grid(row= rowVal, column = colVal)
        if rowVal == pricePointRow and colVal == pricePointColumn:
            self.t.bind("<Return>", lambda e, rowVal = rowVal, colVal = colVal: self.AlterPricePointValue(rowVal, colVal))
        elif colVal ==3:
            self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal: self.changeIngredientNameThenReturnToLabel(rowVal, colVal, labelText, "name"))
        elif colVal ==2:
            self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal: self.changeIngredientNameThenReturnToLabel(rowVal, colVal, labelText, "rawMaterialNumber"))
        elif colVal ==4:
            ingred = self.grid_slaves(row = rowVal, column = 3)[0]
            self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal: self.changeIngredientNameThenReturnToLabel(rowVal, colVal, ingred['text'], "pricePerLB"))
        else: self.t.bind("<Return>", lambda e, rowVal = rowVal, colVal = colVal: self.ReturnToLabel(rowVal, colVal))
        self.ListOfWidgets.append(self.t)

    def changeFormulaName(self):
        # row 0 column 1
        labelText = self.label.cget("text")
        title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        self.entry = tk.Entry(self, font = title_font, width = 15) 
        self.entry.insert(END, labelText)
        self.entry.grid(row= 0, column = 1, columnspan = 3)
        self.entry.bind("<Return>", lambda e: self.returnFormulaLabel())
        self.label.config(fg = self.backgroundColor)
        

    def returnFormulaLabel(self):
        self.label.destroy()
        rowVal = 0
        colVal = 1
        entryToRemove = self.grid_slaves(row = rowVal, column = colVal)[0]
        labelContent = entryToRemove.get()
        entryToRemove.destroy()
        title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        self.label = tk.Label(self, text = labelContent, font=title_font) 
        self.label.grid(row= rowVal, column = colVal, columnspan = 3)
        self.label.bind("<Button-1>",lambda e: self.changeFormulaName())
        self.ttr.name = labelContent
        

    # Checks to see if the name change is successfully in the back end, returns entry to label
    def changeIngredientNameThenReturnToLabel(self, rowVal: int, colVal: int, labelText: str, contentType: str):
        didItWork = self.changeIngredientName(labelText, contentType, rowVal, colVal)
        if didItWork == True:
            if contentType == "name":
                self.modifySolventAndVariList(rowVal, labelText)
            self.ReturnToLabel(rowVal, colVal)
            self.create_charts()


    def modifySolventAndVariList(self, rowVal: int, labelText: str):
        # get new value
        newValue = self.grid_slaves(row = rowVal, column = 3)[0].get()
        # does list of vari contain labelText?
        if labelText in self.ListOfVari:
            # if so delete labelText
            self.ListOfVari.remove(labelText)
            # add new value
            self.ListOfVari.append(newValue)
        # does list of solvent contain labelText
        if labelText in self.ListOfSolvents:
            # if so delete labelText
            self.ListOfSolvents.remove(labelText)
            # add new value
            self.ListOfSolvents.append(newValue)

        self.dictOfIngredientsAndRows.pop(labelText)
        self.dictOfIngredientsAndRows[newValue] = rowVal

        print("This is the new dict")
        for x in self.dictOfIngredientsAndRows:
            print(x)

    def changeIngredientName(self, oldIngredientName: str, contentType: str, rowVal: int, colVal: int) -> bool:
        newIngredientName = self.grid_slaves(row = rowVal, column = colVal)[0].get()
        if newIngredientName == "":
            return
        if contentType == "name":
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == oldIngredientName:
                    self.ttr.testTubes[i].name = newIngredientName 
                    return True 
        elif contentType == "rawMaterialNumber":
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].rawMaterialNumber == oldIngredientName: 
                    self.ttr.testTubes[i].rawMaterialNumber = newIngredientName 
                    return True
        elif contentType == "pricePerLB":
            try:
                float(newIngredientName)
            except ValueError:
                return False
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == oldIngredientName: 
                    self.ttr.testTubes[i].pricePerPound = float(newIngredientName)
                    self.updateCurrentPrice()
                    self.updateIngredientCost(rowVal)
                    return True
        return False

    def updateIngredientCost(self, rowVal: int):
        ingredientName = self.grid_slaves(row= rowVal, column=3)[0].cget("text")
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName: 
                newIngredientCost = self.ttr.testTubes[i].getCost()
        self.grid_slaves(row= rowVal, column=6)[0].delete(0, END)
        self.grid_slaves(row= rowVal, column=6)[0].insert(END, newIngredientCost)

    def updateIngredientConcentration(self, rowVal: int):
        ingredientName = self.grid_slaves(row = rowVal, column = 3)[0].cget("text")
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName: 
                newIngredientCost = self.ttr.testTubes[i].concentration
        self.grid_slaves(row= rowVal, column=5)[0].delete(0, END)
        self.grid_slaves(row= rowVal, column=5)[0].insert(END, newIngredientCost)

    def openNewIngredientWindow(self):
        top = Toplevel()
        titleFont = tkfont.Font(family='Helvetica', size=15, weight="bold", slant="italic")
        Label(top, text = "Add New Ingredient", font = titleFont).grid(row = 0, column = 0, columnspan = 2)
        Label(top, text = "Raw Material Number: ").grid(row = 1, column = 0)
        Entry(top).grid(row=1, column = 1)
        Label(top, text = "Ingredient Name: ").grid(row = 2, column = 0)
        Entry(top).grid(row=2, column = 1)
        Label(top, text = "Price Per Pound: ").grid(row = 3, column = 0)
        Entry(top).grid(row=3, column = 1)
        Button(top, text = "Add", command = lambda top = top: self.getNewWindowValues(top)).grid(row =4, column = 0, columnspan = 2)
        # self, text = "Fill", command = lambda rowVal = rowVal, solvName=solvName: self.FillIngredient(rowVal, solvName)) 

    def getNewWindowValues(self, top):

        ab = top.grid_slaves(row=1, column = 1)[0].get()
        solvName = top.grid_slaves(row=2, column = 1)[0].get()
        ef = top.grid_slaves(row=3, column = 1)[0].get()

        if len(ab) == 0 or len(solvName) == 0:
            return
        try:
            float(ef)
        except ValueError:
            return

        if self.ttr.createRackTube(ab, solvName, float(ef), 0) == True:
            
            top.destroy()
            rowVal = self.lastIngredientRow 
            # Updates dictionary to include pairing for newest ingredient
            self.dictOfIngredientsAndRows[solvName] = rowVal

            self.vari = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddVari(rowVal))
            self.vari.grid(row= rowVal, column = 0)
            self.ListOfWidgets.append(self.vari)

            self.sol = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddSolvent(rowVal))
            self.sol.grid(row= rowVal, column = 1)
            self.ListOfWidgets.append(self.sol)

            self.z = tk.Label(self, text = ab) 
            self.z.grid(row= rowVal, column = 2)
            self.ListOfWidgets.append(self.z)
            self.z.bind("<Button-1>",lambda e, z=self.z, rowVal = rowVal:self.changeLabel(z, rowVal, 2))

            self.x = tk.Label(self, text = solvName) 
            self.x.grid(row= rowVal, column = 3)
            self.ListOfWidgets.append(self.x)
            self.x.bind("<Button-1>",lambda e, x=self.x, rowVal = rowVal:self.changeLabel(x, rowVal, 3))
                    
            self.y = tk.Label(self, text = ef) 
            self.y.grid(row= rowVal, column = 4)
            self.ListOfWidgets.append(self.y)
            self.y.bind("<Button-1>",lambda e, y=self.y, rowVal = rowVal:self.changeLabel(y, rowVal, 4))

            self.t = tk.Entry(self) 
            self.t.insert(END, 0)
            self.t.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientConcentration(rowVal))
            self.t.grid(row= rowVal, column = 5)
            self.ListOfWidgets.append(self.t)

            self.m = tk.Entry(self) 
            self.m.insert(END, 0)
            self.m.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientPrice(rowVal))
            self.m.grid(row= rowVal, column = 6)
            self.ListOfWidgets.append(self.m)
                    
            self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal: self.FillIngredient(rowVal)) 
            self.q.grid(row= rowVal, column = 7)
            self.ListOfWidgets.append(self.q)
                    
            self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal: self.DeleteIngredient(rowVal)) 
            self.r.grid(row= rowVal, column = 8)
            self.ListOfWidgets.append(self.r)

            self.v = tk.Button(self, text = "↑", command = lambda rowVal = rowVal: self.MoveUp(rowVal)) 
            self.v.grid(row= rowVal, column = 9)
            self.ListOfWidgets.append(self.v)
            
            self.p = tk.Button(self, text = "↓", command = lambda rowVal = rowVal: self.MoveDown(rowVal)) 
            self.p.grid(row= rowVal, column = 10)
            self.ListOfWidgets.append(self.p)

            self.lastIngredientRow += 1
        

    def alterIngredientConcentration(self, rowVal):  
        ingredientName = self.grid_slaves(row= rowVal, column = 3)[0]['text']
        alteredConcentration = self.grid_slaves(row= rowVal, column = 5)[0].get()
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName: 
                try:
                    float(alteredConcentration)
                except ValueError:
                    self.grid_slaves(row= rowVal, column = 5)[0].clear()
                    self.grid_slaves(row= rowVal, column = 5)[0].insert(END, self.ttr.testTubes[i].concentration)
                self.ttr.alterRackTubeConcentration(ingredientName, float(alteredConcentration))
                self.grid_slaves(row= rowVal, column = 5)[0].delete(0, 'end')
                self.grid_slaves(row= rowVal, column = 5)[0].insert(END, self.ttr.testTubes[i].concentration)
        self.updateCurrentPrice()
        self.updateIngredientCost(rowVal)

    def alterIngredientPrice(self, rowVal):    
        ingredientName = self.grid_slaves(row= rowVal, column = 3)[0]['text']
        alteredConcentration = self.grid_slaves(row= rowVal, column = 6)[0].get()
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName: 
                try:
                    float(alteredConcentration)
                except ValueError:
                    self.grid_slaves(row= rowVal, column = 6)[0].clear()
                    self.grid_slaves(row= rowVal, column = 6)[0].insert(END, self.ttr.testTubes[i].getCost())
                self.ttr.alterRackTubePrice(ingredientName,float(alteredConcentration))
                self.grid_slaves(row= rowVal, column = 6)[0].delete(0, 'end')
                self.grid_slaves(row= rowVal, column = 6)[0].insert(END, self.ttr.testTubes[i].getCost())
        self.updateCurrentPrice()
        self.updateIngredientConcentration(rowVal)
              


    def ReturnToLabel(self, rowVal: int, colVal: int):
        entryToRemove = self.grid_slaves(row = rowVal, column = colVal)[0]
        labelContent = entryToRemove.get()
        entryToRemove.destroy()
        self.n = tk.Label(self, text = labelContent) 
        self.n.grid(row= rowVal, column = colVal)
        self.ListOfWidgets.append(self.n)
        self.n.bind("<Button-1>",lambda e, n=self.n, rowVal = rowVal, colVal = colVal:self.changeLabel(n, rowVal, colVal))
        # 7 & 8
        self.grid_slaves(row = rowVal, column = 7)[0]["state"] = "normal"
        self.grid_slaves(row = rowVal, column = 8)[0]["state"] = "normal"

    
    def AlterPricePointValue(self, rowVal: int, colVal: int):
        latestEntry = self.grid_slaves(row = rowVal, column = colVal)[0]
        newPricePoint = latestEntry.get()
        latestEntry.destroy()
        self.targetPriceValue.config(text = newPricePoint)
        try:
            self.ttr.changePricePoint(float(newPricePoint))
        except ValueError:
            self.targetPriceValue.config(text = str(self.ttr.pricePoint))


    def DeleteIngredient(self, rowVal: int):
        ingredientName = self.grid_slaves(row = rowVal, column = 3)[0]['text']
        # destroys the test tube for the chosen ingredient in the back end
        for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == ingredientName: 
                    del self.ttr.testTubes[i]
                    break
        # destroys all widgets for the chosen ingredient in the front end
        for j in range(0,11):
            self.grid_slaves(row = rowVal, column = j)[0].grid_remove()
        self.updateCurrentPrice()
        self.create_charts()
        self.CheckForVaris()
        self.removeFromSolvents(ingredientName)
        self.removeFromVari(ingredientName)
        self.dictOfIngredientsAndRows.pop(ingredientName)


    def removeFromSolvents(self, ingredientName: str):
        if ingredientName in self.ListOfSolvents:
            self.ListOfSolvents.remove(ingredientName)


    def removeFromVari(self, ingredientName: str):
        if ingredientName in self.ListOfVari:
            self.ListOfVari.remove(ingredientName)


    def MoveUp(self, rowVal: int) -> None:
        if rowVal == 6:
            return
        topRowVal = rowVal - 1
        topRMN = self.grid_slaves(row=topRowVal, column = 2)[0]['text']
        topsolvName = self.grid_slaves(row=topRowVal, column = 3)[0]['text']
        topPPLB = self.grid_slaves(row=topRowVal, column = 4)[0]['text']
        topConcentration = self.grid_slaves(row=topRowVal, column = 5)[0].get()
        topCost = self.grid_slaves(row=topRowVal, column = 6)[0].get()

        bottomRMN = self.grid_slaves(row=rowVal, column = 2)[0]['text']
        bottomsolvName = self.grid_slaves(row=rowVal, column = 3)[0]['text']
        bottomPPLB = self.grid_slaves(row=rowVal, column = 4)[0]['text']
        bottomConcentration = self.grid_slaves(row=rowVal, column = 5)[0].get()
        bottomCost = self.grid_slaves(row=rowVal, column = 6)[0].get()

        self.GenerateRow(topRowVal, "", "", bottomRMN, bottomsolvName, bottomPPLB, bottomConcentration, bottomCost)
        self.GenerateRow(rowVal, "", "", topRMN, topsolvName, topPPLB, topConcentration, topCost)
        
        self.ttr.swapIngredients(topsolvName, bottomsolvName)
        

    def MoveDown(self, rowVal: int) -> None:
        if rowVal >= (self.lastIngredientRow -1):
            return
        topRowVal = rowVal + 1
        topRMN = self.grid_slaves(row=topRowVal, column = 2)[0]['text']
        topsolvName = self.grid_slaves(row=topRowVal, column = 3)[0]['text']
        topPPLB = self.grid_slaves(row=topRowVal, column = 4)[0]['text']
        topConcentration = self.grid_slaves(row=topRowVal, column = 5)[0].get()
        topCost = self.grid_slaves(row=topRowVal, column = 6)[0].get()

        bottomRMN = self.grid_slaves(row=rowVal, column = 2)[0]['text']
        bottomsolvName = self.grid_slaves(row=rowVal, column = 3)[0]['text']
        bottomPPLB = self.grid_slaves(row=rowVal, column = 4)[0]['text']
        bottomConcentration = self.grid_slaves(row=rowVal, column = 5)[0].get()
        bottomCost = self.grid_slaves(row=rowVal, column = 6)[0].get()

        self.GenerateRow(topRowVal, "", "", bottomRMN, bottomsolvName, bottomPPLB, bottomConcentration, bottomCost)
        self.GenerateRow(rowVal, "", "", topRMN, topsolvName, topPPLB, topConcentration, topCost)

        self.ttr.swapIngredients(topsolvName, bottomsolvName)



    def GenerateRow(self, rowVal:int, variVal: str, solvVal:str, rmn: str, solvName: str, pricePerPound: float, concentration:float, cost:float) -> None:
        for y in range(0,11):
            self.grid_slaves(row= rowVal, column = y)[0].destroy()

        self.vari = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddVari(rowVal))
        if solvName in self.ListOfVari:
            self.vari.select()
        self.vari.grid(row= rowVal, column = 0)
        self.ListOfWidgets.append(self.vari)

        self.sol = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddSolvent(rowVal))
        if solvName in self.ListOfSolvents:
            self.sol.select()
        self.sol.grid(row= rowVal, column = 1)
        self.ListOfWidgets.append(self.sol)

        self.z = tk.Label(self, text = rmn) 
        self.z.grid(row= rowVal, column = 2)
        self.ListOfWidgets.append(self.z)
        self.z.bind("<Button-1>",lambda e, z=self.z, rowVal = rowVal: self.changeLabel(z, rowVal, 2))

        self.x = tk.Label(self, text = solvName) 
        self.x.grid(row= rowVal, column = 3)
        self.ListOfWidgets.append(self.x)
        self.x.bind("<Button-1>",lambda e, x=self.x, rowVal = rowVal: self.changeLabel(x, rowVal, 3))
        
        self.y = tk.Label(self, text = pricePerPound) 
        self.y.grid(row= rowVal, column = 4)
        self.ListOfWidgets.append(self.y)
        self.y.bind("<Button-1>",lambda e, y=self.y, rowVal = rowVal: self.changeLabel(y, rowVal, 4))

        self.t = tk.Entry(self) 
        self.t.insert(END, concentration)
        self.t.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientConcentration(rowVal))
        self.t.grid(row= rowVal, column = 5)
        self.ListOfWidgets.append(self.t)

        self.m = tk.Entry(self) 
        self.m.insert(END, cost)
        self.m.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientPrice(rowVal))
        self.m.grid(row= rowVal, column = 6)
        self.ListOfWidgets.append(self.m)
        
        self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal: self.FillIngredient(rowVal)) 
        self.q.grid(row= rowVal, column = 7)
        self.ListOfWidgets.append(self.q)
        
        self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal: self.DeleteIngredient(rowVal)) 
        self.r.grid(row= rowVal, column = 8)
        self.ListOfWidgets.append(self.r)

        self.v = tk.Button(self, text = "↑", command = lambda rowVal = rowVal: self.MoveUp(rowVal)) 
        self.v.grid(row= rowVal, column = 9)
        self.ListOfWidgets.append(self.v)
        
        self.p = tk.Button(self, text = "↓", command = lambda rowVal = rowVal: self.MoveDown(rowVal)) 
        self.p.grid(row= rowVal, column = 10)
        self.ListOfWidgets.append(self.p)



    def getIngredientNameFromRow(self, rowVal: int) -> str:
        return self.grid_slaves(row = rowVal, column = 3)[0]['text']


    def FillIngredient(self, rowVal: int):
        ingredName = self.getIngredientNameFromRow(rowVal)
        FillList = []
        FillList.append(ingredName)
        self.ttr.fillToConcentration(FillList)
        self.updateCurrentPrice()    
        self.updateIngredientConcentration(rowVal)
        self.updateIngredientCost(rowVal)

    def updateCurrentPrice(self):
        self.currentPriceValue.config(text = str(self.ttr.getCost()))
        self.create_charts()

    def create_charts(self):
        prices = []
        concentrations = []
        label1 = [] # Labels for the concentration pie chart
        label2 = [] # Labels for the cost pie chart
        explode1 = []
        explode2 = []
        totalFormulaCost = self.ttr.getCost()
        totalConcentration = 0

        for i in range(0,len(self.ttr.testTubes)):
            
            # Handles if the total formula cost is equal to zero
            if totalFormulaCost > 0:
                # if the cost of the ingredient is greater than 0, add its cost and label
                if self.ttr.testTubes[i].getCost() > 0:
                    prices.append(self.ttr.testTubes[i].getCost()/totalFormulaCost)
                    label2.append(self.ttr.testTubes[i].name)
                    explode2.append(0)
            else:
                prices.append(0)
                label2.append("No Cost")
                explode2.append(0)  
            
            # if the concentration is greater than 0 add the concentrtion and the label
            if self.ttr.testTubes[i].concentration > 0:
                concentrations.append(self.ttr.testTubes[i].concentration)
                label1.append(self.ttr.testTubes[i].name)
                explode1.append(0)
            
            totalConcentration += self.ttr.testTubes[i].concentration
            
            

        undefinedConcentration = 100 - totalConcentration

        if undefinedConcentration > 0:

            concentrations.append(undefinedConcentration)
            label1.append("Undefined")
            explode1.append(0)
        
        figure1 = Figure(figsize=(4,3), dpi=100) 
        subplot1 = figure1.add_subplot(111) 
        figure2 = Figure(figsize=(4,3), dpi=100) 
        figure2.set_facecolor("#f0f0f0")
        figure1.set_facecolor("#f0f0f0")
        subplot2 = figure2.add_subplot(111)  
        # pieSizes = [float(x1),float(x2),float(x3)]
        my_colors2 = ['lightblue','lightsteelblue', '#C85923', '#ECB471', '#A4596D', '#C0D6C0', '#8E5B5E', '#AABCD5']
      
        subplot2.pie(prices, colors=my_colors2, labels= label2, explode=explode2, autopct='%1.1f%%', shadow=False, startangle=90) 
        subplot1.pie(concentrations, colors=my_colors2, labels= label1, explode=explode1, autopct='%1.1f%%', shadow=False, startangle=90) 
        subplot2.axis('equal')  
        subplot1.axis('equal')  

        # subplot1.legend(label1, loc="center left", bbox_to_anchor=(0.7, 0.5))

        figure1.suptitle('Concentration', fontsize=15, fontweight="bold")
        figure2.suptitle('Price', fontsize=15, fontweight="bold")

        self.pie2 = FigureCanvasTkAgg(figure2, self)
        self.pie1 = FigureCanvasTkAgg(figure1, self)

        if totalConcentration > 0:
            self.pie1.get_tk_widget().grid(row = 3, column = 1, columnspan = 3)
        else:
            for i in self.grid_slaves(row=3, column = 1):
                i.destroy()
        
        if totalFormulaCost > 0:
            self.pie2.get_tk_widget().grid(row = 3, column = 4, columnspan = 3)
        else:
            for i in self.grid_slaves(row= 3, column = 4):
                    i.destroy()

    def clear_charts(self):
        self.grid_slaves(row = 3, column = 0)[0].destroy()
        self.grid_slaves(row = 3, column = 5)[0].destroy()

    def saveFormula(self):
        # get the current name of the formula
        newName = self.label['text']
        # get the name of the file which currently exists
        # self.currentFileName 
        self.formulaGenerator.saveFormula(newName, self.currentFileName, self.ttr)
        # set current name of formula as the file whcih currently exists
        self.currentFileName = newName

    def openFormula(self):
        # get the current name of the formula
        newName = self.label['text']
        # get the name of the file which currently exists
        # self.currentFileName 
        self.formulaGenerator.openExcelFile(newName, self.currentFileName, self.ttr)
        # set current name of formula as the file whcih currently exists
        self.currentFileName = newName

    def saveAsFormula(self) -> None:
        # get the current name of the formula
        newName = self.label['text']
        # get the name of the file which currently exists
        # self.currentFileName 
        SaveAsFormulaName = self.formulaGenerator.saveAsFormula(newName, self.currentFileName, self.ttr)
        # set current name of formula as the file whcih currently exists
        self.currentFileName = SaveAsFormulaName    
        self.label.config(text = SaveAsFormulaName)

    def deleteFormula(self):
        fileNameToDelete = self.currentFileName
        self.formulaGenerator.deleteFormula(fileNameToDelete)
        self.controller.show_frame("StartPage", "")


    def setFormula(self, formula: str):
        self.grid_slaves(row = 0, column = 1)
        self.ListOfSolvents.clear()
        self.ListOfVari.clear()
        # self.clear_charts()
        self.dictOfIngredientsAndRows = {}
        self.clearGrid(self.ListOfWidgets)
        self.formula = formula
        if self.grid_slaves(row= 0, column = 1)[0].winfo_class() == 'Entry':
            self.grid_slaves(row= 0, column = 1)[0].destroy()
            title_font =  tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
            self.label = tk.Label(self, text = formula, font=title_font)
            self.label.grid(row = 0, column = 1, columnspan = 3, rowspan = 2)
        self.label.config(text = self.formula)
        self.label.bind("<Button-1>",lambda e: self.changeFormulaName())

        self.u = tk.Button(self, text = "Save", command = lambda: self.saveFormula()) 
        self.u.grid(row= 0, column = 7)
        self.ListOfWidgets.append(self.u)

        self.h = tk.Button(self, text = "Save As", command = lambda: self.saveAsFormula()) 
        self.h.grid(row= 0, column = 8)
        self.ListOfWidgets.append(self.h)

        self.h = tk.Button(self, text = "Delete", command = lambda: self.deleteFormula()) 
        self.h.grid(row= 1, column = 8)
        self.ListOfWidgets.append(self.h)

        self.j = tk.Button(self, text = "Open", command = lambda: self.openFormula()) 
        self.j.grid(row= 1, column = 7)
        self.ListOfWidgets.append(self.j)
        
        self.formulaGenerator = rackMaker()

        if formula == "Create New Formula":
            uf= "Untitled Formula"
            rack = testTubeRack(uf, 0)
            self.label.config(text = uf)
            self.ttr = rack
            self.lastIngredientRow = 6
            self.currentFileName = ""
            self.targetPriceValue.config(text = "0")
            self.currentPriceValue.config(text = "0")
            if len(self.grid_slaves(row= 3, column = 1)) > 0:
                for i in self.grid_slaves(row= 3, column = 1):
                    i.destroy()
                for i in self.grid_slaves(row= 3, column = 4):
                    i.destroy()
        else:    
            ttr= self.formulaGenerator.createTestTubeRack(formula)
            self.currentFileName = formula
            self.ttr = ttr
            self.create_charts()
            self.targetPriceValue.config(text = str(ttr.pricePoint))
            self.currentPriceValue.config(text = str(ttr.getCost()))
            
            rowVal = 6
            for tt in ttr.testTubes:
                solvName = tt.name
                self.dictOfIngredientsAndRows[solvName] = rowVal

                self.vari = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddVari(rowVal))
                self.vari.grid(row= rowVal, column = 0)
                self.ListOfWidgets.append(self.vari)

                self.sol = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddSolvent(rowVal))
                self.sol.grid(row= rowVal, column = 1)
                self.ListOfWidgets.append(self.sol)

                self.z = tk.Label(self, text = tt.rawMaterialNumber) 
                self.z.grid(row= rowVal, column = 2)
                self.ListOfWidgets.append(self.z)
                self.z.bind("<Button-1>",lambda e, z=self.z, rowVal = rowVal: self.changeLabel(z, rowVal, 2))

                self.x = tk.Label(self, text = solvName) 
                self.x.grid(row= rowVal, column = 3)
                self.ListOfWidgets.append(self.x)
                self.x.bind("<Button-1>",lambda e, x=self.x, rowVal = rowVal: self.changeLabel(x, rowVal, 3))
                
                self.y = tk.Label(self, text = tt.pricePerPound) 
                self.y.grid(row= rowVal, column = 4)
                self.ListOfWidgets.append(self.y)
                self.y.bind("<Button-1>",lambda e, y=self.y, rowVal = rowVal: self.changeLabel(y, rowVal, 4))

                self.t = tk.Entry(self) 
                self.t.insert(END, tt.concentration)
                self.t.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientConcentration(rowVal))
                self.t.grid(row= rowVal, column = 5)
                self.ListOfWidgets.append(self.t)

                self.m = tk.Entry(self) 
                self.m.insert(END, tt.getCost())
                self.m.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientPrice(rowVal))
                self.m.grid(row= rowVal, column = 6)
                self.ListOfWidgets.append(self.m)
                
                self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal: self.FillIngredient(rowVal)) 
                self.q.grid(row= rowVal, column = 7)
                self.ListOfWidgets.append(self.q)
                
                self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal: self.DeleteIngredient(rowVal)) 
                self.r.grid(row= rowVal, column = 8)
                self.ListOfWidgets.append(self.r)

                self.v = tk.Button(self, text = "↑", command = lambda rowVal = rowVal: self.MoveUp(rowVal)) 
                self.v.grid(row= rowVal, column = 9)
                self.ListOfWidgets.append(self.v)
                
                self.p = tk.Button(self, text = "↓", command = lambda rowVal = rowVal: self.MoveDown(rowVal)) 
                self.p.grid(row= rowVal, column = 10)
                self.ListOfWidgets.append(self.p)


                rowVal += 1
                self.lastIngredientRow = rowVal
            
               


    

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()