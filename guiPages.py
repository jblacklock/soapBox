import tkinter as tk                
from tkinter import font  as tkfont 
from tkinter import *
from tkinter import filedialog
from soap import rackMaker, testTubeRack, testTube
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import glob, os
from os import path
import numpy as np

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # configures the title
        self.title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # sets the title to soapbox
        Tk.title(self,"SoapBox")
        # Tk.iconbitmap(self, r"C:\Users\wcbla\Desktop\Python\soapBox\soapBox\Boxen.ico")
        # this array is necessary for adding pages in the future
        self.frames = {}
        # creates the formula page
        page_name = PageOne.__name__
        frame = PageOne(parent=container, controller=self)
        self.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.a_frame = PageOne(container, self)
        # Sets the first page the user sees
        self.show_frame("PageOne", "Create New Formula")



    # creates the menu bar
    def create_menu(self):
        self.menubar = tk.Menu(self)
        self['menu'] = self.menubar
        # creates file in menubar
        filemenu = Menu(self.menubar, tearoff=0)
        # option for creating new formula
        filemenu.add_command(label="New", command = lambda: self.show_frame("PageOne", "Create New Formula"))
        # option for opening previously existing formula
        filemenu.add_command(label="Open", command=self.openFormula)
        # option for saving formula
        filemenu.add_command(label="Save", command=lambda: self.frames["PageOne"].saveFormula())
        # option for Save As
        filemenu.add_command(label="Save As", command=lambda: self.frames["PageOne"].saveAsFormula())
        # option for opening .xlsx
        filemenu.add_command(label="Open .XLSX", command= lambda: self.frames["PageOne"].openFormula())
        # option for deleting formula
        filemenu.add_command(label="Delete", command= lambda: self.deleteFormula())
        # names option "File"
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=self.menubar)



    # deletes formula
    def deleteFormula(self):
        # calls deleteFormula method from page one
        # TODO: does this method even exist?
        self.frames["PageOne"].deleteFormula()
        # after deleting formula, opens new formula page
        self.show_frame("PageOne", "Create New Formula")



    # opens formula from .xlsx
    def openFormula(self):
        # sets current directory to location of source code 
        dirPath = os.path.dirname(__file__)    
        # create interface for users to select file
        FormulaFileName = filedialog.askopenfilename(initialdir=dirPath, title="Select Formula", filetypes = (("xlsx files","*.xlsx"),("all files","*.*")))
        # sets page with formula
        self.show_frame("PageOne", FormulaFileName)



    # displays page
    def show_frame(self, page_name: str, formula: str) -> None:
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        if page_name == "PageOne":
            # checks to make sure that the formula name is set
            if formula == "":
                return
            # sets formula to page
            self.frames[page_name].setFormula(formula)
            # creates menubar
            self.create_menu()
        frame.tkraise()



