from typing import List, Any, Tuple
import openpyxl
import xlsxwriter
import pandas as pd
import xlrd
import glob
import os
import subprocess as sp
from os import path


class testTube:

    # create a testTube, name, price, concentration, and maxconcentration, however, maxConcentration is currently useless
    def __init__(self, maxConcentration: float, rawMaterialNumber, name: str, pricePerPound: float, concentration: float) -> None:
        if maxConcentration < 0:
            raise Exception(
                "the formula is not allowed to have a maxconcentration below 0")
        if pricePerPound < 0:
            raise Exception(
                "the formula is not allowed to have a pricePerPound below 0")
        if concentration < 0:
            raise Exception(
                "the formula is not allowed to have a concentration below 0")
        if type(rawMaterialNumber) is int:
            rawMaterialNumber = str(rawMaterialNumber)
        self.rawMaterialNumber = rawMaterialNumber
        # set the max concentration of a tube... not necessary since it will always be 100
        self.maxConcentration = maxConcentration
        self.pricePerPound = pricePerPound  # set price per pound of the chemical
        # set the concentration of the chemical used in the "mixture"
        self.concentration = concentration
        self.name = name  # name of the chemical
        # i would also like to add a raw material number attribute to this object

# name of the testtube
    def __repr__(self) -> str:
        return self.name  # return the name of the chemical

# increase the concentration of the tube by specified amount
    def addByConcentration(self, amount: float) -> bool:
        if amount + self.concentration > self.maxConcentration or amount < 0:
            return False
        self.concentration += amount
        return True

# decrease the concentration of the tube by specified amount
    def reduceByConcentration(self, amount: float) -> bool:
        # check to see if the amound will decrease concentration below 0 or amound is negative
        if self.concentration - amount < 0 or amount < 0:
            return False  # dont do anything
        # decrease the concentration of the chemical by the amount
        self.concentration -= amount
        return True  # return true, is returning a bool even necessary in this method?

    # NOTE: The following method is never used.
    # It has been preserved for the purposes of future use.
    def alterByConcentration(self, newConc: float) -> bool:
        difference = self.concentration - newConc
        if difference < 0:
            self.addByConcentration(difference * -1)
        if difference > 0:
            self.reduceByConcentration(difference)

    # NOTE: The following method is never used.
    # It has been preserved for the purposes of future use.
    def alterByPrice(self, newPrice: float) -> bool:
        difference = self.getCost() - newPrice
        if difference < 0:
            self.addByConcentration(difference * -1)
        if difference > 0:
            self.reduceByConcentration(difference)


# Set the concentration of the tube by replacing with amount

    def setCapacity(self, amount: float) -> bool:
        # checking input bounds, this is using the max concentration attribute, but it could just be 100
        if amount > self.maxConcentration or amount < 0:
            return False  # is this necessary? can it be removed?
        self.concentration = amount  # set the current concentration to the input "amount"
        return True  # return true, necessary?

# get the cost of the tube = price/lb * concentration in the tube
    def getCost(self) -> float:
        # Calculate and return the cost of the chemical in the mixture, based on concentration and price per pound
        return (self.pricePerPound * self.concentration) / 100

# reduce the concentration of the tube by this $amount
# FIXED! 04/07/2020 todo self.pricePerPound !=0 error handeling looks good?
    def reduceByPrice(self, amount: float) -> bool:
        if self.pricePerPound != 0:
            cost = self.getCost()  # get the cost of the chemical using the getCost method
            # calculate the new desired cost based on the amount and current cost
            newcost = cost - amount
            if newcost < 0 or amount < 0:  # check to make sure the cost is not out of bounds
                return False  # necessary?...probably
            self.concentration = 100 * newcost / \
                self.pricePerPound  # calculate the new concentration
            return True
        else:
            return True

# increase the concentration of the tube by this $amount
# FIXED! 04/07/2020 todo needs self.pricePerPound == 0 error
    def addByPrice(self, amount: float) -> bool:
        if self.pricePerPound != 0:
            # calculate a new cost based off of the amount and current cost
            newcost = self.getCost() + amount
            # calculate the new concentration based on the newcost
            increasedConcentration = 100 * newcost / self.pricePerPound
            if increasedConcentration > 100:  # check that the concentration does not go out of bound
                return False
            self.concentration = increasedConcentration  # set the new concentration
            return True
        else:
            return True

