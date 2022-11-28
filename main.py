import csv
import random
from MOGBHS import MOGBHS
from Individual import Individual
from ObjectiveFunction import ObjectiveFunction
from Input import Input

SITEPACKAGES = "C:\\Python27\\Lib\\site-packages"
sys.path.append(SITEPACKAGES)
import pandas as pd
import numpy as np

def readConfig():

    df = pd.read_csv("C:\\Users\\ahmadiam\\Desktop\\Config.csv", header=None, names=range(2))
    table_names = ["Configuration", "Parameters range"]
    groups = df[0].isin(table_names).cumsum()
    tables = {g.iloc[0, 0]: g.iloc[1:] for k, g in df.groupby(groups)}

    sum = 0
    for k, v in tables.items():
        print("table:", k)
        sum += 1
        print(v)
        for i in range(sum, len(v[1]) + sum):
            print(v[1][i])
        sum += len(v[1])


def main(argv):
    
    readConfig()
    
    function = ObjectiveFunction()
    function.setOpc(0)
    range = np.array([[0.5, 2], [0.7, 3], [0.7, 3], [2.5, 3.5], [1, 1.4], [40, 60], [4, 7], [0.5, 2]])
    alg = MOGBHS(function, 10, 5, len(range), 0.5, 0.2, 0.8, range, argv)
    ind = alg.run();

if __name__ == "__main__":

    sys.exit(main(sys.argv))

