from typing import List, Any, Tuple
import openpyxl 
import xlsxwriter 
import pandas as pd
import xlrd
import glob, os

class testTube:

# create a testTube, name, price, concentration, and maxconcentration, however, maxConcentration is currently useless
    def __init__(self, maxConcentration: float, rawMaterialNumber, name: str, pricePerPound: float, concentration: float) -> None:
        if maxConcentration < 0:
            raise Exception("the formula is not allowed to have a maxconcentration below 0")
        if pricePerPound < 0:
            raise Exception("the formula is not allowed to have a pricePerPound below 0")
        if concentration < 0:
            raise Exception("the formula is not allowed to have a concentration below 0")
        if type(rawMaterialNumber) is int:
            rawMaterialNumber = str(rawMaterialNumber)
        self.rawMaterialNumber = rawMaterialNumber
        self.maxConcentration = maxConcentration # set the max concentration of a tube... not necessary since it will always be 100
        self.pricePerPound = pricePerPound # set price per pound of the chemical
        self.concentration = concentration # set the concentration of the chemical used in the "mixture"
        self.name = name # name of the chemical
        # i would also like to add a raw material number attribute to this object

# name of the testtube
    def __repr__(self) -> str:
        return self.name # return the name of the chemical
    
# increase the concentration of the tube by specified amount
    def addByConcentration(self, amount: float) -> bool:
        if amount + self.concentration > self.maxConcentration or amount < 0:
            return False
        self.concentration += amount
        return True

# decrease the concentration of the tube by specified amount
    def reduceByConcentration(self, amount: float) -> bool:
        if self.concentration - amount < 0 or amount < 0: # check to see if the amound will decrease concentration below 0 or amound is negative
            return False # dont do anything
        self.concentration -= amount # decrease the concentration of the chemical by the amount
        return True # return true, is returning a bool even necessary in this method?

# Set the concentration of the tube by replacing with amount
    def setCapacity(self, amount: float) -> bool:
        if amount > self.maxConcentration or amount < 0: # checking input bounds, this is using the max concentration attribute, but it could just be 100
            return False # is this necessary? can it be removed?
        self.concentration = amount # set the current concentration to the input "amount"
        return True # return true, necessary?

# get the cost of the tube = price/lb * concentration in the tube
    def getCost(self) -> float:
        return (self.pricePerPound * self.concentration) / 100 # Calculate and return the cost of the chemical in the mixture, based on concentration and price per pound

# reduce the concentration of the tube by this $amount
    def reduceByPrice(self, amount: float) -> bool:
        cost = self.getCost() # get the cost of the chemical using the getCost method
        newcost = cost - amount # calculate the new desired cost based on the amount and current cost
        if newcost < 0 or amount < 0: # check to make sure the cost is not out of bounds
            return False # necessary?...probably
        self.concentration = 100 * newcost / self.pricePerPound # calculate the new concentration
        return True

# increase the concentration of the tube by this $amount
    def addByPrice(self, amount: float) -> bool:
        newcost = self.getCost() + amount # calculate a new cost based off of the amount and current cost
        increasedConcentration = 100 * newcost / self.pricePerPound # calculate the new concentration based on the newcost
        if increasedConcentration > 100: # check that the concentration does not go out of bound
            return False
        self.concentration = increasedConcentration # set the new concentration
        return True

# if the concentration was filled relative to the $amount, what would the concentration be?
    def concentrationIfFillToPrice(self, amount: float) -> float:
        newcost = self.getCost() + amount # calculate the new cost based on the current cost and input amount
        increasedConcentration = 100 * newcost / self.pricePerPound # calculate the new concentration
        return increasedConcentration # return the increased concentration to be used later

# Set the concentration of the tube to 0
    def emptyTube(self) -> None:
        self.concentration = 0 # set the current concentration equal to 0

