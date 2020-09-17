# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 09:32:41 2017

@author: Jonas
"""

import os
from os import path
import glob
from PIL import Image, ImageEnhance
import sys
from sys import argv

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def print_usage():
    eprint("Usage: python imagepype.py <input_directory>")

def main():
    """
    Expects and Input directory that contains .tif images.
    Creates an output-folder within that directory.
    Creates two Lists:
    One with all names of the directory, one to collect all histoarrays for the images.

    Opens each image in the directory and splits the channels.
    Then calls the functions getHistogram with and saveWithIncreasedSaturation.
    Finaly calls the dumpHistoArray function
    """
    if (len(argv)==2):
        indir=argv[1]
        if (path.exists(indir)):
            outdir=path.join(indir, "output")
            fileList=glob.glob(indir+"/*.tif")
            print(fileList)
            namelist=[]
            histoarray=[]
            if not path.exists(outdir):
                os.makedirs(outdir)

            for filename in fileList:
                base=path.basename(filename)
                name=path.splitext(base)[0]
                namelist.append(name)

                with Image.open(filename) as img:
                    red, green, blue = img.split()
                    histo=getHistogram(red)
                    histoarray.append(histo)
                    output_imagename=path.join(outdir, name+"_enhanced.tif")
                    saveWithIncreasedSaturation(red, output_imagename)

            output_histoarray=path.join(outdir,"completehistolist.csv")
            dumpHistoArray(output_histoarray,histoarray,namelist)
        else:
            eprint("Input directory "+indir+" does not exist")
    else:
        print_usage()

def getHistogram(img):
    histogram=img.histogram()
    return histogram

def saveWithIncreasedSaturation(img, outputname):
    enhancer=ImageEnhance.Contrast(img)
    factor=2
    image_enh=enhancer.enhance(factor)
    image_enh.save(outputname)


def dumpHistoArray(outputfile,histoarray,namelist):
    with open(outputfile,"w") as file:
        for filename in namelist:
            file.write(filename+",")
        file.write("\n")
        for i in range(0,256):
            for array in histoarray:
                count = str(array[i])
                file.write(count+",")
            file.write("\n")

if __name__=="__main__":
    main()
