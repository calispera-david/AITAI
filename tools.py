import pandas as pd 
import numpy as np
import math
from xgboost import XGBClassifier

train = pd.read_csv("train.csv")
test = pd.read_csv("test.csv")
target_col = pd.Series()

def get_data_train():
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

def get_data_test():
    """get information from data file"""
    rowNr = len(test["PassengerId"])
    answer = [str(rowNr)," rows \n"]
    for col in test.columns:
        answer.append(col)
        answer.append(" : ")
        answer.append("count=")
        answer.append(str(rowNr - test[col].isnull().sum()))
        answer.append(" type=")
        answer.append(str(test[col].dtype))
        answer.append(" EXAMPLE VALUES: ")
        answer.append(str(test[col].unique()[:5]))
        answer.append("\n")
    answer.append(str(test.describe()))
    txt = "".join(answer)
    
    return txt

def set_target_col(col):
    """remembers the target column to use in training the model (does not drop the column in the dataframe)"""
    global target_col, train
    target_col = train[col]

def drop_cols_train(columns):
    """drop the columns listed in the array passed as the parameter columns from the train dataframe"""
    global train
    train.drop(columns = columns, inplace = True)

def drop_cols_test(columns):
    """drop the columns listed in the array passed as the parameter columns from the test dataframe"""
    global test
    test.drop(columns = columns, inplace = True)


def show_user():
    """shows user info regarding the dataset, should be used at the end of the message"""
    train.info()
    test.info()