## Currently useless
# Based on a misunderstanding of requirements
    def checkCapacity(self) -> float:
        return self.maxConcentration - self.concentration # reduce the max concentration by the current concentration... useless

###################################################################################################################################

class testTubeRack:

# define a new testTubeRack
    def __init__(self, name: str, pricePoint: float) -> None:
        if pricePoint < 0:
            raise Exception("the formula is not allowed to have a pricepoint below 0")
        self.pricePoint = pricePoint # set the pricepoint argument
        self.testTubes = [] # add the testtube to the rack of tubes
        self.name = name # associate the name in the rack
        self.currentPrice = 0 # initialize the currentPrice of the rack, current price will be adjusted later? i think 

# name of the testTubeRack
    def __repr__(self) -> str:
        return self.name # return the name of the formula

# Report the formula name and pricepoint, then the ingredients and their corresponding concentrations
# Gives a high level overview of the formula, not really usefull for anything else... probably wont be implemented in the front end
    def formula(self) -> List[Any]:
        a = [] # initialize the formula variable
        a.append([self.name, self.pricePoint]) # first array will be the name of the formula, and the pricepoint of the formula
        for i in range(0, len(self.testTubes)): # the remaining arrays are the names of the testtubes and their corresponding concentrations in the formula 
            a.append([self.testTubes[i].name, self.testTubes[i].concentration])
        return a

    def createIngredientArray(self) -> List[Any]:
        finalList = []
        for t in self.testTubes:
            pNum = t.rawMaterialNumber
            desc = t.name
            quantity = t.concentration
            curCost = t.getCost()
            partialArray = [pNum, desc, quantity, curCost]
            finalList.append(partialArray)
        return finalList

    def exportFormula(self) -> None:
        workbook = xlsxwriter.Workbook('Formulas/'+self.name+'.xlsx') 
        worksheet = workbook.add_worksheet(self.name) 
        worksheet.write('B1', 'Part Number') 
        worksheet.write('C1', 'Description') 
        worksheet.write('E1', 'Quantity') 
        worksheet.write('F1', 'Current Cost')

        # Some data we want to write to the worksheet. 
        scores = self.createIngredientArray()
        
        # Start from the first cell. Rows and 
        # columns are zero indexed. 
        row = 1
        col = 1
        
        # Iterate over the data and write it out row by row. 
        for partNumber, Description, Quantity, currentCost in (scores): 
            worksheet.write(row, col, partNumber) 
            worksheet.write(row, col + 1, Description) 
            worksheet.write(row, col + 3, Quantity)
            worksheet.write(row, col + 4, currentCost)
            row += 1
        
        workbook.close()  
        
# change the target price of the rack
    def changePricePoint(self, amount: float) -> bool:
        if amount < 0: # check bounds
            return False
        self.pricePoint = amount # reset the pricepoint to the input amount    
        return True
    
## Based on misunderstanding of specifications, dangerous... (but not really dangerous) do not use!
    # def addTestTube(self, tube: testTube) -> None:
        # self.testTubes.append(tube)

# create a new tube, name, price/lb, and desired concentration
    def createRackTube(self, rawMaterialNumber, name: str, pricePerPound: float, concentration: float) -> bool:
        if concentration <=  self.unusedRackConcentration(): # check to see if the new concentration will push the total rack concentration over 100/ out of bounds
            self.testTubes.append(testTube(100,rawMaterialNumber,name,pricePerPound,concentration)) # add new chemical to the formula
            return True
        return False

# returns the total cost of the rack by suming the cost * concentration of each ingredient
    def getCost(self) -> float:
        totalCost = 0 # initialize the total cost
        for i in range(0, len(self.testTubes)): # loop through the length of the testtubes
            totalCost += self.testTubes[i].getCost() # calculate the total cost of the formula by adding the cost of each ingredient
        return totalCost

