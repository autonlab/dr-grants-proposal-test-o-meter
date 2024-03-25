from sys import argv
import pandas as pd
from re import split

args=argv[1:]
data = open(args[0],'r')
data_lines = data.readlines()

all_records={}
curr_record={}
i=1
for line in data_lines:
    if line.strip().isdigit() and curr_record is not None:
        all_records[i]={key:val.strip() for key,val in curr_record.items()}
        curr_record={}
        i+=1#int(line.strip())
    elif line.startswith('\n'):
        continue
    elif not line.startswith(' '):
        curr_attr=line.split(':')[0]
        curr_record[curr_attr]=' '.join(line.split(':')[1:])
    else:
        curr_record[curr_attr]+=line


df=pd.DataFrame.from_dict(all_records,orient='index')

cdf=pd.DataFrame(columns=df.columns)
for idx in df.index:# <- increases hits with GFORWARD which i am testing downweighting
    description=df.loc[idx].Abstract
    if isinstance(description,float):
        continue
    for c in description.split('<br/>'):#tag for new paragraph?
        if c.strip():
            row=df.loc[idx]
            row['Abstract']=c
            cdf.loc[len(cdf)]=row
#print('PIVOT',cdf)

cdf.to_csv(f'{args[0][:-4]}.csv',index=False)
#for idx, chunk in enumerate(array_split(cdf,10*len(cdf)/int(args[1]))):
    #i=str(idx).zfill(3)
    #chunk.to_csv(f'{args[0][:-4]}_S{i}',index=False)




