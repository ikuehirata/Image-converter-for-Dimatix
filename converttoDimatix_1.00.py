# -*- coding: utf-8 -*-

#import string
import sys

def main():
        if len(sys.argv) < 2:
                print 'input file name needed'
                return
        else:
                fname = sys.argv[1]

        # file type definition
        if not fname.split('.')[-1] == 'svg':
                print 'This file is not supported.'
                return

        # x, y, w, h extraction
        f = open(fname, 'r')
        sq = getXYWH(f)
        f.close()

        # write to .ptn
        writeXYWH(fname, sq)

def appendXYWH(l, x, y, w, h):
        if x and y and w and h:
                l.append([x, y, w, h])
                return None, None, None, None
        else:
                return x, y, w, h
        
def getXYWH(f):
        squares = []
        ignore = True
        x, y, w, h = None, None, None, None
        for l in f:
                if ignore == True:
                        if l.find('<rect') > 1:
                                ignore = False
                        pass
                else:
                        # when one parameter is defined, check if all 4 parameters are completed
                        if l.find(' width="') > 1:
                                w = float(l.strip().split('"')[-2])
                                x, y, w, h = appendXYWH(squares, x, y, w, h)
                        elif l.find(' height="') > 1:
                                h = float(l.strip().split('"')[-2])
                                x, y, w, h = appendXYWH(squares, x, y, w, h)
                        elif l.find(' x="') > 1:
                                x = float(l.strip().split('"')[-2])
                                x, y, w, h = appendXYWH(squares, x, y, w, h)
                        elif l.find(' y="') > 1:
                                y = float(l.strip().split('"')[-2])
                                x, y, w, h = appendXYWH(squares, x, y, w, h)
        return squares

def writeXYWH(fname, sq):
        # calculate pattern area. startx and starty are offset
        startx = min([elm[0] for elm in sq])
        starty = min([elm[1] for elm in sq])
        endx = max([elm[0]+elm[2] for elm in sq])
        endy = max([elm[1]+elm[3] for elm in sq])
        # calculate pattern width and height
        patw = endx - startx
        path = endy - starty

        # set output file name
        fwrite = fname.split('.')[-2] + '.ptn'
        f = open(fwrite, 'w')

        # write header
        f.write("""<?xml version="1.0"?>

<!--Standalone Deposition Materials Printer Pattern File. To be converted into .ptn -->

<PatternFile>

<GeneralConfig>

	<Left>0</Left>
	<Top>0</Top>
	<Width>%f</Width>
	<Height>%f</Height>
	<UseReferenceCoordinates>False</UseReferenceCoordinates>
	<XReference>0</XReference>
	<YReference>0</YReference>
	<XReferenceTile>0</XReferenceTile>
	<YReferenceTile>0</YReferenceTile>
	<UseLeaderBar>False</UseLeaderBar>
	<LeaderBarWidth>0</LeaderBarWidth>
	<LeaderBarGap>0</LeaderBarGap>
	<JetSpacing>40</JetSpacing>
	<LayerCount>1</LayerCount>
	<LayerDelayInSeconds>0</LayerDelayInSeconds>

</GeneralConfig>

<PatternBlock>

<Left>0</Left>
<Top>0</Top>
<Width>%f</Width>
<Height>%f</Height>
<XSpacing>0</XSpacing>
<YSpacing>0</YSpacing>
<MaxXCount>1</MaxXCount>
<MaxYCount>1</MaxYCount>""" % (patw, path, patw, path))
        
        # write each block
        for elm in sq:
                f.write("""	<Drop>
		<StartX>%f</StartX>
		<StartY>%f</StartY>
		<XWidth>%f</XWidth>
		<YHeight>%f</YHeight>
	</Drop>
""" % (elm[0]-startx, elm[1]-starty, elm[2], elm[3]))

        # write close tags
        f.write("""
</PatternBlock>

</PatternFile>""")
        f.close()

main()
