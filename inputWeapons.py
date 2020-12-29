# -*- coding: utf-8 -*-

"""
inputWeapons.py provides the input functions for damage-calc.

*** Recent Changes: ***
2020-12-29: Translated comments to English
"""

import pandas as pd

def readInput(fileName, sheet):
    """
    Input function. Opens the given Excel file and imports the selected sheet
    as a whole into a pandas.DataFrame which can be further handled.
        
    Parameters
    ----------
    fileName : str
        Name of input file.
    sheet : int or str
        Sheet of input file. Accepts a sheet name (str) or a sheet index (int).

    Returns
    -------
    dfWeaponList : list
        two-dimensional list containing attacks which themselves contain weapon
        data.
    
    """
    
    # Read Weapon data from Excel file. header=None prevents pandas from assuming
    # a header line, which the input file does not have.
    dfWeapon = pd.read_excel(fileName, sheet_name=sheet, header=None)
    
    # The first row contains the attack names, they are separated here and
    # stored in a separate list
    attackNames = []
    attackRow = dfWeapon.iloc[0,:]
    for a in attackRow[~pd.isnull(attackRow)]:
        attackNames.append(str(a))
    
    dfWeaponList = readInputWeapons(dfWeapon.iloc[1:,:])
    
    return dfWeaponList, attackNames

def readInputWeapons(dfWeapon):
    """
    This function accepts a DataFrame from an Excel import and partitions it
    into attacks and weapons.
        
    Parameters
    ----------
    dfWeapon : pandas.DataFrame
        The input is a single DataFrame which 1:1 represents the input file.

    Returns
    -------
    dfWeaponList : list
        Two-dimensional list with attacks and weapons.
    
    """
    
    # The first column of the input file contains description text for the row
    # contents and is helpful for finding empty lines, which divide weapons
    # from each other.
    # The input is searched row-wise to find completely empty rows. The indices
    # of those rows are written to cutIndexHorizontal
    # An empty row contains only NaN entries, which means that isna() of this
    # row only contains True.
    cutIndexHorizontal = [-1]
    
    cutMap = dfWeapon.isna().values
    for i in range(dfWeapon.values.shape[0]):
        if not False in cutMap[i,:]:
            cutIndexHorizontal.append(i)
    
    # The first column is no longer needed after that and is removed.
    dfWeapon = dfWeapon.drop(labels=0, axis=1)
    
    # The attacks are separated by empty columns.
    # The process is exactly the same as the search for empty rows above.
    cutIndexVertical = [-1]

    # dfWeapon.isna() is searched for columns with only True-entries.
    cutMap = dfWeapon.isna().values
    for i in range(dfWeapon.values.shape[1]):
        if not False in cutMap[:,i]:
            cutIndexVertical.append(i)
    
    # dfWeapon is now separated along the empty columns to separate attacks from
    # each other. They are temporarily stored in dfAttackList, before they are
    # split along empty rows to separate weapons from each other.
    dfAttackList = []
    for index in range(1,len(cutIndexVertical)):
        dfAttackList.append(dfWeapon.iloc[:,cutIndexVertical[index-1]+1:cutIndexVertical[index]])
    
    dfAttackList.append(dfWeapon.iloc[:,cutIndexVertical[-1]+1:])

    # Horizontal splitting of the attacks and storing the resulting weapon
    # dataFrames in dfWeaponList, grouped by attack.
    # dfWeaponList looks like this: [[A1W1, A1W2], [A2W1], [A3W1, A3W2, A3W3]]
    dfWeaponList = []

    for a in range(len(dfAttackList)):
        dfWeaponList.append([])
        attack = dfAttackList[a]
        for index in range(1,len(cutIndexHorizontal)):
            subset = attack.iloc[cutIndexHorizontal[index-1]+1:cutIndexHorizontal[index],:]
            if False in subset.isna().values:
                dfWeaponList[a].append(subset)
        subset = attack.iloc[cutIndexHorizontal[-1]+1:,:]
        if False in subset.isna().values:
            dfWeaponList[a].append(subset)
        
    return dfWeaponList