# returns the sum of the concentration of all ingredients in the rack
    def sumRackConcentration(self) -> float:
        totalConcentration = 0 # initialize totalConcentrations
        for i in range(0, len(self.testTubes)):
            totalConcentration += self.testTubes[i].concentration # Calculate the total concentration by adding each individual concentrations
        return totalConcentration

# return 100 - total Rack concentration. How much room is left to add ingredients?
    def unusedRackConcentration(self) -> float:
        return 100 - self.sumRackConcentration() # check the available concentration in the rack

# if the cost of the ingredients is greater than the pricepoint, decrease the concentration of each listed ingredient until 
# the pricpoint is reached. If an ingrdient reaches 0% concentration and the pricepoint is not reached, continue removing 
# the concentration evenly from the other listed ingredients.
    def reduceToPrice(self, reduceableIngredients: List[str]) -> None:
        reduceCurrentPriceBy = self.getCost() - self.pricePoint # calculate the new desired price of the formula
        if reduceCurrentPriceBy > 0: # make sure input is reasonable and not out of bounds
            N = len(reduceableIngredients) # reduceable ingredients may change later if concentration is set to 0, still need the initial amount of reduceable ingredients
            remainingReducableCost = reduceCurrentPriceBy # this is important for breaking the while loop, reducecurrentpriceby changes later
            ingredientPrices = [] # i need to get their prices in a for loop, initializing this variable here
            lowestCost = 0 # initializing the lowest cost of all the ingredients, used later
            while remainingReducableCost != 0: # condition to break the while loop, once all cost is accounted for, loop will be broken
                for i in range(0,len(self.testTubes)): # loop to get the position of the reduceable ingredients in the rack and important information
                    if self.testTubes[i].name in reduceableIngredients: # finds reduceable ingredients
                        ingredientPrices.append(self.testTubes[i].getCost()) # returns current cost of each ingredient
                lowestCost = min(ingredientPrices) # determine the lowest cost in the available reduceable ingredients
                if remainingReducableCost/N <= lowestCost: # this is important to know if we can or cannot evenly distribute the change in price to each ingredient
                    for i in range(0,len(self.testTubes)):
                        if self.testTubes[i].name in reduceableIngredients:
                            self.testTubes[i].reduceByPrice(remainingReducableCost/N) # evenly distribute the change in price to all reduceable ingredients
                    break # no need to check remainingreduceablecost while loop is satisfied, the math is good enough
                else: # if they are not evenly reduceable, first reduce everything by the lowest ingredient and remove it from the reduceable ingredients list
                    for i in range(0, len(self.testTubes)):
                        if self.testTubes[i].name in reduceableIngredients and self.testTubes[i].getCost() == lowestCost: # remove any ingredient with the same lowest cost
                            self.testTubes[i].reduceByPrice(lowestCost) # reduce all ingredients by the lowest price
                            remainingReducableCost -= lowestCost # necessary for breaking the while loop
                            reduceableIngredients.remove(self.testTubes[i].name) # if it is the lowest cost, remove from available ingredients
                            ingredientPrices.remove(lowestCost) # also remove the cost in the list of costs..
                            N-=1 # reduce the number of available ingredients. this is important... but i think my be unnecessary, see two lines up
                        elif self.testTubes[i].name in reduceableIngredients: # reduce ingredients that are greater than the lowest cost by the lowest costing ingredient
                            self.testTubes[i].reduceByPrice(lowestCost)
                            remainingReducableCost -= lowestCost # to break while loop if condition is satisfied
                    ingredientPrices = [] # reset the ingredient prices because prices and ingredients have changed at this point, but still in the while loop. reinitialize


        # while remainingReducableCost != 0:
        #     if remainingReducableCost/N <= 0:
        #         for i in range(0, len(testTubeRack)):
        #             if List[i] == self.testTubes[i]:
        #                 self.testTubes[i].reduceByPrice(remainingReducableCost/N)

        # self.testTube.reduceByPrice

