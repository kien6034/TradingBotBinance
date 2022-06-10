import pandas as pd 



sr = pd.Series([0, 1, 2, 5])


print(sr.rolling(2).sum())