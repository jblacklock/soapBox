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
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        ttr = rackMaker()
        xcelFiles = ttr.getNamesOfExcelFiles()
        xcelFiles.insert(0, "Create New Formula")
        tk.Label(self, text = "Formula Select", font = controller.title_font).grid(row = 0, column = 0, columnspan = 3)
        t = 1
        y = 0
        for x in xcelFiles:
            tk.Button(self, text = x, width = (100//6), height = 3, fg="white", bg ="teal", command=lambda x=x: controller.show_frame("PageOne", x)).grid(row = t, column = y)
            y += 1
            if y == 6:
                y = 0
                t += 1

        # button1 = tk.Button(self, text="Go to Page One", command=lambda: controller.show_frame("PageOne"))


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        self.pie1 = None
        self.pie2 = None
        self.ListOfWidgets = []
        self.ListOfSolvents = []
        self.ListOfVari = []
        self.lastIngredientRow = 0
        self.ttr = None
        tk.Frame.__init__(self, parent)
        self.controller = controller
        formula = "poop"
        button = tk.Button(self, text="<- Back", command=lambda: controller.show_frame("StartPage", ""))
        button.grid(row = 0, column = 0)
        self.label = tk.Label(self, text = formula, font=controller.title_font)
        self.label.grid(row = 0, column = 1, columnspan = 3, rowspan = 2)
        self.targetPrice = tk.Label(self, text = "Target Price:")
        self.targetPrice.grid(row = 0, column = 4)
        self.currentPrice = tk.Label(self, text = "Current Price:")
        self.currentPrice.grid(row = 1, column = 4)
        self.targetPriceValue = tk.Label(self, text = "")
        self.targetPriceValue.grid(row = 0, column = 5)
        self.targetPriceValue.bind("<Button-1>",lambda e, targetPriceValue=self.targetPriceValue:self.changeLabel(targetPriceValue, 0, 5))
        self.currentPriceValue = tk.Label(self, text = "")
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
        addIngred.grid(row = 4, column = 1)
        
    def clearGrid(self, list_of_widgets):
        for widget in list_of_widgets:
            widget.destroy()     

    def fillVariToConcentration(self):
        self.ttr.fillToConcentration(self.ListOfVari)
        self.updateCurrentPrice()
        print("done")

    # the backend logic for this is shit
    def reduceToPrice(self):
        self.ttr.increaseSolventWhenReduceToPricePoint(self.ListOfSolvents ,self.ListOfVari)
        self.updateCurrentPrice()
        print("done")

    def fillVariToPrice(self):
        self.ttr.reduceSolventWhenFillToPricePoint(self.ListOfSolvents ,self.ListOfVari)
        self.updateCurrentPrice()
        print("done")
        

    def AddVari(self, vari: str):
        if vari in self.ListOfVari: self.ListOfVari.remove(vari)
        else: self.ListOfVari.append(vari)
        print(*self.ListOfVari, sep = "\n")

    def AddSolvent(self, solvent: str):
        if solvent in self.ListOfSolvents: self.ListOfSolvents.remove(solvent)
        else: self.ListOfSolvents.append(solvent)
        print(*self.ListOfSolvents, sep = "\n")

    def changeLabel(self, label: Label, rowVal: int, colVal:int):
        pricePointRow = 0
        pricePointColumn = 5 
        labelText = label.cget("text")
        if rowVal != pricePointRow and colVal != pricePointColumn:
            label.destroy()
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
        # TODO: deal with file saving weirdness
        # row 0 column 1
        labelText = self.label.cget("text")
        title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        self.entry = tk.Entry(self, font = title_font, width = 15) 
        self.entry.insert(END, labelText)
        self.entry.grid(row= 0, column = 1, columnspan = 3)
        self.entry.bind("<Return>", lambda e: self.returnFormulaLabel())
        

    def returnFormulaLabel(self):
        # TODO: deal with file saving weirdness
        self.label.destroy()
        rowVal = 0
        colVal = 1
        entryToRemove = self.grid_slaves(row = rowVal, column = colVal)[0]
        labelContent = entryToRemove.get()
        print("this is the labelContent: "+labelContent)
        entryToRemove.destroy()
        title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        self.label = tk.Label(self, text = labelContent, font=title_font) 
        self.label.grid(row= rowVal, column = colVal, columnspan = 3)
        self.label.bind("<Button-1>",lambda e: self.changeFormulaName())
        


    def changeIngredientNameThenReturnToLabel(self, rowVal: int, colVal: int, labelText: str, contentType: str):
        didItWork = self.changeIngredientName(labelText, contentType, rowVal, colVal)
        if didItWork == True:
            self.ReturnToLabel(rowVal, colVal)

    def changeIngredientName(self, oldIngredientName: str, contentType: str, rowVal: int, colVal: int) -> bool:
        newIngredientName = self.grid_slaves(row = rowVal, column = colVal)[0].get()
        if contentType == "name":
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == oldIngredientName:
                    self.ttr.testTubes[i].name = newIngredientName 
                    print("This is the new name of the ingredient: "+self.ttr.testTubes[i].name)
                    return True 
        elif contentType == "rawMaterialNumber":
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].rawMaterialNumber == oldIngredientName: 
                    self.ttr.testTubes[i].rawMaterialNumber = newIngredientName 
                    print("This is the new rmn of the ingredient: "+self.ttr.testTubes[i].rawMaterialNumber)
                    return True
        elif contentType == "pricePerLB":
            try:
                float(newIngredientName)
            except ValueError:
                return False
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == oldIngredientName: 
                    self.ttr.testTubes[i].pricePerPound = float(newIngredientName) 
                    print("This is the new $/lb. of the ingredient: "+str(self.ttr.testTubes[i].pricePerPound))
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
        ingredientName = self.grid_slaves(row= rowVal, column=3)[0].cget("text")
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
        print("here they are: "+ab+", "+solvName+", "+ef)
        try:
            float(ef)
        except ValueError:
            return
        if self.ttr.createRackTube(ab, solvName, float(ef), 0) == True:
            top.destroy()
            rowVal = self.lastIngredientRow
            self.vari = tk.Checkbutton(self, padx = 20, command = lambda solvName=solvName: self.AddVari(solvName))
            self.vari.grid(row= rowVal, column = 0)
            self.ListOfWidgets.append(self.vari)

            self.sol = tk.Checkbutton(self, padx = 20, command = lambda solvName=solvName: self.AddSolvent(solvName))
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
                    
            self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal, solvName=solvName: self.FillIngredient(rowVal, solvName)) 
            self.q.grid(row= rowVal, column = 7)
            self.ListOfWidgets.append(self.q)
                    
            self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal, solvName=solvName: self.DeleteIngredient(rowVal, solvName)) 
            self.r.grid(row= rowVal, column = 8)
            self.ListOfWidgets.append(self.r)

            self.lastIngredientRow += 1
        print(*self.ttr.testTubes)                     

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
                print("New cost: "+str(self.ttr.testTubes[i].concentration))
                self.grid_slaves(row= rowVal, column = 5)[0].insert(END, self.ttr.testTubes[i].concentration)
        self.updateCurrentPrice()
        self.updateIngredientCost(rowVal)
        print("here")

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
                print("New cost: "+str(self.ttr.testTubes[i].getCost()))
                self.grid_slaves(row= rowVal, column = 6)[0].insert(END, self.ttr.testTubes[i].getCost())
        self.updateCurrentPrice()
        self.updateIngredientConcentration(rowVal)
        print("here")
              


    def ReturnToLabel(self, rowVal: int, colVal: int):
        entryToRemove = self.grid_slaves(row = rowVal, column = colVal)[0]
        labelContent = entryToRemove.get()
        print("this is the labelContent: "+labelContent)
        entryToRemove.destroy()
        self.n = tk.Label(self, text = labelContent) 
        self.n.grid(row= rowVal, column = colVal)
        self.ListOfWidgets.append(self.n)
        self.n.bind("<Button-1>",lambda e, n=self.n, rowVal = rowVal, colVal = colVal:self.changeLabel(n, rowVal, colVal))

    
    def AlterPricePointValue(self, rowVal: int, colVal: int):
        latestEntry = self.grid_slaves(row = rowVal, column = colVal)[0]
        newPricePoint = latestEntry.get()
        latestEntry.destroy()
        self.targetPriceValue.config(text = newPricePoint)
        try:
            self.ttr.changePricePoint(float(newPricePoint))
        except ValueError:
            self.targetPriceValue.config(text = str(self.ttr.pricePoint))
        print("The pricepoint is: "+str(self.ttr.pricePoint))

    def addIngredient(self, rwm = str, name = str, pplb = str):
        print("New RWM: "+rwm)
        print("New Name: "+name)
        print("New PPLB: "+pplb)


    def DeleteIngredient(self, rowVal: int, ingredientName: str):
        for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == ingredientName: 
                    del self.ttr.testTubes[i]
                    break
        for l in range(0,len(self.ttr.testTubes)):
            print(self.ttr.testTubes[l].name)
        print("END formula")
        for j in range(0,9):
            self.grid_slaves(row = rowVal, column = j)[0].grid_remove()
        self.updateCurrentPrice()
        self.create_charts()

    def FillIngredient(self, rowVal: int, ingredName: str):
        FillList = []
        FillList.append(ingredName)
        self.ttr.fillToConcentration(FillList)
        self.updateCurrentPrice()    

    def updateCurrentPrice(self):
        self.currentPriceValue.config(text = str(self.ttr.getCost()))
        self.create_charts()

    def create_charts(self):
        prices = []
        concentrations = []
        label1 = []
        label2 = []
        explode1 = []
        explode2 = []
        totalFormulaCost = self.ttr.getCost()
        totalConcentration = 0

        for i in range(0,len(self.ttr.testTubes)):
            prices.append(self.ttr.testTubes[i].getCost()/totalFormulaCost)
            concentrations.append(self.ttr.testTubes[i].concentration)
            totalConcentration += self.ttr.testTubes[i].concentration
            label1.append(self.ttr.testTubes[i].name)
            label2.append(self.ttr.testTubes[i].name)
            explode1.append(0)
            explode2.append(0)
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
    
        self.pie1.get_tk_widget().grid(row = 3, column = 1, columnspan = 3)
        self.pie2.get_tk_widget().grid(row = 3, column = 4, columnspan = 3)

    def clear_charts(self):
        self.grid_slaves(row = 3, column = 0)[0].destroy()
        self.grid_slaves(row = 3, column = 5)[0].destroy()

    # def saveFormula(self):
        # get the current name of the formula
        # get the name of the file which currently exists
        # destroy the file that currently exists
        # write the new file

    def setFormula(self, formula: str):
        self.grid_slaves(row = 0, column = 1)
        self.ListOfSolvents.clear()
        self.ListOfVari.clear()
        # self.clear_charts()
        self.clearGrid(self.ListOfWidgets)
        self.formula = formula
        if self.grid_slaves(row= 0, column = 1)[0].winfo_class() == 'Entry':
            self.grid_slaves(row= 0, column = 1)[0].destroy()
            title_font =  tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
            self.label = tk.Label(self, text = formula, font=title_font)
            self.label.grid(row = 0, column = 1, columnspan = 3, rowspan = 2)
        self.label.config(text = self.formula)
        self.label.bind("<Button-1>",lambda e: self.changeFormulaName())

        if formula == "Create New Formula":
            uf= "Untitled Formula"
            rack = testTubeRack(uf, 0)
            self.label.config(text = uf)
            self.ttr = rack
        else:    
            self.formulaGenerator = rackMaker()
            ttr= self.formulaGenerator.createTestTubeRack(formula)
            self.currentFileName = formula
            self.ttr = ttr
            self.create_charts()
            self.targetPriceValue.config(text = str(ttr.pricePoint))
            self.currentPriceValue.config(text = str(ttr.getCost()))

            self.u = tk.Button(self, text = "Save File", command = lambda: self.saveFormula()) 
            self.u.grid(row= 0, column = 7)
            self.ListOfWidgets.append(self.u)

            self.j = tk.Button(self, text = "Open File", command = lambda formulaName = self.ttr.name: self.formulaGenerator.openExcelFile(formulaName)) 
            self.j.grid(row= 1, column = 7)
            self.ListOfWidgets.append(self.j)
            
            rowVal = 6
            for tt in ttr.testTubes:
                solvName = tt.name

                self.vari = tk.Checkbutton(self, padx = 20, command = lambda solvName=solvName: self.AddVari(solvName))
                self.vari.grid(row= rowVal, column = 0)
                self.ListOfWidgets.append(self.vari)

                self.sol = tk.Checkbutton(self, padx = 20, command = lambda solvName=solvName: self.AddSolvent(solvName))
                self.sol.grid(row= rowVal, column = 1)
                self.ListOfWidgets.append(self.sol)

                self.z = tk.Label(self, text = tt.rawMaterialNumber) 
                self.z.grid(row= rowVal, column = 2)
                self.ListOfWidgets.append(self.z)
                self.z.bind("<Button-1>",lambda e, z=self.z, rowVal = rowVal:self.changeLabel(z, rowVal, 2))

                self.x = tk.Label(self, text = solvName) 
                self.x.grid(row= rowVal, column = 3)
                self.ListOfWidgets.append(self.x)
                self.x.bind("<Button-1>",lambda e, x=self.x, rowVal = rowVal:self.changeLabel(x, rowVal, 3))
                
                self.y = tk.Label(self, text = tt.pricePerPound) 
                self.y.grid(row= rowVal, column = 4)
                self.ListOfWidgets.append(self.y)
                self.y.bind("<Button-1>",lambda e, y=self.y, rowVal = rowVal:self.changeLabel(y, rowVal, 4))

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
                
                self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal, solvName=solvName: self.FillIngredient(rowVal, solvName)) 
                self.q.grid(row= rowVal, column = 7)
                self.ListOfWidgets.append(self.q)
                
                self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal, solvName=solvName: self.DeleteIngredient(rowVal, solvName)) 
                self.r.grid(row= rowVal, column = 8)
                self.ListOfWidgets.append(self.r)

                rowVal += 1
                self.lastIngredientRow = rowVal
            
               


    

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()