# if the cost of the ingredients is less than the price point, increase the concentration of the listed ingredients
# until the price point is met. If the total concentration of the rack needs to exceed 100% to reach the price point 
# equally increase the price of each ingredient until the rack concentration = 100%
    def fillToPrice(self, increaseableIngredients: List[str]) -> None:
        addCurrentPriceBy = self.pricePoint - self.getCost() # calculate the price the formula needs to increase to
        concentrationIncrease = 0 # initialize concentration increase to later check for going out of bounds of the max concentration of the rack
        potentialNewConcentration = 0 # initialize the potential new concentration to later check if we are moving out of bounds
        if addCurrentPriceBy > 0:
            for i in range(0,len(self.testTubes)):
                if self.testTubes[i].name in increaseableIngredients: # find increaseable ingredients
                    potentialNewConcentration = self.testTubes[i].concentrationIfFillToPrice(addCurrentPriceBy/len(increaseableIngredients)) # determine what the concentration would be if allowed
                    concentrationIncrease += potentialNewConcentration - self.testTubes[i].concentration # calculate how much this increase would increase the overall concentration
            if concentrationIncrease > self.unusedRackConcentration(): # if the potential concentration greater than the available concentration in the rack
                addCurrentPriceBy = ((concentrationIncrease-(concentrationIncrease + self.sumRackConcentration() - 100)) / concentrationIncrease) * addCurrentPriceBy # recalculate a new price to increase everything evenly by to stay within bounds
            for i in range(0,len(self.testTubes)):
                if self.testTubes[i].name in increaseableIngredients:
                    self.testTubes[i].addByPrice(addCurrentPriceBy/len(increaseableIngredients)) # evenly increase concentration by the available price/number of increaseable ingredients

# Use the listed ingredients to make the total rack concentration = 100%
    def fillToConcentration(self, increaseableIngredients: List[str]) -> None:
        increaseConcentrationBy = self.unusedRackConcentration()
        if self.unusedRackConcentration() > 0: # check to make sure inputs are in bounds
            for i in range(0,len(self.testTubes)):
                if self.testTubes[i].name in increaseableIngredients: # find reduceable ingredients in the rack
                    self.testTubes[i].addByConcentration(increaseConcentrationBy / len(increaseableIngredients)) # increase ingredients evenly by available concentration/number of increaseable ingredients

# Set listed tubes concentration to 0 by calling empty tube in the testTube object
    def emptyTubes(self, emptyIngredients: List[str]) -> None:
        for i in range(0,len(self.testTubes)):
            if self.testTubes[i].name in emptyIngredients: # find ingredients in rack
                self.testTubes[i].emptyTube() # set concentraiton of the tube to 0

# Example: Current Tube cost = $4, amount = $10, increase tube concentration by $6
# if cost will increase concentration greater than unused rack concentration call fill to 100% concentration
    def increaseRackTubeToPrice(self, ingredient: str, amount: float) -> None:
        potentialNewConcentration = 0
        concentrationIncrease = 0
        indexValue = -1
        for i in range(0,len(self.testTubes)):
            if self.testTubes[i].name in ingredient: # find ingredients in rack
                potentialNewConcentration = self.testTubes[i].concentrationIfFillToPrice(amount - self.testTubes[i].getCost()) # calculate the potential new concentration
                concentrationIncrease += potentialNewConcentration - self.testTubes[i].concentration # calculate overall concentration increase
                indexValue = i
        if concentrationIncrease > self.unusedRackConcentration(): # check if adding the concentration increase will push the rack out of boundss
            self.fillToConcentration(ingredient) # if out of bounds fill to max concnentration
        else:
            self.testTubes[indexValue].addByPrice(amount - self.testTubes[indexValue].getCost()) # else fill to desired concentration