# if the concentration was filled relative to the $amount, what would the concentration be?
# FIXED! 04/07/2020 todo Handle $0 Price Per Pound divide by zero
    def concentrationIfFillToPrice(self, amount: float) -> float:
        if self.pricePerPound != 0:
            # calculate the new cost based on the current cost and input amount
            newcost = self.getCost() + amount
            increasedConcentration = 100 * newcost / \
                self.pricePerPound  # calculate the new concentration
            return increasedConcentration  # return the increased concentration to be used later
        else:
            return self.concentration

# Set the concentration of the tube to 0
    def emptyTube(self) -> None:
        self.concentration = 0  # set the current concentration equal to 0

# Currently useless
# Based on a misunderstanding of requirements
    def checkCapacity(self) -> float:
        # reduce the max concentration by the current concentration... useless
        return self.maxConcentration - self.concentration

###################################################################################################################################


class testTubeRack:

    # define a new testTubeRack
    def __init__(self, name: str, pricePoint: float) -> None:
        if pricePoint < 0:
            raise Exception(
                "the formula is not allowed to have a pricepoint below 0")
        self.pricePoint = pricePoint  # set the pricepoint argument
        self.testTubes = []  # add the testtube to the rack of tubes
        self.name = name  # associate the name in the rack
        self.notes = ""

    # Changes the order of the ingredients in the back-end
    def swapIngredients(self, ingredientOne: str, ingredientTwo: str) -> None:
        indexCounter = 0
        for tt in self.testTubes:
            if tt.name == ingredientOne:
                ingredientOneIndex = indexCounter
            if tt.name == ingredientTwo:
                ingredientTwoIndex = indexCounter
            indexCounter += 1
        tempTestTubeOne = self.testTubes[ingredientOneIndex]
        tempTestTubeTwo = self.testTubes[ingredientTwoIndex]
        self.testTubes[ingredientOneIndex] = tempTestTubeTwo
        self.testTubes[ingredientTwoIndex] = tempTestTubeOne

# name of the testTubeRack
    def __repr__(self) -> str:
        return self.name  # return the name of the formula

# Report the formula name and pricepoint, then the ingredients and their corresponding concentrations
# Gives a high level overview of the formula, not really usefull for anything else... probably wont be implemented in the front end
    def formula(self) -> List[Any]:
        a = []  # initialize the formula variable
        # first array will be the name of the formula, and the pricepoint of the formula
        a.append([self.name, self.pricePoint])
        # the remaining arrays are the names of the testtubes and their corresponding concentrations in the formula
        for i in range(0, len(self.testTubes)):
            a.append([self.testTubes[i].name, self.testTubes[i].concentration])
        return a

    def createIngredientArray(self) -> List[Any]:
        finalList = []
        for t in self.testTubes:
            pNum = t.rawMaterialNumber
            desc = t.name
            quantity = t.concentration
            curCost = t.pricePerPound
            partialArray = [pNum, desc, quantity, curCost]
            finalList.append(partialArray)
        return finalList

    def exportFormula(self) -> None:
        # somehow this is not creating the workbook
        workbook = xlsxwriter.Workbook(self.name + '.xlsx')
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

        worksheet.write(0, 8, self.pricePoint)
        worksheet.write(2, 8, self.notes)

        workbook.close()

# change the target price of the rack
    def changePricePoint(self, amount: float) -> bool:
        res = isinstance(amount, str)
        if res == True:
            return False
        if amount < 0:  # check bounds
            return False
        self.pricePoint = amount  # reset the pricepoint to the input amount
        return True

# Based on misunderstanding of specifications, dangerous... (but not really dangerous) do not use!
    # def addTestTube(self, tube: testTube) -> None:
        # self.testTubes.append(tube)

# create a new tube, name, price/lb, and desired concentration
    def createRackTube(self, rawMaterialNumber, name: str, pricePerPound: float, concentration: float) -> bool:
        # check to see if the new concentration will push the total rack concentration over 100/ out of bounds
        if concentration <= self.unusedRackConcentration():
            # add new chemical to the formula
            self.testTubes.append(
                testTube(100, rawMaterialNumber, name, pricePerPound, concentration))
            return True
        return False

# returns the total cost of the rack by suming the cost * concentration of each ingredient
    def getCost(self) -> float:
        totalCost = 0  # initialize the total cost
        for i in range(0, len(self.testTubes)):  # loop through the length of the testtubes
            # calculate the total cost of the formula by adding the cost of each ingredient
            totalCost += self.testTubes[i].getCost()
        return totalCost

