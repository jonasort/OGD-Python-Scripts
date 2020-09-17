# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 12:53:09 2018

@author: Lisa Liebenstund, Tamara Fechter, Jonas Ort
"""

import pandas as pd
df = pd.read_csv("completehistolist.csv")
df = df[100:]
added = df.sum()
finished = added.transpose()
finished.to_excel("masterlist.xlsx")