# Example: Current Tube Concentration = 4, amount = 10, increase tube concentration by 6
# if increase tube concentration will exceed 100 percent call fil to 100% concentration
    def increaseRackTubeToConcentration(self, ingredient: str, amount: float) -> None:
        for i in range(0, len(self.testTubes)):
            if self.testTubes[i].name in ingredient: # find ingredients in rack
                if amount - self.testTubes[i].concentration >= self.unusedRackConcentration(): # check to see if changing to the new amount will push rach concentration out of bounds
                    self.fillToConcentration([self.testTubes[i].name]) # if > 100 send concentration to max
                    break
                else:
                    self.testTubes[i].addByConcentration(amount - self.testTubes[i].concentration) # if < 100 change the concentration to the desired setpoint
                    break




# Example: Current Tube Cost = $10, amount = $4, reduce concentration by $6
# if amount is greater than tube cost or < 0, do nothing
    def decreaseRackTubeToPrice(self, ingredient: str, amount: float) -> None:
        if amount >= 0: # check amount bounds
            for i in range(0, len(self.testTubes)):
                if self.testTubes[i].name in ingredient: # find ingredients in rack
                    if self.testTubes[i].getCost() > amount: # reality check
                        self.testTubes[i].reduceByPrice(self.testTubes[i].getCost() - amount) # reduce price to the amount
                        break
                    else:
                        break



# Example: Current Tube concentration = 10, amount = 4, reduce concentration by 6
# if amount is greater than tube concentration or < 0, do nothing    
    def decreaseRackTubeToConcentration(self, ingredient: str, amount: float) -> None:
        if amount >= 0: # check bounds
            for i in range(0, len(self.testTubes)):
                if self.testTubes[i].name in ingredient: # find ingredients in rack
                    if self.testTubes[i].concentration > amount: # reality check
                        self.testTubes[i].reduceByConcentration(self.testTubes[i].concentration - amount) # decrease rack tube concentration to amount
                        break
                    else:
                        break



    def reduceSolventWhenFillToPricePoint(self, solvents: List[str], ingredientsToChange: List[str]) -> None:
        self.emptyTubes(solvents) # empty tubes selected as solvents in the list
        self.fillToPrice(ingredientsToChange) # fill the ingredients that can change
        self.fillToConcentration(solvents) # refill the solvents to max concentration



    def increaseSolventWhenFillToPricePoint(self, solvents: List[str], ingredientsToChange: List[str]) -> None:
        self.reduceToPrice(ingredientsToChange)
        self.fillToConcentration(solvents)

# TODO: Change concentrations, reduce and increase tube concentrations relative to another and price
# TODO: repr should be the name of the thing we are trying to make and the ingredients we are using @ their concentratinos
# TODO: Calculate the amount of water needed to finalize the formula
# TODO: Create a visual user interface wooooot - Find GUI library for python
# TODO: be able to delete a testtube from a testtube rack

#######################################################################################################################################################################

class rackMaker:

    def createTestTubeRack(self, formulaName: str) -> testTubeRack:
        # Give the location of the file 
        dirPath = os.path.dirname(__file__)    
        os.chdir(dirPath+"/Formulas")
        loc = (formulaName+'.xlsx') 
        # To open Workbook 
        wb = xlrd.open_workbook(loc) 
        sheet = wb.sheet_by_index(0) 
        i = sheet.nrows
        # sheet.row_values(1)
        targetValue = 0
        allTestubes = []
        for x in range(1, i):
            value = sheet.row_values(x)
            print(str(value[4])+"*"+str(value[5]))
            targetValue += value[4] * value[5]
            allTestubes.append(value)
        targetValue = targetValue/100
        ttr = testTubeRack(formulaName, targetValue)

        for tt in allTestubes:
            ttr.createRackTube(tt[1], tt[2], tt[5], tt[4])

        return ttr



    def getNamesOfExcelFiles(self) -> List[str]: 

        dirPath = os.path.dirname(__file__)    
        os.chdir(dirPath+"/Formulas")
        fileNames = []
        
        for file in glob.glob("*.xlsx"):
            file = file[:-5]
            fileNames.append(file)
        return fileNames
            

    
        