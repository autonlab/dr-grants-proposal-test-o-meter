from sys import argv
import pandas as pd
from numpy import array_split
from re import split

args=argv[1:]
data = open(args[0],'r')
data_lines = data.readlines()

all_records={}
curr_record={}
i=0
for line in data_lines:
    if line.startswith('*** '):
        curr_attr=line.split(':')[0][4:].strip()
        curr_record[curr_attr]=''
        continue
    elif line.startswith('\n'):
        continue
    elif line.startswith('==='):
        all_records[i]={key:val.strip() for key,val in curr_record.items()}
        curr_record={}
        i+=1
    else:
        curr_record[curr_attr]+=line.strip()

df=pd.DataFrame.from_dict(all_records,orient='index')
#print(df)
#print(df.columns)
df=df.drop_duplicates()
#cdf=df
cdf=pd.DataFrame(columns=df.columns)
for idx in df.index:# <- increases hits with GFORWARD which i am testing downweighting
    description=df.loc[idx].Description
    if isinstance(description,float):
        continue
    for c in split(r'\*\*.*\*\*',description):
        if c.strip():
            row=df.loc[idx]
            row['Description']=c
            cdf.loc[len(cdf)]=row
#print('GFORWARD',cdf)
#print(df)

for idx, chunk in enumerate(array_split(cdf,10*len(cdf)/int(args[1]))):
    i=str(idx).zfill(3)
    chunk.to_csv(f'{args[0][:-4]}_S{i}',index=False)
