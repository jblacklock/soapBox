import soap
from soap import testTube
from soap import testTubeRack
from soap import rackMaker

testCreator = rackMaker()
ttr = testCreator.createTestTubeRack("counterCleaner")
stuff= ttr.formula()
print(*stuff, sep='\n')
ttr2 = testCreator.createTestTubeRack("windowCleaner")
stuff2= ttr2.formula()
print(*stuff2, sep='\n')
