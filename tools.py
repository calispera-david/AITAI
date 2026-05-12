import pandas as pd 
import numpy as np
import math

train = pd.read_csv("train.csv")

def get_data():
    """get information from data file"""
    rowNr = len(train["PassengerId"])
    answer = [str(rowNr)," rows \n"]
    for col in train.columns:
        answer.append(col)
        answer.append(" : ")
        answer.append("count=")
        answer.append(str(rowNr - train[col].isnull().sum()))
        answer.append(" type=")
        answer.append(str(train[col].dtype))
        answer.append(" EXAMPLE VALUES: ")
        answer.append(str(train[col].unique()[:5]))
        answer.append("\n")
    answer.append(str(train.describe()))
    txt = "".join(answer)
    
    return txt


