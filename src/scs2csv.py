from sys import argv
import pandas as pd
from numpy import array_split
from re import split
from datetime import datetime

args=argv[1:]
df = pd.read_csv(args[0],delimiter='\t',lineterminator='\n')
df=df.drop(df.columns[0], axis=1)
df=df.drop_duplicates()
df['Due Date']= pd.to_datetime(df['Due Date'].astype(str),errors='coerce',exact=False)
#df['Due Date']= pd.to_datetime(df['Due Date'].astype(str),errors='coerce',format='%m/%d/%Y')
df['Post Date']= pd.to_datetime(df['Post Date'].astype(str),errors='coerce',exact=False)
#df['Post Date']= pd.to_datetime(df['Post Date'].astype(str),errors='coerce',format='%m/%d/%Y')
print(df)

for idx, chunk in enumerate(array_split(df,max(10*len(df)/int(args[1]),1))):
    i=str(idx).zfill(3)
    chunk.to_csv(f'{args[0][:-4]}_S{i}',index=False)
