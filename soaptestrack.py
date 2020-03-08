import soap

from soap import testTube
from soap import testTubeRack
#######################################
# Initiate four object racks to test; two all purpose cleaners, lavender dish soap, and a liquid laundry detergent
apc1 = testTubeRack("windowCleaner", 5.0)
apc2 = testTubeRack("counterCleaner", 10.0)
dish1 = testTubeRack("lavenderDishSoap", 100.0)
lld1 = testTubeRack("magLilLaundry", 50.0)

tube1 = testTube(100,7020,"Citric Acid",0.13, 0.1)
assert tube1.rawMaterialNumber == "7020"
#######################################
# Test__repr__

assert str(apc1) == "windowCleaner"
assert str(apc2) == "counterCleaner"

#######################################
# Test def formula

assert apc1.formula() == [["windowCleaner", 5.0]]
assert apc2.formula() == [["counterCleaner", 10.0]]

#######################################
# Test def changePricePoint

assert lld1.changePricePoint(1000) == True
assert lld1.changePricePoint(-10) == False
assert lld1.changePricePoint(0) == True
assert lld1.changePricePoint(50) == True

########################################
# Test def createRackTube

assert apc1.createRackTube(1015, "glucopon", 1.0, 10) == True
assert apc2.createRackTube(1015, "glucopon", 1.0, 10) == True
assert dish1.createRackTube(1015, "glucopon", 1.0, 10) == True
assert lld1.createRackTube(1015, "glucopon", 1.0, 10) == True

assert apc1.createRackTube(9001, "fragrance", 20, 0.1) == True
assert apc2.createRackTube(9001, "fragrance", 30, 0.1) == True
assert dish1.createRackTube(9001, "fragrance", 60, 0.1) == True
assert lld1.createRackTube(9001, "fragrance", 100, 0.1) == True

assert apc1.createRackTube(6035, "preservative", 20, 1) == True
assert apc2.createRackTube(6035, "preservative", 30, 1) == True
assert dish1.createRackTube(6035, "preservative", 60, 1) == True
assert lld1.createRackTube(6035, "preservative", 100, 1) == True

assert apc1.createRackTube(3022, "chelater", 5, 2.5) == True
assert apc2.createRackTube(3022, "chelater", 5, 5) == True
assert dish1.createRackTube(3022, "chelater", 5, 7.5) == True
assert lld1.createRackTube(3022, "chelater", 5, 10) == True

############################################
# Test getCost
print("CostTesting")
print(apc1.getCost())
print(apc2.getCost())
print(dish1.getCost())
print(lld1.getCost())
assert apc1.getCost() == 0.445
assert dish1.getCost() == 1.135
assert lld1.getCost() == 1.7

#############################################
# Test sumRackConcentration

assert apc1.sumRackConcentration() == 13.6
assert apc2.sumRackConcentration() == 16.1
assert dish1.sumRackConcentration() == 18.6
assert lld1.sumRackConcentration() == 21.1

#############################################
# Test unusedRackConcentration

assert apc1.unusedRackConcentration() == 100 - 13.6
assert apc2.unusedRackConcentration() == 100 - 16.1
assert dish1.unusedRackConcentration() == 100 - 18.6
assert lld1.unusedRackConcentration() == 100 - 21.1
#############################################
# Test fillToPrice

print("fillToPriceTesting Part1")
print(apc1.unusedRackConcentration())
print(apc1.sumRackConcentration())
print(apc1.getCost())
print(apc1.formula())
assert apc1.fillToPrice(["glucopon", "fragrance", "preservative"]) == None
print("fillToPriceTesting Part2")
print(apc1.unusedRackConcentration())
print(apc1.sumRackConcentration())
print(apc1.getCost())
print(apc1.formula())
#############################################
# Test reduceToPrice

print("testing reductToPrice")
assert apc1.changePricePoint(0.445) == True
print(apc1.formula())
assert apc1.reduceToPrice(["glucopon", "fragrance", "preservative"]) == None 
print(apc1.formula())
assert apc1.changePricePoint(5) == True
#############################################
# Test fillToConcentration

print("testing fill To Concentration")
assert apc1.fillToConcentration(["glucopon", "fragrance"]) == None
print(apc1.unusedRackConcentration())
print(apc1.sumRackConcentration())
print(apc1.getCost())
print(apc1.formula())
#############################################
# Test emptyTubes

print("testing emptyTubes")
assert apc1.emptyTubes(["glucopon", "fragrance"]) == None
print(apc1.unusedRackConcentration())
print(apc1.sumRackConcentration())
print(apc1.getCost())
print(apc1.formula())
#############################################
# Test increaseRackTubesByPrice

print("testing increaseRackTubesByPrice")
assert apc1.increaseRackTubeToPrice(["fragrance"], 2.5) == None
print(apc1.unusedRackConcentration())
print(apc1.sumRackConcentration())
print(apc1.getCost())
print(apc1.formula())
#############################################
# Test increaseRackTubeToConcentration

print("testing increaseRackTubeToConcentration")
assert apc1.increaseRackTubeToConcentration("glucopon", 4.625) == None
print(apc1.unusedRackConcentration())
print(apc1.formula())
print(apc1.getCost())
print("Glucopon cost")
print(apc1.testTubes[0].getCost())
# Check error/bound handeling
assert apc1.increaseRackTubeToConcentration("glucopon", 80) == None
print(apc1.unusedRackConcentration()) 
print(apc1.formula())
print(apc1.getCost())
print("glucopon Cost")
print(apc1.testTubes[0].getCost())
#############################################
# Test decreaseRackTubeToPrice

assert apc1.decreaseRackTubeToPrice("glucopon", 0.04625) == None
print(apc1.formula())
assert apc1.decreaseRackTubeToPrice("glucopon", 0) == None
print(apc1.formula())
assert apc1.increaseRackTubeToPrice("glucopon", 0.04625) == None
print(apc1.formula())
#############################################
# Test decreaseRackTubeToConcentration

assert apc1.decreaseRackTubeToConcentration("glucopon", 0) == None
print(apc1.formula())
#############################################
# Test reduceSolventWhenFillToPricePoint

print("Testing SolventFillTo PricePoint")
apc1.createRackTube("0100", "water", 0, 0)
print(apc1.formula())
apc1.fillToConcentration(["water"])
print(apc1.formula())
apc1.emptyTubes(["fragrance", "preservative"])
print(apc1.formula())
apc1.increaseRackTubeToConcentration("preservative", 1)
print(apc1.formula())
apc1.changePricePoint(1.5)
apc1.reduceSolventWhenFillToPricePoint(["water"], ["glucopon", "fragrance"])
print(apc1.formula())
print(apc1.getCost())
print(len("help"))