# returns the sum of the concentration of all ingredients in the rack
    def sumRackConcentration(self) -> float:
        totalConcentration = 0  # initialize totalConcentrations
        for i in range(0, len(self.testTubes)):
            # Calculate the total concentration by adding each individual concentrations
            totalConcentration += self.testTubes[i].concentration
        return totalConcentration

# return 100 - total Rack concentration. How much room is left to add ingredients?
    def unusedRackConcentration(self) -> float:
        # check the available concentration in the rack
        return 100 - self.sumRackConcentration()

# if the cost of the ingredients is greater than the pricepoint, decrease the concentration of each listed ingredient until
# the pricpoint is reached. If an ingrdient reaches 0% concentration and the pricepoint is not reached, continue removing
# the concentration evenly from the other listed ingredients.
# FIXED! 04/07/2020 todo if N == 0 break out of this method? - Justification: nothing should change if N == 0
    def reduceToPrice(self, reduceableIngredients: List[str]) -> None:
        # calculate the new desired price of the formula
        reduceCurrentPriceBy = self.getCost() - self.pricePoint
        if reduceCurrentPriceBy > 0:  # make sure input is reasonable and not out of bounds
            if len(reduceableIngredients) <= 0:
                return
            # this is important for breaking the while loop, reducecurrentpriceby changes later
            remainingReducableCost = reduceCurrentPriceBy
            # i need to get their prices in a for loop, initializing this variable here
            ingredientPrices = []
            lowestCost = 0  # initializing the lowest cost of all the ingredients, used later
            while remainingReducableCost != 0:  # condition to break the while loop, once all cost is accounted for, loop will be broken
                # loop to get the position of the reduceable ingredients in the rack and important information
                for i in range(0, len(self.testTubes)):
                    # finds reduceable ingredients
                    if self.testTubes[i].name in reduceableIngredients:
                        # Fix 04/07/2020
                        if self.testTubes[i].getCost() != 0:
                            # returns current cost of each ingredient
                            ingredientPrices.append(
                                self.testTubes[i].getCost())
                        else:
                            reduceableIngredients.remove(
                                self.testTubes[i].name)
                            if len(reduceableIngredients) <= 0:
                                return
                if ingredientPrices == []:
                    return
                # determine the lowest cost in the available reduceable ingredients
                lowestCost = min(ingredientPrices)
                # this is important to know if we can or cannot evenly distribute the change in price to each ingredient
                if remainingReducableCost/len(reduceableIngredients) <= lowestCost:
                    for i in range(0, len(self.testTubes)):
                        if self.testTubes[i].name in reduceableIngredients:
                            # evenly distribute the change in price to all reduceable ingredients
                            self.testTubes[i].reduceByPrice(
                                remainingReducableCost/len(reduceableIngredients))
                    break  # no need to check remainingreduceablecost while loop is satisfied, the math is good enough
                else:  # if they are not evenly reduceable, first reduce everything by the lowest ingredient and remove it from the reduceable ingredients list
                    for i in range(0, len(self.testTubes)):
                        # remove any ingredient with the same lowest cost
                        if self.testTubes[i].name in reduceableIngredients and self.testTubes[i].getCost() == lowestCost:
                            # reduce all ingredients by the lowest price
                            self.testTubes[i].reduceByPrice(lowestCost)
                            remainingReducableCost -= lowestCost  # necessary for breaking the while loop
                            # if it is the lowest cost, remove from available ingredients
                            reduceableIngredients.remove(
                                self.testTubes[i].name)
                            # also remove the cost in the list of costs..
                            ingredientPrices.remove(lowestCost)
                        # reduce ingredients that are greater than the lowest cost by the lowest costing ingredient
                        elif self.testTubes[i].name in reduceableIngredients:
                            self.testTubes[i].reduceByPrice(lowestCost)
                            # to break while loop if condition is satisfied
                            remainingReducableCost -= lowestCost
                    ingredientPrices = []  # reset the ingredient prices because prices and ingredients have changed at this point, but still in the while loop. reinitialize

        # while remainingReducableCost != 0:
        #     if remainingReducableCost/len(reduceableIngredients) <= 0:
        #         for i in range(0, len(testTubeRack)):
        #             if List[i] == self.testTubes[i]:
        #                 self.testTubes[i].reduceByPrice(remainingReducableCost/len(reduceableIngredients))

        # self.testTube.reduceByPrice

