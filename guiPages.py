import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter import *
from soap import rackMaker, testTubeRack, testTube

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

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
            # print("it happened")
            self.frames[page_name].setFormula(formula)
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        ttr = rackMaker()
        xcelFiles = ttr.getNamesOfExcelFiles()
        xcelFiles.insert(0, "Create New Formula")
        tk.Label(self, text = "Formula Select", font = controller.title_font).grid(row = 0, column = 2, columnspan = 2)
        t = 1
        y = 0
        for x in xcelFiles:
            # print(x)
            tk.Button(self, text = x, width = (100//6), height = 3, fg="white", bg ="teal", command=lambda x=x: controller.show_frame("PageOne", x)).grid(row = t, column = y)
            # command=lambda name=name: self.a(name)
            y += 1
            if y == 6:
                y = 0
                t += 1

        # button1 = tk.Button(self, text="Go to Page One", command=lambda: controller.show_frame("PageOne"))


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        self.ListOfWidgets = []
        self.ListOfSolvents = []
        self.ListOfVari = []
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
        self.variLabel.grid(row=2, column = 0)
        self.solvLabel = tk.Label(self, text= "Solvent")
        self.solvLabel.grid(row=2, column = 1)
        self.rawNumLabel = tk.Label(self, text= "Raw Material Number")
        self.rawNumLabel.grid(row=2, column = 2)
        self.ingredLabel = tk.Label(self, text= "Ingredient")
        self.ingredLabel.grid(row=2, column = 3)
        self.pplbLabel = tk.Label(self, text= "$/lb.")
        self.pplbLabel.grid(row=2, column = 4)
        self.concentrationLabel = tk.Label(self, text= "Concentration")
        self.concentrationLabel.grid(row=2, column = 5)
        self.concentrationLabel = tk.Label(self, text= "Total Price")
        self.concentrationLabel.grid(row=2, column = 6)
        self.currentPrice2 = tk.Label(self, text= "")
        self.CPriceLabel = tk.Label(self, text= "Total Cost:")
        
    def clearGrid(self, list_of_widgets):
        for widget in list_of_widgets:
            widget.destroy()     

    def AddVari(self, vari: str):
        if vari in self.ListOfVari: self.ListOfVari.remove(vari)
        else: self.ListOfVari.append(vari)
        # print(*self.ListOfVari, sep = "\n")

    def AddSolvent(self, solvent: str):
        if solvent in self.ListOfSolvents: self.ListOfSolvents.remove(solvent)
        else: self.ListOfSolvents.append(solvent)
        # print(*self.ListOfSolvents, sep = "\n")

    def changeLabel(self, label: Label, rowVal: int, colVal:int):
        labelText = label.cget("text")
        if rowVal != 0 and colVal != 5: 
            label.destroy()
        #print(str(rowVal)+","+str(colVal))
        self.t = tk.Entry(self) 
        self.t.insert(END, labelText)
        self.t.grid(row= rowVal, column = colVal)
        # if colVal ==3:
        #     self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal, t=self.t:self.changeIngredientNameThenReturnToLabel(self.t.get(), rowVal, colVal, t, labelText, "name"))
        # elif colVal ==2:
        #     self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal, t=self.t:self.changeIngredientNameThenReturnToLabel(self.t.get(), rowVal, colVal, t, labelText, "rawMaterialNumber"))
        # elif colVal ==4:
        #     ingred = self.grid_slaves(row = rowVal, column = 3)[0]
        #     self.t.bind("<Return>", lambda e, labelText = labelText, rowVal = rowVal, colVal = colVal, t=self.t:self.changeIngredientNameThenReturnToLabel(self.t.get(), rowVal, colVal, t, ingred['text'], "pricePerLB"))
        # else:
        #     self.t.bind("<Return>", lambda e, rowVal = rowVal, colVal = colVal, t=self.t:self.ReturnToLabel(self.t.get(), rowVal, colVal, t))
        # self.t.bind("<Return>", lambda e, rowVal = rowVal, colVal = colVal, t=self.t:self.ReturnToLabel(self.t.get(), rowVal, colVal, t))
        self.ListOfWidgets.append(self.t)

    def changeIngredientNameThenReturnToLabel(self, newIngredientName : str, rowVal: int, colVal: int, t: Entry, labelText: str, contentType: str):
        didItWork = self.changeIngredientName(newIngredientName, labelText, contentType)
        if didItWork == True:
            self.ReturnToLabel(newIngredientName, rowVal, colVal, t)

    def changeIngredientName(self, newIngredientName: str, oldIngredientName: str, contentType: str) -> bool:
        #print("new label: "+newIngredientName)  
        #print("old label: "+oldIngredientName+"<--")  
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
            # don't forget to update the total cost of the formula and the total cost of the various ingredients
            # self.updateIngredientCosts()
            # self.updateTotalCost()
            # which should be it's own method
            try:
                float(newIngredientName)
            except ValueError:
                return False
            for i in range(0,len(self.ttr.testTubes)):
                if self.ttr.testTubes[i].name == oldIngredientName: 
                    self.ttr.testTubes[i].pricePerPound = newIngredientName 
                    # self.updateCurrentPrice()
                    return True
            
                # print(self.ttr.testTubes[i].pricePerPound)
            #print("END")
        return False

    def ReturnToLabel(self, labelContent: str, rowVal: int, colVal: int, entry: Entry):
        if rowVal == 0 and colVal == 5:
            self.AlterPricePointValue(labelContent, rowVal, colVal, entry)
            return
        entry.destroy()
        #print(labelContent)
        self.n = tk.Label(self, text = labelContent) 
        self.n.grid(row= rowVal, column = colVal)
        self.ListOfWidgets.append(self.n)
        self.n.bind("<Button-1>",lambda e, n=self.n, rowVal = rowVal, colVal = colVal:self.changeLabel(n, rowVal, colVal))

    
    def AlterPricePointValue(self, labelContent: str, rowVal: int, colVal: int, entry: Entry):
        entry.destroy()
        self.targetPriceValue.config(text = labelContent)
        try:
            self.ttr.changePricePoint(float(labelContent))
        except ValueError:
            self.targetPriceValue.config(text = self.ttr.pricePoint)
        print("New Price Point: "+str(self.ttr.pricePoint))

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

    def updateCurrentPrice(self):
        self.currentPriceValue.config(text = str(self.ttr.getCost()))

    def setFormula(self, formula: str):
        self.ListOfSolvents.clear()
        self.ListOfVari.clear()
        self.clearGrid(self.ListOfWidgets)
        self.formula = formula
        self.label.config(text = self.formula)
        if formula == "Create New Formula":
            uf= "Untitled Formula"
            rack = testTubeRack(uf, 0)
            self.label.config(text = uf)
            self.ttr = rack
        else:    
            formulaGenerator = rackMaker()
            ttr= formulaGenerator.createTestTubeRack(formula)
            self.ttr = ttr
            self.targetPriceValue.config(text = str(ttr.pricePoint))
            self.currentPriceValue.config(text = str(ttr.getCost()))
            rowVal = 3
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
                self.t.grid(row= rowVal, column = 5)
                self.ListOfWidgets.append(self.t)

                self.m = tk.Entry(self) 
                self.m.insert(END, tt.getCost())
                self.m.grid(row= rowVal, column = 6)
                self.ListOfWidgets.append(self.m)
                
                self.q = tk.Button(self, text = "Fill") 
                self.q.grid(row= rowVal, column = 7)
                self.ListOfWidgets.append(self.q)
                
                self.r = tk.Button(self, text = "Delete", command = lambda rowVal = rowVal, solvName=solvName: self.DeleteIngredient(rowVal, solvName)) 
                # button = tk.Button(self, text="<- Back", command=lambda: controller.show_frame("StartPage", ""))
                self.r.grid(row= rowVal, column = 8)
                self.ListOfWidgets.append(self.r)

                rowVal += 1
               


    

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()