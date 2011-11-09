#!/usr/bin/python

'''
Updates overviewer.dat file sign info

This script will scan through every chunk looking for signs and write out an
updated overviewer.dat file.  This can be useful if your overviewer.dat file
is either out-of-date or non-existant.  

To run, simply give a path to your world directory and the path to your
output directory. For example:

    python contrib/findAnimals.py ../world.test/ output_dir/ 

An optional north direction may be specified as follows:
    
    python contrib/findAnimals.py ../world.test/ output_dir/ lower-right

Valid options are upper-left, upper-right, lower-left and lower-right.
If no direction is specified, lower-left is assumed

Once that is done, simply re-run the overviewer to generate markers.js:

    python overviewer.py ../world.test/ output_dir/

'''
import sys
import re
import os
import string
from array import array
import png
import cPickle

colours = [[0, 0, 0],          # 0  Not explored
            [0, 0, 0],         # 1  Not explored
            [0, 0, 0],         # 2  Not explored
            [0, 0, 0],         # 3  Not explored
            [89, 125, 39],     # 4  Grass
            [109, 153, 48],    # 5  Grass
            [127, 178, 56],    # 6  Grass
            [109, 153, 48],    # 7  Grass
            [174, 164, 115],   # 8  Sand/Gravel
            [213, 201, 140],   # 9  Sand/Gravel
            [247, 233, 163],   # 10 Sand/Gravel
            [213, 201, 140],   # 11 Sand/Gravel
            [117, 117, 117],   # 12 Other
            [144, 144, 144],   # 13 Other
            [167, 167, 167],   # 14 Other
            [144, 144, 144],   # 15 Other
            [180, 0, 0],       # 16 Lava
            [220, 0, 0],       # 17 Lava
            [255, 0, 0],       # 18 Lava
            [220, 0, 0],       # 19 Lava
            [112, 112, 180],   # 20 Ice
            [138, 138, 220],   # 21 Ice
            [160, 160, 255],   # 22 Ice
            [138, 138, 220],   # 23 Ice
            [117, 117, 117],   # 24 Other
            [144, 144, 144],   # 25 Other
            [167, 167, 167],   # 26 Other
            [144, 144, 144],   # 27 Other
            [0, 87, 0],        # 28 Leaves
            [0, 106, 0],       # 29 Leaves
            [0, 124, 0],       # 30 Leaves
            [0, 106, 0],       # 31 Leaves
            [180, 180, 180],   # 32 Snow
            [220, 220, 220],   # 33 Snow
            [255, 255, 255],   # 34 Snow
            [220, 220, 220],   # 35 Snow
            [115, 118, 129],   # 36 Clay
            [141, 144, 158],   # 37 Clay
            [164, 168, 184],   # 38 Clay
            [141, 144, 158],   # 39 Clay
            [129, 74, 33],     # 40 Dirt
            [157, 91, 40],     # 41 Dirt
            [183, 106, 47],    # 42 Dirt
            [157, 91, 40],     # 43 Dirt
            [79, 79, 79],      # 44 Smoothstone/Cobblestone/Ore
            [96, 96, 96],      # 45 Smoothstone/Cobblestone/Ore
            [112, 112, 112],   # 46 Smoothstone/Cobblestone/Ore
            [96, 96, 96],      # 47 Smoothstone/Cobblestone/Ore
            [45, 45, 180],     # 48 Water
            [55, 55, 220],     # 49 Water
            [64, 64, 255],     # 50 Water
            [55, 55, 220],     # 51 Water
            [73, 58, 35],      # 52 Log/Tree/Wood
            [89, 71, 43],      # 53 Log/Tree/Wood
            [104, 83, 50],     # 54 Log/Tree/Wood
            [89, 71, 43]]      # 55 Log/Tree/Wood

print colours[4]

# incantation to be able to import overviewer_core
if not hasattr(sys, "frozen"):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0], '..')))

from overviewer_core import nbt

from pprint import pprint
if len(sys.argv) < 3:
    sys.exit("Usage: %s <worlddir> <outputdir>" % sys.argv[0])
    
worlddir = sys.argv[1]
outputdir = sys.argv[2]

if not os.path.exists(worlddir):
    sys.exit("Bad WorldDir")

worlddir = os.path.join(worlddir, 'data/')
if os.path.exists(worlddir):
    print "Scanning for maps in ", worlddir
else:
    sys.exit("Bad WorldDir or no maps crafted")

if os.path.exists(outputdir):
    #print "Output directory is ", outputdir
    pass
else:
    sys.exit("Bad OutputDir")

mapoutputdir = os.path.join(outputdir, 'maps')
if not os.path.exists(mapoutputdir):
    os.mkdir(mapoutputdir)

matcher = re.compile(r"^map_(.*)\.dat$")

POI = []

for dirpath, dirnames, filenames in os.walk(worlddir):
    for f in filenames:
        if matcher.match(f):
            newPOI = None
            full = os.path.join(dirpath, f)
            # force lower-left so chunks are loaded in correct positions
            r = nbt.load(full)

            # heavily assume we are a *map*
            mapItem = r[1]['data']

            newFile = string.replace(f, 'dat', 'png', 1)
            output = os.path.join(mapoutputdir, newFile)

            mapWidth = mapItem['width']
            mapHeight = mapItem['height']
            data = array('b', mapItem['colors']).tolist()
            data = map(lambda x: colours[x+1], data)
            data = [item for sublist in data for item in sublist]
            data = map(lambda x: data[x*(mapHeight*3):(x+1)*(mapHeight*3)], range(0,(mapWidth)))            
            png.from_array(data, 'RGB', { 'width':mapWidth, 'height':mapHeight, 'transparent': colours[0] } ).save(output)

            # further assumptions; dimension = 0, scale = 3
            newPOI = dict(type="map",
                            x=mapItem['xCenter'], y=60, z=mapItem['zCenter'], msg=f, chunk=(mapItem['xCenter']/16, mapItem['zCenter']/16),)

            # now we have to write out the map as an image
            if newPOI is not None:
                print "Found map centred at (%d, %d)" % (newPOI['x'], newPOI['z'])
            

if os.path.isfile(os.path.join(worlddir, "overviewer.dat")):
    print "Overviewer.dat detected in WorldDir - this is no longer the correct location\n"
    print "You may wish to delete the old file. A new overviewer.dat will be created\n"
    print "Old file: ", os.path.join(worlddir, "overviewer.dat")

#pickleFile = os.path.join(outputdir,"overviewer.dat")
#with open(pickleFile,"wb") as f:
#    cPickle.dump(dict(POI=POI,north_direction=north_direction), f)

