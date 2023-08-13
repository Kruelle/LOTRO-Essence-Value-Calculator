import os
import xml.etree.ElementTree as ETree
import pandas as pd
import numpy as np
import argparse

#File path to the most recent Lotro-Companion xml items db
#Download from https://raw.githubusercontent.com/LotroCompanion/lotro-data/master/common/progressions.xml
curves_xml_fp = '/Users/brand/Desktop/Lotro Items Python Sandbox/stat_progressions.xml'

def parse_curves(fp = curves_xml_fp, ilvl_cutoff=549):
    #Parse with ETree, then convert to pandas dataframe
    
    #Read file, get root
    prstree = ETree.parse(fp)
    root = prstree.getroot()

    #Initialize Lists
    stat_curves = []
    stat_curve_idxs = []

    #Iterate thru xml trees
    for progression in root.iter('arrayProgression'):
        #parse array progressions
        #x: 1 -> 501, but standarize to <ilvl_cutoff> with Nones as needed to match linearInterpolationProgression possibilities
        identifier = progression.attrib.get('identifier')
        stat_curve_idxs.append(identifier)

        #Create an empty array of length <ilvl_cutoff> to fill in with available values
        ys = ilvl_cutoff*[None]

        #Iterate thru points to fill the ys array
        for point in progression.iter('point'):
            x = point.attrib.get('x')
            xmin = point.attrib.get('xMin')
            xmax = point.attrib.get('xMax')
            y = point.attrib.get('y')

            if x is not None:
                idx = int(x)-1
                ys[idx] = y
            else:
                for idx in range(int(xmin)-1, int(xmax)):
                    ys[idx] = y

        stat_curves.append(ys)

    for progression in root.iter('linearInterpolationProgression'):
        #parse array progressions
        #x: 1 -> 999, standarize to <ilvl_cutoff> with Nones as needed
        #x's can go to 999 (or higher?) but ignore anything >ilvl_cutoff
        identifier = progression.attrib.get('identifier')
        stat_curve_idxs.append(identifier)

        #Create an empty array of length 549 to fill in with available values
        ys_full = ilvl_cutoff*[None]
        #Initialize arrays for available x, y pairs
        xs = []
        ys = []

        #Iterate thru points to fill the ys array
        for point in progression.iter('point'):
            x = int(point.attrib.get('x'))
            y = float(point.attrib.get('y'))

            xs.append(x)
            ys.append(y)

        #Generate the stat curve from available xs, ys using linear interpolation
        for idx in range(len(xs)-1):
            #Get endpoints
            x0 = xs[idx]
            x1 = xs[idx+1]
            y0 = ys[idx]
            y1 = ys[idx+1]
            #If starting x > ilvl_cutoff, don't bother
            if x0 > ilvl_cutoff:
                continue

            #find interpolating function
            #y=mx+b --> m=(y2-y1)/(x2-x1), b=y1-m*x1
            m = (y1-y0)/(x1-x0)
            b = y0-m*x0
            assert(m*x1+b - y1 <= 1e-6) #Sanity check, within margin of error

            #limit x1 to be <= 549
            if x1 > ilvl_cutoff:
                x1 = ilvl_cutoff

            #Loop over every integer from x0 to x1
            for i in range(x0, x1+1): #Now we use the derived interpolation y_i = f(i) = m*i+b
                #This includes endpoints, f(x0) = y0 and f(x1) = y1
                #Remember idx in ys_full is xval-1
                ys_full[i-1] = m*i+b

        stat_curves.append(ys_full)

    #Convert data to dataframe
    statsDf = pd.DataFrame(np.array(stat_curves).transpose(), columns=stat_curve_idxs)
    
    #Index is 0->548, let's fix that to be 1->549 to match associated levels
    #Don't run this cell more than once or you'll end up making the index 2->550 etc
    statsDf.index+=1
    
    return statsDf
    
#Example call: Python stat_curve_parsing.py -f u35_progressions.xml -s u35_progressions.csv
def main(args):
    #Make sure xml file path exists
    if not os.path.isfile(args.stat_curves_fp):
        print(f"File '{args.stat_curves_fp}' does not exist.")
        return -1
    
    df = parse_curves(fp=args.stat_curves_fp, ilvl_cutoff=args.ilvl_cutoff)
    df.to_csv(args.save_fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse the stat curves .xml file and save as csv")
    parser.add_argument('--stat_curves_fp', '-f', type=str, help="File path to xml of stat curves (download from LotroCompanion)",required=True)
    parser.add_argument('--save_fp', '-s', type=str, help="Save path/name for csv (include .csv extension)", required=True)
    parser.add_argument('--ilvl_cutoff', '-i', type=int, help="Value of the maximum ilvls to calculate", required=False, default=549) 
    args = parser.parse_args()
    main(args)  