# if the cost of the ingredients is less than the price point, increase the concentration of the listed ingredients
# until the price point is met. If the total concentration of the rack needs to exceed 100% to reach the price point
# equally increase the price of each ingredient until the rack concentration = 100%
# FIXED! 04/07/2020 todo if len(increaseableIngredeints) == 0 break out of this method
# Never a problem: todo concentration increaase != 0 error handeling

    def fillToPrice(self, increaseableIngredients: List[str]) -> None:
        # calculate the price the formula needs to increase to
        addCurrentPriceBy = self.pricePoint - self.getCost()
        # initialize concentration increase to later check for going out of bounds of the max concentration of the rack
        concentrationIncrease = 0
        # initialize the potential new concentration to later check if we are moving out of bounds
        potentialNewConcentration = 0
        if addCurrentPriceBy > 0:
            for i in range(0, len(self.testTubes)):
                # find increaseable ingredients
                if self.testTubes[i].name in increaseableIngredients:
                    if len(increaseableIngredients) <= 0:
                        return
                    potentialNewConcentration = self.testTubes[i].concentrationIfFillToPrice(
                        addCurrentPriceBy/len(increaseableIngredients))  # determine what the concentration would be if allowed
                    # calculate how much this increase would increase the overall concentration
                    concentrationIncrease += potentialNewConcentration - \
                        self.testTubes[i].concentration
            # if the potential concentration greater than the available concentration in the rack
            if concentrationIncrease > self.unusedRackConcentration():
                # recalculate a new price to increase everything evenly by to stay within bounds
                addCurrentPriceBy = ((concentrationIncrease-(concentrationIncrease +
                                                             self.sumRackConcentration() - 100)) / concentrationIncrease) * addCurrentPriceBy
            for i in range(0, len(self.testTubes)):
                if self.testTubes[i].name in increaseableIngredients:
                    # evenly increase concentration by the available price/number of increaseable ingredients
                    self.testTubes[i].addByPrice(
                        addCurrentPriceBy/len(increaseableIngredients))

# Use the listed ingredients to make the total rack concentration = 100%
    def fillToConcentration(self, increaseableIngredients: List[str]) -> None:
        increaseConcentrationBy = self.unusedRackConcentration()
        if self.unusedRackConcentration() > 0:  # check to make sure inputs are in bounds
            for i in range(0, len(self.testTubes)):
                # find reduceable ingredients in the rack
                if self.testTubes[i].name in increaseableIngredients:
                    # increase ingredients evenly by available concentration/number of increaseable ingredients
                    self.testTubes[i].addByConcentration(
                        increaseConcentrationBy / len(increaseableIngredients))

# Set listed tubes concentration to 0 by calling empty tube in the testTube object
    def emptyTubes(self, emptyIngredients: List[str]) -> None:
        for i in range(0, len(self.testTubes)):
            if self.testTubes[i].name in emptyIngredients:  # find ingredients in rack
                # set concentraiton of the tube to 0
                self.testTubes[i].emptyTube()

# Example: Current Tube cost = $4, amount = $10, increase tube concentration by $6
# if cost will increase concentration greater than unused rack concentration call fill to 100% concentration
    def increaseRackTubeToPrice(self, ingredient: str, amount: float) -> None:
        potentialNewConcentration = 0
        concentrationIncrease = 0
        indexValue = -1
        for i in range(0, len(self.testTubes)):
            if self.testTubes[i].name in ingredient:  # find ingredients in rack
                potentialNewConcentration = self.testTubes[i].concentrationIfFillToPrice(
                    amount - self.testTubes[i].getCost())  # calculate the potential new concentration
                concentrationIncrease += potentialNewConcentration - \
                    self.testTubes[i].concentration  # calculate overall concentration increase
                indexValue = i
        # check if adding the concentration increase will push the rack out of boundss
        if concentrationIncrease > self.unusedRackConcentration():
            # if out of bounds fill to max concnentration
            self.fillToConcentration(ingredient)
        else:
            # else fill to desired concentration
            self.testTubes[indexValue].addByPrice(
                amount - self.testTubes[indexValue].getCost())

