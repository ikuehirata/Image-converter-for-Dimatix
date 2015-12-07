# -*- coding: utf-8 -*-

#import string
import sys

# factor px to mm
fc = 25.4/90

def main():
        if len(sys.argv) < 2:
                print 'input file name needed'
                return
        else:
                for fname in sys.argv[1:]:
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

def extractNumber(l, key):
        strl = l.replace('"', ' ').split()
        ind = strl.index(key+'=')
        num = float(strl[ind+1])*fc
        return num
        
def getXYWH(f):
        squares = []
        ignore = True
        x, y, w, h = None, None, None, None
        xywh = [None, None, None, None]
        keys = ['x', 'y', 'width', 'height']
        for l in f:
                if ignore == True:
                        if l.find('rect') > 1 or l.find('svg:rect') > 1:
                                ignore = False
                        else:
                                continue
                        
                # when one parameter is defined, check if all 4 parameters are completed
                for key in keys:
                        if l.find(' '+key+'=') > 1:
                                xywh[keys.index(key)] = extractNumber(l, key)
                if xywh.count(None) == 0:
                        # drop count -1 for width and height
                        xywh[2] = xywh[2]-0.04 if xywh[2]>0.04 else 0.02
                        xywh[3] = xywh[3]-0.04 if xywh[3]>0.04 else 0.02
                        squares.append(xywh)
                        xywh = [None, None, None, None]
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
