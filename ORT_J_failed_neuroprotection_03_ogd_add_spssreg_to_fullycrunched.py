# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 21:13:40 2019

@author: Jonas
"""

import os
import numpy as np
import pandas as pd


#inputdirectory =
#outputdirectory =

#inputfile =

df = pd.read_excel(inputfile)

Regimes = np.sort(df["Regime"].unique())

def addspssreg(df):
    for i in range(0, len(Regimes)+1):
        df.loc[(df.Regime ==i) & (df.Time ==1), "spssreg"] = ((i*2)-1)
        df.loc[(df.Regime ==i) & (df.Time ==2), "spssreg"] = (i*2)

addspssreg(df)
