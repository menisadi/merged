import os
import pathlib
import sys

import matplotlib.pyplot as plt
import pandas as pd
from hard_rules import version_serializtion as verser
from lnds import longest_non_decreasing_subsequence as lnds

# print(pathlib.Path().resolve())
# print("ok?")
# sys.path.append(os.path.abspath("../modules"))

df = pd.read_csv("./modules/bug_in_lnds.csv")
vs = verser(df).to_list()
x, y = lnds(vs)
print()

plt.scatter(df.iloc[y]["time"], x, c="g")