# Example: Current Tube Concentration = 4, amount = 10, increase tube concentration by 6
# if increase tube concentration will exceed 100 percent call fil to 100% concentration
    def increaseRackTubeToConcentration(self, ingredient: str, amount: float) -> None:
        for i in range(0, len(self.testTubes)):
            if self.testTubes[i].name in ingredient:  # find ingredients in rack
                # check to see if changing to the new amount will push rach concentration out of bounds
                if amount - self.testTubes[i].concentration >= self.unusedRackConcentration():
                    # if > 100 send concentration to max
                    self.fillToConcentration([self.testTubes[i].name])
                    break
                else:
                    # if < 100 change the concentration to the desired setpoint
                    self.testTubes[i].addByConcentration(
                        amount - self.testTubes[i].concentration)
                    break

    def alterRackTubeConcentration(self, ingredient: str, amount: float) -> None:
        for i in range(0, len(self.testTubes)):
            if self.testTubes[i].name in ingredient:
                if self.testTubes[i].concentration > amount:
                    self.decreaseRackTubeToConcentration(ingredient, amount)
                else:
                    self.increaseRackTubeToConcentration(ingredient, amount)

    def alterRackTubePrice(self, ingredient: str, amount: float) -> None:
        for i in range(0, len(self.testTubes)):
            if self.testTubes[i].name in ingredient:
                if self.testTubes[i].getCost() > amount:
                    self.decreaseRackTubeToPrice(ingredient, amount)
                else:
                    self.increaseRackTubeToPrice(ingredient, amount)


# Example: Current Tube Cost = $10, amount = $4, reduce concentration by $6
# if amount is greater than tube cost or < 0, do nothing

    def decreaseRackTubeToPrice(self, ingredient: str, amount: float) -> None:
        if amount >= 0:  # check amount bounds
            for i in range(0, len(self.testTubes)):
                if self.testTubes[i].name in ingredient:  # find ingredients in rack
                    if self.testTubes[i].getCost() > amount:  # reality check
                        self.testTubes[i].reduceByPrice(
                            self.testTubes[i].getCost() - amount)  # reduce price to the amount
                        break
                    else:
                        break


# Example: Current Tube concentration = 10, amount = 4, reduce concentration by 6
# if amount is greater than tube concentration or < 0, do nothing

    def decreaseRackTubeToConcentration(self, ingredient: str, amount: float) -> None:
        if amount >= 0:  # check bounds
            for i in range(0, len(self.testTubes)):
                if self.testTubes[i].name in ingredient:  # find ingredients in rack
                    if self.testTubes[i].concentration > amount:  # reality check
                        # decrease rack tube concentration to amount
                        self.testTubes[i].reduceByConcentration(
                            self.testTubes[i].concentration - amount)
                        break
                    else:
                        break


# test for errors

    def reduceSolventWhenFillToPricePoint(self, solvents: List[str], ingredientsToChange: List[str]) -> None:
        # empty tubes selected as solvents in the list
        self.emptyTubes(solvents)
        # fill the ingredients that can change
        self.fillToPrice(ingredientsToChange)
        # refill the solvents to max concentration
        self.fillToConcentration(solvents)
        acceptableError = 0.00001
        # Converge to this error, this should be okay for $solvents
        while self.getCost() - self.pricePoint > acceptableError:
            oldCost = self.getCost()
            # reduce the price of the varis evenly
            self.reduceToPrice(ingredientsToChange)
            # Fill concentration of solvents
            self.fillToConcentration(solvents)
            newCost = self.getCost()
            if newCost >= oldCost:
                self.emptyTubes(ingredientsToChange)  # empty varies
                self.emptyTubes(solvents)  # empty solvents
                self.fillToPrice(solvents)
                return

    def increaseSolventWhenReduceToPricePoint(self, solvents: List[str], ingredientsToChange: List[str]) -> None:
        self.emptyTubes(solvents)  # empty solvents
        # reduce the ingredients to the price point
        self.reduceToPrice(ingredientsToChange)
        self.fillToConcentration(solvents)  # fill the solvents

        acceptableError = 0.00001
        # Converge to this error, this should be okay for $solvents
        while self.getCost() - self.pricePoint > acceptableError:
            oldCost = self.getCost()
            # reduce the price of the varis evenly
            self.reduceToPrice(ingredientsToChange)
            # Fill concentration of solvents
            self.fillToConcentration(solvents)
            newCost = self.getCost()
            if newCost >= oldCost:
                self.emptyTubes(ingredientsToChange)  # empty varies
                self.emptyTubes(solvents)  # empty solvents
                self.fillToPrice(solvents)
                return

    def batchingInstructions(self, batchSize: float) -> List[Any]:
        ingredientAmount = []  # initialize the list of names and batching amount
        for tt in self.testTubes:
            # append name of ingredient and batching amount
            ingredientAmount.append(
                [tt.name, tt.concentration * batchSize / 100])
            print(tt.name + ": " + str(tt.concentration))
        # return names and batching amount * Batching amount is in column 2
        return ingredientAmount

    def pricePerGallon(self, specificGravity: float) -> float:
        lbPerGram = 1/453.592  # conversion 1 lb == 453.592 grams
        mlPerGallon = 3785.41  # conversion 1 gallon == 3785.41 ml
        # Calculates the price per gallon. * requires specific gravity input
        return self.getCost() * lbPerGram * specificGravity * mlPerGallon

