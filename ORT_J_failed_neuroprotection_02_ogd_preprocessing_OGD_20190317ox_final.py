import os
import glob
import pathlib
import numpy as np
import pandas as pd


inputdirectory="C:/Users/Jonas/Documents/MEDIZIN/Doktorarbeit/Statistik/Statistikprozess/data"
#outputdirectory=
#inputfile=

def pipe(inputfile):
    """
    main function that calls other functions
    expects an .xlsx-file containing the following Columns:
    [CASE_LBL, Damage, Time, Trauma, Regime, oneslice, gyrusnonident, CA1nonident, darkspots, PIClot, wrinkling, margininhomogenous]
    """
    df = pd.read_excel(inputfile) # input file is read and stored in the variable df
    df = include(df) # calls include function
    maxpredamage = findmaxpredamage(df) # sets variable maxpredamage to the result of called function findmaxpredamage(df)
    df.loc[(df["Damage"] <= maxpredamage) & (df["Time"] == 1), "belowPredamage"] = 1 # sets "belowPredamage to 1 if "Damage" is below maxpredamage and Time == 1
    maxdamagelist = findmaxdamage(df) #calls the findmaxdamage(df)function and will set the variable maxdamagelist to a list of 20 maximum damages according to the Regimes
    df = setmaxdamage(df, maxdamagelist)
    indexlistpre = df[df["belowPredamage"] == 1].index #??? still needed ???
    df = slicecouples(df)  # calls slicecouples function --> every slice gets an ID
    df = includetostats(df) # calls the includetostatsfunction --> where into_stats == 1 is eligible for the statistic processing
    df.to_excel("fullycrunched_data.xlsx") # saves a fully processed dataframe ready for statistics
    #df_forstats = df[df["into_stats"] == 1]
    #df_forstats_grouped = df_forstats.groupby(["Regime", "Time"]) # both lines create a first impression of the included slices (mean, std, count)
    #output = df_forstats_grouped["Damage"].describe()
    #output = output.to_frame()
    #output.to_excel("Analyse_intostats_groupby-Regime-time.xlsx") # saves this first analysis to an .xlsx



def include(df):
    """
    expects: a dataframe consisting to the criteria described in def pipe(inputfile)
    does:
    it will drop completely empty lines and columns
    it will add an inclusion column (set to 0 initially)
    will set inclusion=1 for slices where oneslice, gyrusnonident, CA1nonident, darkspots, PIClot, wrinkling, margininhomogenous == 0
    will create to columns "belowPredamage" and "belowMaxdamage" and sets them to 0 initially
    """
    df_without_index = df.dropna(axis=0, how="all") # drops all empty indexes
    df_without_na = df_without_index.dropna(axis=1, how="all") #drops all empty columns
    zeros = np.zeros(len(df_without_na)) # creates an array of zeros according to lenght of the dataframe
    df_without_na["Inclusion"] = zeros # creates a column "Inclusion" and sets it to 0
    df = df_without_na
    df.loc[(df["oneslice"] == 0.0) & (df["gyrusnonident"] == 0.0) & (df["CA1nonident"] == 0.0) & (df["darkspots"] == 0.0) & (
        df["PIClot"] == 0.0) & (df["wrinkling"] == 0.0) & (df["margininhomogenous"] == 0.0), "Inclusion"] = 1
    # where all conditions are met, slices are regarded as included for further processing
    df["belowPredamage"]=0 # creates column belowPredamage
    df["belowMaxdamage"]=0 # creates column belowMaxdamage
    #df.to_excel("cleaned_inclusion-checked_"+inputfile)
    return df # returns df to pipe()-function

def findmaxpredamage(df):
    """
    :param df: uses the dataframe(df) that has been processed by def include()

    :return: the maximum value for that slices are not counted as predamaged (mean + std) for all included slices at T==1
    """
    #df = pd.read_excel("converted20171120.xlsx") #dfinc soll später in der obigen funktion der output sein
    dfinc = df[df["Inclusion"] == 1] # selects slices where "Inclusion" == 1
    dfincpre = dfinc[dfinc["Time"] == 1] # selects slices where "Time" == 1
    predamage = dfincpre["Damage"] # from the above filtered slices, collects the "Damage column"
    maxpredamage = predamage.mean() + predamage.std() # calculates the maxpredamage and returns it to pipe()-function
    return maxpredamage

