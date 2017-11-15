# -*- coding: utf-8 -*-

#import string
import sys

# factor px to mm
fc = 25.4/90

# drop spacing (default 40 um)
dropSpacing = 0.04

def main():
    if len(sys.argv) < 2:
        print 'input file name needed'
        return
    else:
        fname = sys.argv[1]
        if len(sys.argv) > 2:
            dropSpacing = float(sys.argv[2]) * 1e-3
            print 'Drop spacing is set to %s um'%sys.argv[2]
        else:
            print 'python converttoDimatix.py [file to convert] [drop spacing in um]'
            print 'Drop spacing is set to %g um'%dropSpacing*1e3

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
    #if num < 0:
    #    num = abs(num)
    return round(num, 2)

def getXYWH(f):
    squares = []
    ignore = True
    layermode = False
    xywh = [None, None, None, None]
    keys = ['x', 'y', 'width', 'height']
    for l in f:
        if ignore == True:
            if l.find('<g') > 1:
                ignore = False
                layermode = True
            pass
        else:
            # each layer into different files
            if layermode == True:
                if l.find("label=") > 1:
                    layername = l.split('"')[-2]
                    squares.append([layername])
                    layermode = False
            elif l.find("<g") > -1:
                layermode = True
            # when one parameter is defined, check if all 4 parameters are completed
            for key in keys:
                if l.find(' '+key+'=') > 1:
                    xywh[keys.index(key)] = extractNumber(l, key)
            if xywh.count(None) == 0:
                # check negative coordniate
                if xywh[0] < 0:
                    xywh[0] = -1 * xywh[0] - xywh[2]
                if xywh[1] < 0:
                    xywh[1] = -1 * xywh[1] - xywh[3]
                # drop count -1 for width and height
                xywh[2] = xywh[2]-dropSpacing if xywh[2]>dropSpacing else 0.02
                xywh[3] = xywh[3]-dropSpacing if xywh[3]>dropSpacing else 0.02
                squares[-1].append(xywh)
                xywh = [None, None, None, None]
    return squares

def writeXYWH(fname, sq):
    # define globaloffset (smallest offset among layers)
    xlst = []
    ylst = []
    for lyr in sq:
        xlst = xlst + [elm[0] for elm in lyr[1:]]
        ylst = ylst + [elm[1] for elm in lyr[1:]]
    globaloffsetx = min(xlst)
    globaloffsety = min(ylst)

    for lyr in sq:
        layername = lyr[0]
        # calculate pattern area. patternstartx and patternstarty are layer local offset
        patternstartx = min([elm[0] for elm in lyr[1:]])
        patternstarty = min([elm[1] for elm in lyr[1:]])
        endx = max([elm[0]+elm[2] for elm in lyr[1:]])
        endy = max([elm[1]+elm[3] for elm in lyr[1:]])
        # calculate pattern width and height
        patternw = endx - patternstartx
        patternh = endy - patternstarty
        localoffsetx = patternstartx - globaloffsetx
        localoffsety = patternstarty - globaloffsety
    
        # set output file name
        fwrite = fname.split('.')[-2] + "_" + layername + '.ptn'
        f = open(fwrite, 'w')
    
        # write header
        f.write("""<?xml version="1.0"?>

<!--Standalone Deposition Materials Printer Pattern File. To be converted into .ptn -->
<!--Created by converttoDimatix https://github.com/ikuehirata/Image-converter-for-Dimatix-->

<PatternFile>

<GeneralConfig>

    <Left>%f</Left>
    <Top>%f</Top>
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
    <JetSpacing>%s</JetSpacing>
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
<MaxYCount>1</MaxYCount>
""" % (localoffsetx, localoffsety, patternw, patternh,
       dropSpacing,
       patternw, patternh))
    
        # write each block
        for elm in lyr[1:]:
            f.write("""    <Drop>
        <StartX>%f</StartX>
        <StartY>%f</StartY>
        <XWidth>%f</XWidth>
        <YHeight>%f</YHeight>
    </Drop>
""" % (elm[0]-patternstartx, elm[1]-patternstarty, elm[2], elm[3]))

        # write close tags
        f.write("""
</PatternBlock>

</PatternFile>
""")
        f.close()

main()