#######################################################################################################################################################################


class rackMaker:

    def createTestTubeRack(self, formulaName: str, formulaLoc: str) -> testTubeRack:
        # To open Workbook
        wb = xlrd.open_workbook(formulaLoc)
        sheet = wb.sheet_by_index(0)
        i = sheet.nrows
        # sheet.row_values(1)
        targetValue = 0
        allTestubes = []
        for x in range(1, i):
            value = sheet.row_values(x)
            if value[4] == "" and value[5] == "":
                break
            targetValue += value[4] * value[5]
            allTestubes.append(value)
        targetValue = targetValue/100
        ttr = testTubeRack(formulaName, targetValue)
        for tt in allTestubes:
            ttr.createRackTube(tt[1], tt[2], tt[5], tt[4])
        try:
            ttr.notes = sheet.cell(rowx=2, colx=8).value
        except:
            print("")
        try:
            ttr.pricePoint = float(sheet.cell(rowx=0, colx=8).value)
        except:
            print("")

        return ttr

    def saveFormula(self, fileName: str, oldFileName: str, ttr: testTubeRack) -> None:
        # for new formula, set "oldFileName" to ""
        # no alteration needed for new formula
        dirPath = r"C:\Users\wcbla\Desktop\SoapBoxFormulas"
        os.chdir(dirPath)
        if oldFileName != "":
            # destroy oldFileName
            os.remove(oldFileName + ".xlsx")
        # write the new file
        ttr.name = fileName
        ttr.exportFormula()

    def saveAsFormula(self, fileName: str, oldFileName: str, ttr: testTubeRack) -> str:
        # no alteration needed for new formula
        dirPath = r"C:\Users\wcbla\Desktop\SoapBoxFormulas"
        os.chdir(dirPath)
        # if filename exists  in directory
        if path.exists(fileName + ".xlsx"):
            # if the last value of filename is )
            if fileName[-1] == ")":
                # if filename has a (
                if "(" in fileName:
                    openParenth = fileName.rfind("(")
                    potentialFileNumber = fileName[openParenth + 1:-1]
                    # if the content between the open parenthese and close parenthese type(int()) == type(int)
                    try:
                        # then int('number') + 1
                        newInt = int(potentialFileNumber) + 1
                        # TODO: check to see if that save file already exists:
                        # if it does, increment up until you can find a file name that hasn't been used yet
                        newFormulaName = fileName[0:openParenth -
                                                  1] + " (" + str(newInt) + ")"
                        self.saveFormula(newFormulaName, "", ttr)
                        ttr.name = newFormulaName
                        return newFormulaName
                    except:
                        # save a newFile with the same name but + "(1)"
                        newFormulaName = fileName + " (1)"
                        # TODO: check to see if that save file already exists:
                        # if it does, increment up until you can find a file name that hasn't been used yet
                        self.saveFormula(newFormulaName, "", ttr)
                        ttr.name = newFormulaName
                        return newFormulaName
                else:
                    # save a newFile with the same name but + "(1)"
                    newFormulaName = fileName + " (1)"
                    # TODO: check to see if that save file already exists:
                    # if it does, increment up until you can find a file name that hasn't been used yet
                    self.saveFormula(newFormulaName, "", ttr)
                    ttr.name = newFormulaName
                    return newFormulaName
            else:
                # save a newFile with the same name but + "(1)"
                newFormulaName = fileName + " (1)"
                # TODO: check to see if that save file already exists:
                # if it does, increment up until you can find a file name that hasn't been used yet
                self.saveFormula(newFormulaName, "", ttr)
                ttr.name = newFormulaName
                return newFormulaName
        else:
            # save file without destroying the previous one
            self.saveFormula(fileName, "", ttr)
            ttr.name = fileName
            return fileName