def findmaxdamage(df):
    """

    :param df: takes in the dataframe df as processed in pipe() so far
    :return:
    """
    maxdamagelist = []
    maxmeanlist = []
    maxstdlist = []
    dfinc = df[df["Inclusion"] == 1]
    indexlist = df[df["belowPredamage"] == 1].index #creates a list with the index positions of all Time=1 slices with "belowPredamage"=1 --> thus, maxdamage is only calculated for the slices included so far!
    dfmaxdamage = df.iloc[indexlist + 1] #a df with the Time=2 slices according to Time=1 slices with "belowPredamage"=1
    dfmaxdamagegrouped = dfmaxdamage.groupby("Regime")
    maxstdlist.append(dfmaxdamagegrouped["Damage"].std()) #creates list of all std for each regime
    maxmeanlist.append(dfmaxdamagegrouped["Damage"].mean()) #creates list of all mean for each regime
    listsum = np.add(maxmeanlist, maxstdlist)  # creates array of mean+single std
    maxdamagelist = np.add(listsum, maxstdlist)  # creates array of mean+double std
    maxdamagelist = maxdamagelist.tolist() # creates list from array
    maxdamagelist = maxdamagelist[0]  # only takes in the first part
    return maxdamagelist

def setmaxdamage(df, maxdamagelist):
    dfinc = df[df["Inclusion"] == 1] #only takes in slices that are included so far
    indexlist = df[df["belowPredamage"] == 1].index  # creates a list with the index positions of all Time=1 slices with "belowPredamage"=1
    dfmaxdamage = df.iloc[indexlist + 1]  # a df with the Time=2 slices according to Time=1 slices with "belowPredamage"=1
    #dfmaxdamagegrouped = dfmaxdamage.groupby("Regime")
    for i in range(1, len(maxdamagelist)+1): # for all existing regimes there is an i
        df.loc[(df["Regime"] == i) & (df["Time"]==2) & (df["Damage"]<= maxdamagelist[i-1]), "belowMaxdamage"]=1 # if in the observed regime and time==2 and damage is below the maxdamagelist value for that regime, sets below maxDamage == 1
    return df  # returns the dataframe df with belowMaxdamagevalues ==1 for the observed slices if appropriate

def slicecouples(df):
    """
    :param df: takes the processed df
    :return: will give every slice-couple an couple - ID which are ints
    """
    numberofcouples = len(df)/2
    a = np.arange(0, numberofcouples, 1)
    b = a.tolist()
    a = b
    couplelist = [j for i in zip(a,b) for j in i] # merges list a and b, so the list will be [1, 1, 2, 2, 3, 3,...n, n]
    """
    check line below: df.loc --> df[]
    """
    df["couple"]=couplelist # adds the line couple to df, one slice at two times gets the couple - ID
    return df

def includetostats(df):
    for i in range(0, int(len(df)/2)):
        pre = df[(df["couple"] == i) & (df["Time"] == 1) ]["belowPredamage"]
        post = df[(df["couple"] == i) & (df["Time"] == 2)]["belowMaxdamage"]
        both = pre.sum() + post.sum()
        if both == 2:
            into1 = 0
            into2 = 0
            a = df.loc[(df["couple"] == i) & (df["Time"]==1)]["Inclusion"]
            b = df.loc[(df["couple"] == i) & (df["Time"]==2)]["Inclusion"]
            if int(a) ==1:
                into1 += 1
            if int(b) ==1:
                into2 += 1
            if (into1 == 1) & (into2 == 1):
                df.loc[(df["couple"] == i), "into_stats"]=1 # couple included to stats when belowPredamage and belowMaxdamage == 1, and Inclusion criteria are met
            else:
                df.loc[(df["couple"] == i), "into_stats"]=0 # otherwise couple will be excluded
        else:
            df.loc[(df["couple"] == i), "into_stats"]=0 # otherwise couple will be excluded
    return df



#pipe(inputfile)



#set = 1
#for i in range(1, 21):
#    df.loc[(df["Regime"]==i) & (df["Time"]==1), "spssreg"]=set
#    set+=1
#   df.loc[(df["Regime"]==i) & (df["Time"]==2), "spssreg"]=set
#    set+=1
