from sys import argv
import pandas as pd
from numpy import array_split
from re import split
from datetime import datetime

args=argv[1:]
df = pd.read_csv(args[0])
print(df)
df=df.drop_duplicates()
df.ArchiveDate = pd.to_datetime(df.ArchiveDate.astype(str),errors='coerce',format='%Y-%m-%d')
df=df.drop(df[(df['ArchiveDate']<datetime.now())].index)
print(df)

for idx, chunk in enumerate(array_split(df,len(df)/int(args[1]))):
    i=str(idx).zfill(3)
    chunk.to_csv(f'{args[0][:-4]}_S{i}',index=False)