# Page One is the formula page
class PageOne(tk.Frame):

    # initializes the formula page
    def __init__(self, parent, controller):
        # sets background color
        self.backgroundColor = "#f0f0f0"
        # clears piechart #1
        self.pie1 = None
        # clears piechart #1
        self.pie2 = None
        # clears list of widgets
        self.ListOfWidgets = []
        # clears list of solvents
        self.ListOfSolvents = []
        # clears list of vari
        self.ListOfVari = []
        # resets last ingredient row to 0
        self.lastIngredientRow = 0
        # clears the test tube rack
        self.ttr = None
        tk.Frame.__init__(self, parent)
        self.controller = controller
        formula = "Error"
        # sets formula title
        self.label = tk.Label(self, text = formula, font=controller.title_font)
        self.label.grid(row = 0, column = 0, columnspan = 3, rowspan = 2)
        # sets target price label
        self.targetPrice = tk.Label(self, text = "Target Price:")
        self.targetPrice.grid(row = 0, column = 3)
        # sets formula density label
        self.Density = tk.Label(self, text = "Specific Gravity:")
        self.Density.grid(row = 0, column = 5)
        # sets price per gallon label
        self.PPG = tk.Label(self, text = "Price Per Gallon:")
        self.PPG.grid(row = 1, column = 5)
        # sets batch size label
        self.BSize = tk.Label(self, text = "Batch Size:")
        self.BSize.grid(row = 0, column = 7, columnspan = 4)
        # sets notes label
        self.Notes = tk.Label(self, text = "Notes:")
        self.Notes.grid(row = 2, column = 3, columnspan = 9)
        # sets NoteText 
        self.NoteText = tk.Text(self, width = 80, height = 18)
        self.NoteText.grid(row = 3, column = 3, columnspan = 9)
        # updates NoteText whenever it is altered by the user
        self.NoteText.bind("<KeyRelease>", lambda e: self.UpdateNotes())
        # sets current price label
        self.currentPrice = tk.Label(self, text = "Current Price:")
        self.currentPrice.grid(row = 1, column = 3)
        # sets target price value
        self.targetPriceValue = tk.Label(self, text = "0")
        self.targetPriceValue.grid(row = 0, column = 4)
        # allows target price value to be altered by the user
        self.targetPriceValue.bind("<Button-1>",lambda e, targetPriceValue=self.targetPriceValue:self.changeLabel(targetPriceValue, 0, 4))
        # sets current price value
        self.currentPriceValue = tk.Label(self, text = "0")
        self.currentPriceValue.grid(row = 1, column = 4)
        # sets vari label
        self.variLabel = tk.Label(self, text= "Vari")
        self.variLabel.grid(row=5, column = 0)
        # sets solvent label
        self.solvLabel = tk.Label(self, text= "Solvent")
        self.solvLabel.grid(row=5, column = 1)
        # sets raw material label
        self.rawNumLabel = tk.Label(self, text= "Raw Material Number")
        self.rawNumLabel.grid(row=5, column = 2)
        # sets ingredient label
        self.ingredLabel = tk.Label(self, text= "Ingredient")
        self.ingredLabel.grid(row=5, column = 3)
        # sets price per pound label
        self.pplbLabel = tk.Label(self, text= "$/lb.")
        self.pplbLabel.grid(row=5, column = 4)
        # sets concentration label
        self.concentrationLabel = tk.Label(self, text= "Concentration")
        self.concentrationLabel.grid(row=5, column = 5)
        # sets total price label
        self.concentrationLabel = tk.Label(self, text= "Total Price")
        self.concentrationLabel.grid(row=5, column = 6)
        # sets batching instruction label
        self.bInstructions = tk.Label(self, text= "Batching Instructions")
        self.bInstructions.grid(row=5, column = 11)
        self.currentPrice2 = tk.Label(self, text= "")
        # sets total cost label
        self.CPriceLabel = tk.Label(self, text= "Total Cost:")
        # creates fill vari to concentration button
        fillVariToConcentration = tk.Button(self, text="Fill Vari to Concentration", command=lambda: self.fillVariToConcentration())
        fillVariToConcentration.grid(row = 4, column = 2)
        # creates reduce vari to price button
        reduceVariToPrice = tk.Button(self, text="Reduce Vari to Price", command=lambda: self.reduceToPrice())
        reduceVariToPrice.grid(row = 4, column = 3)
        # creates fill vari to price button
        fillVariToPrice = tk.Button(self, text="Fill Vari to Price", command=lambda: self.fillVariToPrice())
        fillVariToPrice.grid(row = 4, column = 4)
        # creates add ingredient button
        addIngred = tk.Button(self, text="Add Ingredient", command = lambda: self.openNewIngredientWindow())
        self.CheckForVaris()
        addIngred.grid(row = 4, column = 1)
        


    # sets the Notes in the GUI
    def UpdateNotes(self):
        self.ttr.notes = self.grid_slaves(row = 3, column = 3)[0].get(1.0,END)



    # Makes vari buttons unclickable while there are no varis
    def CheckForVaris(self):
        # if there are no Varis, make the vari buttons unclickable
        # TODO: refactor - magic numbers
        if len(self.ListOfVari) == 0:
            self.grid_slaves(row = 4, column = 2)[0]["state"] = "disabled"
            self.grid_slaves(row = 4, column = 3)[0]["state"] = "disabled"
            self.grid_slaves(row = 4, column = 4)[0]["state"] = "disabled"
        else: 
            # if there are varis, allow users to click vari buttons
            self.grid_slaves(row = 4, column = 2)[0]["state"] = "normal"
            self.grid_slaves(row = 4, column = 3)[0]["state"] = "normal"
            self.grid_slaves(row = 4, column = 4)[0]["state"] = "normal"



    # destroys old widgets from previous formula
    def clearGrid(self, list_of_widgets):
        for widget in list_of_widgets:
            widget.destroy()     



    # updates current price, ingredient concentration, and ingredient cost
    def updatePriceConcentrationCost(self) -> None:
        self.updateCurrentPrice()
        for rowVal in self.dictOfIngredientsAndRows:
            self.updateIngredientConcentration(self.dictOfIngredientsAndRows[rowVal])
            self.updateIngredientCost(self.dictOfIngredientsAndRows[rowVal])



    # Calls fill vari to concentration from the front end to the backend
    def fillVariToConcentration(self):
        self.ttr.fillToConcentration(self.ListOfVari)
        # follows up change in concentration with changes to price, concentration, and cost
        self.updatePriceConcentrationCost()
    


    # reduces varis to price point and then fills the remaining concentration with solvents
    def reduceToPrice(self):
        self.ttr.increaseSolventWhenReduceToPricePoint(self.ListOfSolvents ,self.ListOfVari)
        self.updatePriceConcentrationCost()



    # reduces the solvents allowing varis to be filled to the pricepoint
    def fillVariToPrice(self):
        self.ttr.reduceSolventWhenFillToPricePoint(self.ListOfSolvents ,self.ListOfVari)
        self.updatePriceConcentrationCost()



    # adds or removes ingredients from the list of vari
    def AddVari(self, rowVal: int):
        # get the name of the vari to be added from the row
        vari = self.getIngredientNameFromRow(rowVal) 
        # if the ingredient is already a vari, remove it from the list of vari
        if vari in self.ListOfVari: self.ListOfVari.remove(vari)
        # otherwise, add it to the list of vari
        else: self.ListOfVari.append(vari) 
        # check to see if the vari buttons should be enabled or not
        self.CheckForVaris()



    # adds or removes ingredients from the list of solvents
    def AddSolvent(self, rowVal: int):
        # get the name of the solvent to be added from the row
        solvent = self.getIngredientNameFromRow(rowVal)
        # if the ingredient is already a solvent, remove it from the list of solvents
        if solvent in self.ListOfSolvents: self.ListOfSolvents.remove(solvent)
        # otherwise, add it to the list of solvents
        else: self.ListOfSolvents.append(solvent)



    # replaces label with entry
    def changeLabel(self, label: Label, rowVal: int, colVal:int):
        # TODO: refactor, the next 2 lines should be elsewhere in this class
        pricePointRow = 0
        pricePointColumn = 4
        # get the content of the label
        labelText = label.cget("text")
        if rowVal != 0:
            # TODO: this may be the cause of the change ingredient name bug
            # destroy the label
            label.destroy()
            # disable name sensative actions on this row
            self.grid_slaves(row = rowVal, column = 7)[0]["state"] = "disabled"
            self.grid_slaves(row = rowVal, column = 8)[0]["state"] = "disabled"
            self.grid_slaves(row = rowVal, column = 9)[0]["state"] = "disabled"
            self.grid_slaves(row = rowVal, column = 10)[0]["state"] = "disabled"
        # create a new entry
        self.t = tk.Entry(self)
        # insert the label content into the entry 
        self.t.insert(END, labelText)
        # place the entry in the label's place
        self.t.grid(row= rowVal, column = colVal)
        # if the label of the pricepoint is being changed, bind the function to the entry which changes price point
        if rowVal == pricePointRow and colVal == pricePointColumn:
            self.t.bind("<Return>", lambda e, rowVal = rowVal, colVal = colVal: self.AlterPricePointValue(rowVal, colVal))
        elif colVal ==3:
            # if the label of the ingredient name is being changed, bind the function to the entry which changes ingredient name
            self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal: self.changeIngredientNameThenReturnToLabel(rowVal, colVal, labelText, "name"))
        elif colVal ==2:
            # if the label of the rmn is being changed, bind the function to the entry which changes rmn
            self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal: self.changeIngredientNameThenReturnToLabel(rowVal, colVal, labelText, "rawMaterialNumber"))
        elif colVal ==4:
            # if the label of the price per lb is being changed, bind the function to the entry which changes price per lb
            # first get theingredient's name
            ingred = self.grid_slaves(row = rowVal, column = 3)[0]
            # then bind the function to the entry
            self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal: self.changeIngredientNameThenReturnToLabel(rowVal, colVal, ingred['text'], "pricePerLB"))
        # nothing should reach this else statement
        # if it does, the change won't be reflected in the backend
        else: self.t.bind("<Return>", lambda e, rowVal = rowVal, colVal = colVal: self.ReturnToLabel(rowVal, colVal))
        # add this entry to the list of widgets to be destroyed if the user selects a different formula
        self.ListOfWidgets.append(self.t)

    # changes the name of the formula
    def changeFormulaName(self):
        # gets the old name of the formula
        labelText = self.label.cget("text")
        title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        # creates an entry for changing the name of the formula
        self.entry = tk.Entry(self, font = title_font, width = 15)
        # inserts the old name into the entry 
        self.entry.insert(END, labelText)
        # places the entry
        self.entry.grid(row= 0, column = 0, columnspan = 3)
        # binds function to entry
        self.entry.bind("<Return>", lambda e: self.returnFormulaLabel())
        self.label.config(fg = self.backgroundColor)
        


    # replaces formula name entry with a new formula name label
    def returnFormulaLabel(self):
        # destroys old label
        self.label.destroy()
        rowVal = 0
        colVal = 0
        # gets content from entry
        entryToRemove = self.grid_slaves(row = rowVal, column = colVal)[0]
        labelContent = entryToRemove.get()
        # destroys entry
        entryToRemove.destroy()
        # creates new formula name label with new content
        title_font = tkfont.Font(family='Helvetica', size=30, weight="bold", slant="italic")
        self.label = tk.Label(self, text = labelContent, font=title_font) 
        # place the label
        self.label.grid(row= rowVal, column = colVal, columnspan = 3)
        # bind change formula name to label
        self.label.bind("<Button-1>",lambda e: self.changeFormulaName())
        # change name of the formula in the backend
        self.ttr.name = labelContent
        


    # Checks to see if the name change is successfully in the back end, returns entry to label
    def changeIngredientNameThenReturnToLabel(self, rowVal: int, colVal: int, labelText: str, contentType: str):
        # check to see if change was successful
        didItWork = self.changeIngredientName(labelText, contentType, rowVal, colVal)
        if didItWork == True:
            # if change was successful
            if contentType == "name":
                # make sure the change is reflected in the list of solvents and varis
                self.modifySolventAndVariList(rowVal, labelText)
            # replace the entry with a label
            self.ReturnToLabel(rowVal, colVal)
            # update the charts
            self.create_charts()



    # add or remove ingredient from list of solvents and varis
    def modifySolventAndVariList(self, rowVal: int, labelText: str):
        # get the name of the new value
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



    # changes the name, raw material number, or price per pound of the ingredient
    # TODO: change the name of this function
    def changeIngredientName(self, oldIngredientName: str, contentType: str, rowVal: int, colVal: int) -> bool:
        # getsentry content
        newIngredientName = self.grid_slaves(row = rowVal, column = colVal)[0].get()
        # exits if the entry is empty
        if newIngredientName == "":
            return
        # if the ingredient's name is changing...
        if contentType == "name":
            for i in range(0,len(self.ttr.testTubes)):
                # find the test tube with the old name
                if self.ttr.testTubes[i].name == oldIngredientName:
                    # and set the name of the test tube to the new name
                    self.ttr.testTubes[i].name = newIngredientName 
                    # list the change as successful
                    return True 
        # if the raw material number is changing...
        elif contentType == "rawMaterialNumber":
            # find the test tube with the old rmn...
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].rawMaterialNumber == oldIngredientName: 
                    # and replaces its rmn with the new rmn
                    self.ttr.testTubes[i].rawMaterialNumber = newIngredientName 
                    # return true to indicate the change was successful
                    return True
        # if the price per pound is changing
        elif contentType == "pricePerLB":
            try:
                # make sure the new value is a float
                float(newIngredientName)
            except ValueError:
                # if not, end the function and indicate that the change failed
                return False
            # then update everything related to price per pound
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == oldIngredientName: 
                    self.ttr.testTubes[i].pricePerPound = float(newIngredientName)
                    self.updateCurrentPrice()
                    self.updateIngredientCost(rowVal)
                    return True
        # changed value should only be a name, or an rmn, or a pplb
        return False



    # updates the cost of the ingredient
    def updateIngredientCost(self, rowVal: int):
        # TODO: getting ingredient name from rowval should be a seperate function
        ingredientName = self.grid_slaves(row= rowVal, column=3)[0].cget("text")
        # find the ingredient in the test tube rack
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName:
                # change the cost of the ingredient in the backend 
                newIngredientCost = round(self.ttr.testTubes[i].getCost(),5)
        # update the ingredient cost entry
        self.grid_slaves(row= rowVal, column=6)[0].delete(0, END)
        self.grid_slaves(row= rowVal, column=6)[0].insert(END, newIngredientCost)
        # update the batching instructions
        self.batchingInstructions()



    # updates the concentration of the ingredient
    def updateIngredientConcentration(self, rowVal: int):
        # get the ingredient name based on the row
        ingredientName = self.grid_slaves(row = rowVal, column = 3)[0].cget("text")
        for i in range(0,len(self.ttr.testTubes)):
            # find the test tube in the test tube rack and update its concentration in the backend
            if self.ttr.testTubes[i].name == ingredientName: 
                newIngredientCost = round(self.ttr.testTubes[i].concentration,5)
        # update the concentration entry
        self.grid_slaves(row= rowVal, column=5)[0].delete(0, END)
        self.grid_slaves(row= rowVal, column=5)[0].insert(END, newIngredientCost)



    # Allows user to add new ingredient to the formula
    def openNewIngredientWindow(self):
        # create new window
        top = Toplevel()
        titleFont = tkfont.Font(family='Helvetica', size=15, weight="bold", slant="italic")
        # create window title
        Label(top, text = "Add New Ingredient", font = titleFont).grid(row = 0, column = 0, columnspan = 2)
        # create rmn label and entry
        Label(top, text = "Raw Material Number: ").grid(row = 1, column = 0)
        Entry(top).grid(row=1, column = 1)
        # create ingredient name label and entry
        Label(top, text = "Ingredient Name: ").grid(row = 2, column = 0)
        Entry(top).grid(row=2, column = 1)
        # create price per pound label and entry
        Label(top, text = "Price Per Pound: ").grid(row = 3, column = 0)
        Entry(top).grid(row=3, column = 1)
        # creates submit button for window
        Button(top, text = "Add", command = lambda top = top: self.getNewWindowValues(top)).grid(row =4, column = 0, columnspan = 2)
        


    # retrieves values from new ingredient window
    def getNewWindowValues(self, top):
        # get rmn from ingredient window
        ab = top.grid_slaves(row=1, column = 1)[0].get()
        # get ingredient name from new ingredient window
        solvName = top.grid_slaves(row=2, column = 1)[0].get()
        # get pplb from new ingredient window
        ef = top.grid_slaves(row=3, column = 1)[0].get()
        # fails to add ingredient if ingredient name or rmn is empty
        if len(ab) == 0 or len(solvName) == 0:
            return
        try:
            # make sure pplb can be made a float
            float(ef)
        except ValueError:
            # if pplb can't be made into a float, return
            return
        # if the ingredient was successfully added to the backend, add it to the front end
        if self.ttr.createRackTube(ab, solvName, float(ef), 0) == True:
            # destroy the new ingredient window
            top.destroy()
            # get the next empty row in the GUI
            rowVal = self.lastIngredientRow 
            # Updates dictionary to include pairing for newest ingredient
            self.dictOfIngredientsAndRows[solvName] = rowVal
            # TODO: turn the code below into it's own method
            # Add new Vari button to frontend
            self.vari = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddVari(rowVal))
            self.vari.grid(row= rowVal, column = 0)
            self.ListOfWidgets.append(self.vari)
            # add new solvent button to front end
            self.sol = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddSolvent(rowVal))
            self.sol.grid(row= rowVal, column = 1)
            self.ListOfWidgets.append(self.sol)
            # add new rmn label to front end
            self.z = tk.Label(self, text = ab) 
            self.z.grid(row= rowVal, column = 2)
            self.ListOfWidgets.append(self.z)
            self.z.bind("<Button-1>",lambda e, z=self.z, rowVal = rowVal:self.changeLabel(z, rowVal, 2))
            # add new name label to frontend
            self.x = tk.Label(self, text = solvName) 
            self.x.grid(row= rowVal, column = 3)
            self.ListOfWidgets.append(self.x)
            self.x.bind("<Button-1>",lambda e, x=self.x, rowVal = rowVal:self.changeLabel(x, rowVal, 3))
            # add new pplb to frontend
            self.y = tk.Label(self, text = ef) 
            self.y.grid(row= rowVal, column = 4)
            self.ListOfWidgets.append(self.y)
            self.y.bind("<Button-1>",lambda e, y=self.y, rowVal = rowVal:self.changeLabel(y, rowVal, 4))
            # add new concentration entry to frontend
            self.t = tk.Entry(self) 
            self.t.insert(END, 0)
            self.t.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientConcentration(rowVal))
            self.t.grid(row= rowVal, column = 5)
            self.ListOfWidgets.append(self.t)
            # add new cost entry to frontend
            self.m = tk.Entry(self) 
            self.m.insert(END, 0)
            self.m.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientPrice(rowVal))
            self.m.grid(row= rowVal, column = 6)
            self.ListOfWidgets.append(self.m)
            # add new fill button to frontend
            self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal: self.FillIngredient(rowVal)) 
            self.q.grid(row= rowVal, column = 7)
            self.ListOfWidgets.append(self.q)
            # add new delete button to frontend
            self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal: self.DeleteIngredient(rowVal)) 
            self.r.grid(row= rowVal, column = 8)
            self.ListOfWidgets.append(self.r)
            # add new move up button to frontend
            self.v = tk.Button(self, text = "↑", command = lambda rowVal = rowVal: self.MoveUp(rowVal)) 
            self.v.grid(row= rowVal, column = 9)
            self.ListOfWidgets.append(self.v)
            # add new move down button to frontend
            self.p = tk.Button(self, text = "↓", command = lambda rowVal = rowVal: self.MoveDown(rowVal)) 
            self.p.grid(row= rowVal, column = 10)
            self.ListOfWidgets.append(self.p)
            # indicate that this row is no longer empty
            self.lastIngredientRow += 1
    


    # change an ingredients concentration
    def alterIngredientConcentration(self, rowVal):  
        # get ingredient name based on row
        ingredientName = self.grid_slaves(row= rowVal, column = 3)[0]['text']
        # get new ingredient concentration from frontend
        alteredConcentration = self.grid_slaves(row= rowVal, column = 5)[0].get()
        # find ingredient in the backend
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName: 
                try:
                    # make sure the new concentration is a float
                    float(alteredConcentration)
                except ValueError:
                    # if the new concentration is not a float, empty the entry
                    self.grid_slaves(row= rowVal, column = 5)[0].clear()
                    # and replace it with the old concentration
                    self.grid_slaves(row= rowVal, column = 5)[0].insert(END, round(self.ttr.testTubes[i].concentration,5))
                # Change the concentration in the backend
                self.ttr.alterRackTubeConcentration(ingredientName, float(alteredConcentration))
                # Change the concentration, to the concentration in the backend
                self.grid_slaves(row= rowVal, column = 5)[0].delete(0, 'end')
                self.grid_slaves(row= rowVal, column = 5)[0].insert(END, round(self.ttr.testTubes[i].concentration,5))
        # update the price of the formula
        self.updateCurrentPrice()
        # update the cost of the ingredient
        self.updateIngredientCost(rowVal)



    # Changes the price of the ingredient
    def alterIngredientPrice(self, rowVal):
        # finds ingredient Name based on row 
        ingredientName = self.grid_slaves(row= rowVal, column = 3)[0]['text']
        # gets new concentration
        alteredConcentration = self.grid_slaves(row= rowVal, column = 6)[0].get()
        # looks in backend for appropriate test tube
        for i in range(0,len(self.ttr.testTubes)):
            if self.ttr.testTubes[i].name == ingredientName: 
                try:
                    # makes sure that the new price is a float
                    float(alteredConcentration)
                except ValueError:
                    # if new price is not a float, return old price
                    self.grid_slaves(row= rowVal, column = 6)[0].clear()
                    self.grid_slaves(row= rowVal, column = 6)[0].insert(END, round(self.ttr.testTubes[i].getCost(),5))
                # alters price of ingredient in backend
                self.ttr.alterRackTubePrice(ingredientName,float(alteredConcentration))
                # changes price in frontend
                self.grid_slaves(row= rowVal, column = 6)[0].delete(0, 'end')
                self.grid_slaves(row= rowVal, column = 6)[0].insert(END, round(self.ttr.testTubes[i].getCost(),5))
        # updates current price of formula
        self.updateCurrentPrice()
        self.updateIngredientConcentration(rowVal)
              


    # returns entry to label
    def ReturnToLabel(self, rowVal: int, colVal: int):
        # finds the entry to be removed
        entryToRemove = self.grid_slaves(row = rowVal, column = colVal)[0]
        # gets text in entry
        labelContent = entryToRemove.get()
        # destroy entry
        entryToRemove.destroy()
        # makes new label based on entry
        self.n = tk.Label(self, text = labelContent) 
        # places label
        self.n.grid(row= rowVal, column = colVal)
        # adds label to list of widgets
        self.ListOfWidgets.append(self.n)
        self.n.bind("<Button-1>",lambda e, n=self.n, rowVal = rowVal, colVal = colVal:self.changeLabel(n, rowVal, colVal))
        # TODO: refactor - turn into loop
        # reactiates buttons based on ingredient name
        self.grid_slaves(row = rowVal, column = 7)[0]["state"] = "normal"
        self.grid_slaves(row = rowVal, column = 8)[0]["state"] = "normal"
        self.grid_slaves(row = rowVal, column = 9)[0]["state"] = "normal"
        self.grid_slaves(row = rowVal, column = 10)[0]["state"] = "normal"

    

    # Changes the price point of the formula
    def AlterPricePointValue(self, rowVal: int, colVal: int):
        # gets new value from entry
        latestEntry = self.grid_slaves(row = rowVal, column = colVal)[0]
        newPricePoint = latestEntry.get()
        # destroys entry
        latestEntry.destroy()
        # changes the value on the price point label
        self.targetPriceValue.config(text = newPricePoint)
        try:
            # make sure new price point is a float
            self.ttr.changePricePoint(float(newPricePoint))
        except ValueError:
            # if new price point is not a float, replace with old price point value
            self.targetPriceValue.config(text = str(self.ttr.pricePoint))



    # Deletes ingredient
    def DeleteIngredient(self, rowVal: int):
        # gets ingredient name based on row
        ingredientName = self.grid_slaves(row = rowVal, column = 3)[0]['text']
        # destroys the test tube for the chosen ingredient in the back end
        for i in range(0,len(self.ttr.testTubes)):
                # delete the test tube in the backend
                if self.ttr.testTubes[i].name == ingredientName: 
                    del self.ttr.testTubes[i]
                    break
        # destroys all widgets for the chosen ingredient in the front end
        for j in range(0,12):
            self.grid_slaves(row = rowVal, column = j)[0].grid_remove()
        # update the price of the formula
        self.updateCurrentPrice()
        # update charts
        self.create_charts()
        self.CheckForVaris()
        # update solvent list
        self.removeFromSolvents(ingredientName)
        # update vari list
        self.removeFromVari(ingredientName)
        self.dictOfIngredientsAndRows.pop(ingredientName)
        # update the batching instructions
        self.batchingInstructions()



    # remove an ingredient from the solvents list
    def removeFromSolvents(self, ingredientName: str):
        if ingredientName in self.ListOfSolvents:
            self.ListOfSolvents.remove(ingredientName)



    # remove an ingredient from the vari list
    def removeFromVari(self, ingredientName: str):
        if ingredientName in self.ListOfVari:
            self.ListOfVari.remove(ingredientName)



    # TODO: refactor to combine MoveUp and MoveDown function
    # Move an ingredient up 
    def MoveUp(self, rowVal: int) -> None:
        # Can't move a row higher than 6
        if rowVal == 6:
            return
        topRowVal = rowVal - 1
        # collect values from top row
        topRMN = self.grid_slaves(row=topRowVal, column = 2)[0]['text']
        topsolvName = self.grid_slaves(row=topRowVal, column = 3)[0]['text']
        topPPLB = self.grid_slaves(row=topRowVal, column = 4)[0]['text']
        topConcentration = self.grid_slaves(row=topRowVal, column = 5)[0].get()
        topCost = self.grid_slaves(row=topRowVal, column = 6)[0].get()
        topBatchSize = self.grid_slaves(row = topRowVal, column = 11)[0]['text']
        # collect values from bottom row
        bottomRMN = self.grid_slaves(row=rowVal, column = 2)[0]['text']
        bottomsolvName = self.grid_slaves(row=rowVal, column = 3)[0]['text']
        bottomPPLB = self.grid_slaves(row=rowVal, column = 4)[0]['text']
        bottomConcentration = self.grid_slaves(row=rowVal, column = 5)[0].get()
        bottomCost = self.grid_slaves(row=rowVal, column = 6)[0].get()
        bottomBatchSize = self.grid_slaves(row = rowVal, column = 11)[0]['text']
        # remove both items from the dictionary of ingredients and rows
        self.dictOfIngredientsAndRows.pop(topsolvName)
        self.dictOfIngredientsAndRows.pop(bottomsolvName)
        # create the top row
        self.GenerateRow(topRowVal, "", "", bottomRMN, bottomsolvName, bottomPPLB, bottomConcentration, bottomCost, bottomBatchSize)
        # create the bottom row
        self.GenerateRow(rowVal, "", "", topRMN, topsolvName, topPPLB, topConcentration, topCost, topBatchSize)
        # swap ingredients in the backend
        self.ttr.swapIngredients(topsolvName, bottomsolvName)
    


    # TODO: refactor to combine MoveUp and MoveDown function
    # Move an ingredient down
    def MoveDown(self, rowVal: int) -> None:
        # Can't move a row lower than the last ingredient row
        if rowVal >= (self.lastIngredientRow -1):
            return
        topRowVal = rowVal + 1
        # collect values from top row
        topRMN = self.grid_slaves(row=topRowVal, column = 2)[0]['text']
        topsolvName = self.grid_slaves(row=topRowVal, column = 3)[0]['text']
        topPPLB = self.grid_slaves(row=topRowVal, column = 4)[0]['text']
        topConcentration = self.grid_slaves(row=topRowVal, column = 5)[0].get()
        topCost = self.grid_slaves(row=topRowVal, column = 6)[0].get()
        topBatchSize = self.grid_slaves(row = topRowVal, column = 11)[0]['text']
        # collect values from bottom row
        bottomRMN = self.grid_slaves(row=rowVal, column = 2)[0]['text']
        bottomsolvName = self.grid_slaves(row=rowVal, column = 3)[0]['text']
        bottomPPLB = self.grid_slaves(row=rowVal, column = 4)[0]['text']
        bottomConcentration = self.grid_slaves(row=rowVal, column = 5)[0].get()
        bottomCost = self.grid_slaves(row=rowVal, column = 6)[0].get()
        bottomBatchSize = self.grid_slaves(row = rowVal, column = 11)[0]['text']
        # remove both items from the dictionary of ingredients and rows
        self.dictOfIngredientsAndRows.pop(topsolvName)
        self.dictOfIngredientsAndRows.pop(bottomsolvName)
        # create the top row
        self.GenerateRow(topRowVal, "", "", bottomRMN, bottomsolvName, bottomPPLB, bottomConcentration, bottomCost, bottomBatchSize)
        # create the bottom row
        self.GenerateRow(rowVal, "", "", topRMN, topsolvName, topPPLB, topConcentration, topCost, topBatchSize)
        # swap ingredients in the backend
        self.ttr.swapIngredients(topsolvName, bottomsolvName)



    # generate an ingredient row in the GUI
    def GenerateRow(self, rowVal:int, variVal: str, solvVal:str, rmn: str, solvName: str, pricePerPound: float, concentration:float, cost:float, batchSize:str) -> None:
        # destroy the content of cells in a given row
        for y in range(0,12):
            self.grid_slaves(row= rowVal, column = y)[0].destroy()
        # create check button for vari
        self.vari = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddVari(rowVal))
        if solvName in self.ListOfVari:
            self.vari.select()
        self.vari.grid(row= rowVal, column = 0)
        self.ListOfWidgets.append(self.vari)
        # create check button for solvent
        self.sol = tk.Checkbutton(self, padx = 20, command = lambda rowVal=rowVal: self.AddSolvent(rowVal))
        if solvName in self.ListOfSolvents:
            self.sol.select()
        self.sol.grid(row= rowVal, column = 1)
        self.ListOfWidgets.append(self.sol)
        # create label for rmn
        self.z = tk.Label(self, text = rmn) 
        self.z.grid(row= rowVal, column = 2)
        self.ListOfWidgets.append(self.z)
        self.z.bind("<Button-1>",lambda e, z=self.z, rowVal = rowVal: self.changeLabel(z, rowVal, 2))
        # create label for ingredient name
        self.x = tk.Label(self, text = solvName) 
        self.x.grid(row= rowVal, column = 3)
        self.ListOfWidgets.append(self.x)
        self.x.bind("<Button-1>",lambda e, x=self.x, rowVal = rowVal: self.changeLabel(x, rowVal, 3))
        # create label for price per pound
        self.y = tk.Label(self, text = pricePerPound) 
        self.y.grid(row= rowVal, column = 4)
        self.ListOfWidgets.append(self.y)
        self.y.bind("<Button-1>",lambda e, y=self.y, rowVal = rowVal: self.changeLabel(y, rowVal, 4))
        # create entry for concentration
        self.t = tk.Entry(self) 
        self.t.insert(END, concentration)
        self.t.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientConcentration(rowVal))
        self.t.grid(row= rowVal, column = 5)
        self.ListOfWidgets.append(self.t)
        # create entry for ingredient cost
        self.m = tk.Entry(self) 
        self.m.insert(END, cost)
        self.m.bind("<Return>", lambda e, rowVal = rowVal: self.alterIngredientPrice(rowVal))
        self.m.grid(row= rowVal, column = 6)
        self.ListOfWidgets.append(self.m)
        # create fill button
        self.q = tk.Button(self, text = "Fill", command = lambda rowVal = rowVal: self.FillIngredient(rowVal)) 
        self.q.grid(row= rowVal, column = 7)
        self.ListOfWidgets.append(self.q)
        # create delete button
        self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal: self.DeleteIngredient(rowVal)) 
        self.r.grid(row= rowVal, column = 8)
        self.ListOfWidgets.append(self.r)
        # create button to move ingredient up
        self.v = tk.Button(self, text = "↑", command = lambda rowVal = rowVal: self.MoveUp(rowVal)) 
        self.v.grid(row= rowVal, column = 9)
        self.ListOfWidgets.append(self.v)
        # create button to move ingredient down
        self.p = tk.Button(self, text = "↓", command = lambda rowVal = rowVal: self.MoveDown(rowVal)) 
        self.p.grid(row= rowVal, column = 10)
        self.ListOfWidgets.append(self.p)
        # create label for batch size
        self.bs = tk.Label(self, text = batchSize) 
        self.bs.grid(row= rowVal, column = 11)
        self.ListOfWidgets.append(self.bs)
        self.bs.bind("<Button-1>",lambda e, bs=self.bs, rowVal = rowVal: self.changeLabel(bs, rowVal, 11))
        # add ingredient row
        self.dictOfIngredientsAndRows[solvName] = rowVal



    # TODO: hook everything up to this method
    # gets ingredient name given row
    def getIngredientNameFromRow(self, rowVal: int) -> str:
        return self.grid_slaves(row = rowVal, column = 3)[0]['text']



    # fills an ingredient to the highest concentration possible
    def FillIngredient(self, rowVal: int):
        # find the ingredient name
        ingredName = self.getIngredientNameFromRow(rowVal)
        # send ingredient to backend to be filled
        FillList = []
        FillList.append(ingredName)
        self.ttr.fillToConcentration(FillList)
        # update the current price of the formula
        self.updateCurrentPrice()    
        # update ingredient concentration in front end
        self.updateIngredientConcentration(rowVal)
        # update ingredient cost in front end
        self.updateIngredientCost(rowVal)



    # update the current price of the formula in the front end
    def updateCurrentPrice(self):
        # adjust the current price label
        self.currentPriceValue.config(text = str(round(self.ttr.getCost(),5)))
        # update the pie graphs
        self.create_charts()
        # update the price per gallon of the formula
        self.showPricePerGallon()




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
        subplot2.pie(prices, colors=my_colors2, labels= label2, explode=explode2, autopct='%1.1f%%', shadow=False, startangle=90, radius=1000) 
        subplot1.pie(concentrations, colors=my_colors2, labels= label1, explode=explode1, autopct='%1.1f%%', shadow=False, startangle=90, radius=1000) 
        subplot2.axis('equal')  
        subplot1.axis('equal')  
        # subplot1.legend(label1, loc="center left", bbox_to_anchor=(0.7, 0.5))
        figure1.suptitle('Concentration', fontsize=15, fontweight="bold")
        figure2.suptitle('Price', fontsize=15, fontweight="bold")
        self.pie2 = FigureCanvasTkAgg(figure2, self)
        self.pie1 = FigureCanvasTkAgg(figure1, self)
        # if totalConcentration > 0:
        #     self.pie1.get_tk_widget().grid(row = 3, column = 3, columnspan = 3)
        # else:
        #     for i in self.grid_slaves(row=3, column = 1):
        #         i.destroy()
        if totalFormulaCost > 0:
            self.pie2.get_tk_widget().grid(row = 3, column = 0, columnspan = 3)
        else:
            for i in self.grid_slaves(row= 3, column = 0):
                    i.destroy()



    # removes the old charts to make room for new charts
    def clear_charts(self):
        self.grid_slaves(row = 3, column = 0)[0].destroy()
        # self.grid_slaves(row = 3, column = 5)[0].destroy()




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
        self.formulaGenerator.openExcelFile(newName, self.currentFileName, self.ttr)
        # set current name of formula as the file whcih currently exists
        self.currentFileName = newName




    def saveAsFormula(self) -> None:
        # get the current name of the formula
        newName = self.label['text']
        # get the name of the file which currently exists
        SaveAsFormulaName = self.formulaGenerator.saveAsFormula(newName, self.currentFileName, self.ttr)
        # set current name of formula as the file whcih currently exists
        self.currentFileName = SaveAsFormulaName    
        self.label.config(text = SaveAsFormulaName)




    def showPricePerGallon(self) -> None:
        specificGravity = self.grid_slaves(column = 6, row = 0)[0].get()
        try:
            self.grid_slaves(column = 6, row = 1)[0].destroy()
        except:
            print("")
        try:
            value = self.ttr.pricePerGallon(float(specificGravity))
            self.ppg = tk.Label(self, text = round(value,5)) 
            self.ppg.grid(row= 1, column = 6)
            self.ListOfWidgets.append(self.ppg)
        except:
            return




    def batchingInstructions(self) -> None:
        batchSize = self.grid_slaves(column=11, row=0)[0].get()
        try: 
            value = self.ttr.batchingInstructions(float(batchSize))
            for x in range(0,len(value)):
                ingredName = value[x][0]
                properRow = self.dictOfIngredientsAndRows[ingredName]
                labelContent = round(value[x][1],5)
                self.quantity = tk.Label(self, text = labelContent)
                if len(self.grid_slaves(row= properRow, column=11)) > 0:
                    self.grid_slaves(row= properRow, column = 11)[0].destroy()
                self.quantity.grid(row = properRow, column = 11)
                self.ListOfWidgets.append(self.quantity)
        except:
            return
        
       


    def setFormula(self, formulaLocation: str):
        if formulaLocation != "Create New Formula":
            formula = formulaLocation[:-5]
            locaysh = formulaLocation.rfind("/")
            formula = formula[locaysh + 1:]
        else: 
            formula = formulaLocation
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
        
        self.specificGravity = tk.Entry(self)
        self.specificGravity.insert(END, 1)
        self.specificGravity.bind("<Return>", lambda e: self.showPricePerGallon())
        self.specificGravity.grid(row = 0, column = 6)
        self.ListOfWidgets.append(self.specificGravity)

        # Entry to determine batch size 4
        self.batchSize = tk.Entry(self)
        self.batchSize.insert(END, 1)
        self.batchSize.bind("<Return>", lambda e: self.batchingInstructions())
        self.batchSize.grid(row = 0, column = 11)
        self.ListOfWidgets.append(self.batchSize)
        self.formulaGenerator = rackMaker()
        self.NoteText.delete('1.0', END)

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
                for i in self.grid_slaves(row= 3, column = 0):
                    i.destroy()
                # for i in self.grid_slaves(row= 3, column = 4):
                #     i.destroy()
        else:    
            ttr= self.formulaGenerator.createTestTubeRack(formula, formulaLocation)
            self.currentFileName = formula
            self.ttr = ttr
            self.create_charts()
            self.showPricePerGallon()
            self.targetPriceValue.config(text = str(ttr.pricePoint))
            self.currentPriceValue.config(text = str(round(ttr.getCost(),5)))
            self.NoteText.insert(INSERT, self.ttr.notes)
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
            self.batchingInstructions()
            
               


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
