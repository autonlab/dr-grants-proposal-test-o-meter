'''
/\\\\\\\\\\\\__________________________/\\\\\\\\\\\\__________________________________________________________/\\\\________________
\/\\\////////\\\______________________/\\\//////////__________________________________________________________\///\\_______________
_\/\\\______\//\\\____________________/\\\___________________________________________________________/\\\_______/\\/_______________
__\/\\\_______\/\\\__/\\/\\\\\\\______\/\\\____/\\\\\\\__/\\/\\\\\\\___/\\\\\\\\\_____/\\/\\\\\\___/\\\\\\\\\\\_\//_/\\\\\\\\\\____
___\/\\\_______\/\\\_\/\\\/////\\\_____\/\\\___\/////\\\_\/\\\/////\\\_\////////\\\___\/\\\////\\\_\////\\\////_____\/\\\//////____
____\/\\\_______\/\\\_\/\\\___\///______\/\\\_______\/\\\_\/\\\___\///____/\\\\\\\\\\__\/\\\__\//\\\___\/\\\_________\/\\\\\\\\\\__
_____\/\\\_______/\\\__\/\\\_____________\/\\\_______\/\\\_\/\\\__________/\\\/////\\\__\/\\\___\/\\\___\/\\\_/\\_____\////////\\\_
______\/\\\\\\\\\\\\/___\/\\\___/\\\______\//\\\\\\\\\\\\/__\/\\\_________\//\\\\\\\\/\\_\/\\\___\/\\\___\//\\\\\_______/\\\\\\\\\\
_______\////////////_____\///___\///________\////////////____\///___________\////////\//__\///____\///_____\/////_______\//////////

 /$$$$$$$                                                             /$$      /$$      /$$             /$$                        
| $$__  $$                                                           | $$     | $$$    /$$$            | $$                        
| $$  \ $$ /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$ | $$     | $$$$  /$$$$  /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$ 
| $$$$$$$//$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$_____/ |____  $$| $$     | $$ $$/$$ $$ /$$__  $$|_  $$_/   /$$__  $$ /$$__  $$
| $$____/| $$  \__/| $$  \ $$| $$  \ $$| $$  \ $$|  $$$$$$   /$$$$$$$| $$     | $$  $$$| $$| $$$$$$$$  | $$    | $$$$$$$$| $$  \__/
| $$     | $$      | $$  | $$| $$  | $$| $$  | $$ \____  $$ /$$__  $$| $$     | $$\  $ | $$| $$_____/  | $$ /$$| $$_____/| $$      
| $$     | $$      |  $$$$$$/| $$$$$$$/|  $$$$$$/ /$$$$$$$/|  $$$$$$$| $$     | $$ \/  | $$|  $$$$$$$  |  $$$$/|  $$$$$$$| $$      
|__/     |__/       \______/ | $$____/  \______/ |_______/  \_______/|__/     |__/     |__/ \_______/   \___/   \_______/|__/      
                             | $$                                                                                                  
                             | $$                                                                                                  
                             |__/                                                                                                  
'''
from glob import glob
from os.path import exists
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import faulthandler
from argparse import ArgumentParser
from warnings import filterwarnings
from os import system
from datetime import datetime, timedelta
from numpy import isnan
from dateutil.parser import parse
from src import proposal_meter
import subprocess
# bart-large-cnn
from transformers import pipeline

IDIR='./index'

def display( ds, sorted_ds, i):
    fn = ds.loc[sorted_ds.index[i]].filename
    row = ds.loc[sorted_ds.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval('proposal_meter.'+source)
    raw_data = funcname(fn,target[source])
    raw_data.print(row,sorted_ds.iloc[i].similarity)

def description( ds, sorted_ds, i):
    fn = ds.loc[sorted_ds.index[i]].filename
    row = ds.loc[sorted_ds.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval('proposal_meter.'+source)
    raw_data = funcname(fn,target[source])
    proposal_meter.show_one_limitless(i,raw_data.df.loc[row].Description)


def summarize( ds, sorted_ds, i ):
    if not exists('summarizer.model'):
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summarizer.save_pretrained('summarizer.model')
    else:
        summarizer = pipeline("summarization", model='summarizer.model')
    fn = ds.loc[sorted_ds.index[i]].filename
    row = ds.loc[sorted_ds.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval('proposal_meter.'+source)
    raw_data = funcname(fn,target[source])
    attname = raw_data.description_attribute
    line=raw_data.to_dict(row,sorted_ds.loc[i].similarity)
    summary = summarizer(line['Description'], max_length=280, min_length=140, do_sample=False)[0]['summary_text']
    proposal_meter.show_one_limitless(f'{line["Title"]} Summary',summary)#ds.loc[sorted_ds.index[i]].Description)

def encode_prompt( prompt ):
    model = SentenceTransformer('all-mpnet-base-v2')
    return model.encode([prompt])

def read_narrative_embeddings( filename:str ):
    return pd.read_pickle(filename)

def sort_by_similarity_to_prompt( prompt, embedded_narratives, k):
    embedded_prompt = encode_prompt(prompt)
    similarity = [_[0] for _ in cosine_similarity(embedded_narratives.iloc[:,3:],embedded_prompt.reshape(1,-1))]
    result = pd.DataFrame({'similarity':similarity},index=embedded_narratives.index)
    result.sort_values('similarity',inplace=True,ascending=False)
    return result

def human_readable_dollars( num:float ):
    for unit in ('', 'K', 'M', 'B'):
        if abs(num)<1024.0:
            return f'{num:3.1f}{unit}'
        num/=1024.0
    return f'{num:.1f}T'

if __name__ == "__main__":
    '''
    Parse arguments, read data, run experiment
    '''
    print('\n\n')
    proposal_meter.show_color_banner_no_score("Dr. Grant's Proposal Test-O-Meter!",0.99)
    proposal_meter.show_one('How attractive is your idea to potential sponsors?',"Let's find out!")
    rgb = [240,245,250,255,46,33,92,226,202,199]
    prizes=['poor fish, try again!','clammy','harmless','mild','naughty, but nice','Wild','Burning!','Passionate!!','Hot Stuff!!!','UNCONTROLLABLE!!!!']
    for i in reversed(range(len(prizes))):
        subprocess.run(["echo", "-e", '\e[38;5;%dmCosine Similarity in [%.1f,%.1f)\e[0m -- %s'%(rgb[i],i/len(prizes),(i+1)/len(prizes),prizes[i])])
    embeddingFN= f'{IDIR}/embeddings.pkl'
    faulthandler.enable()
    filterwarnings('ignore')
    p = ArgumentParser()
    p.add_argument('-p', '--prompt', default='CLI',
                   help='Description of the work you want to do')
    p.add_argument('-k', '--k', default=-1,
                   help='Number of matches to return')
    p.add_argument('-a', '--active', default=False, action='store_true',
                   help='Restrict search to CFPs that have not expired.')
    p.add_argument('-r', '--recent', default=-1,
                   help='Restrict search to CFPs in the last r years')
    p.add_argument('-o', '--output',
                   help='CSV file to store output')
    p.add_argument('-s', '--subset', default='*_S*',
                   help='Glob pattern to match specific records in data folder')
    p.add_argument('-t', '--title', default='CLI prompt',
                   help='Title for results if multiple queries')
    p.add_argument('-i', '--interactive', default=False, action='store_true',
                   help='Allows user to explore/summarize results by hand')
    args = p.parse_args()

    if not torch.cuda.is_available():
        print('Torch is not enabled.')
    k = int(args.k)
    r = int(args.recent)
    prompt = args.prompt
    ds = read_narrative_embeddings(embeddingFN)
    print(f'Searching {len(ds)} opportunities')

    sorted_ds = sort_by_similarity_to_prompt(prompt,ds,k)
    target={'NSF':'Synopsis','SCS':'Brief Description','SAM':'Description','GRANTS':'Description','GFORWARD':'Description','CMU':'Summary','PIVOT':'Abstract','EXTERNAL':'Description'}

    print('\033[38;5;84m\nPROMPT: \033[0m%s\n'%prompt)
    csv_output=None
    j=0
    titles=[]

    for i in sorted_ds.index:
        #if j>=k:
            #break
        fn = ds.loc[i].filename
        row = ds.loc[i].row
        source=fn.split('/')[-1].split('_')[0]
        funcname=eval('proposal_meter.'+source)
        raw_data = funcname(fn,target[source])
        line=raw_data.to_dict(row,sorted_ds.loc[i].similarity)
        if line['Similarity']<.45 and j>=k or j>8: break
        if line['Title'] in titles or any([line['Title'][:len(line['Title'])*3//4] in t for t in titles]):
            continue
        if args.active:
            try:
                if not datetime.strptime(line['CloseDate'],'%m/%d/%Y')<datetime.now():
                    j+=1
                    titles.append(line['Title'] )
                else:
                    titles.append('[Closed] '+line['Title'] )
                    continue
            except:
                if not 'CMU' in line['Feed']:
                    titles.append('[Closed] '+line['Title'] )
                    continue
                j+=1
                titles.append(line['Title'] )
        else:
            j+=1
            titles.append(line['Title'])
        if args.output:
            raw_data.print_title(row,sorted_ds.loc[i].similarity)
            if csv_output is None:
                csv_output=raw_data.to_csv(row,sorted_ds.loc[i].similarity)
            else:
                res=raw_data.to_csv(row,sorted_ds.loc[i].similarity).iloc[0]
                try:
                    res['DueDates']=str(res['DueDates'])
                except:
                    res['DueDates']='None on posting'
                csv_output.loc[len(csv_output)]=res
        else:
            #summary = summarizer(sorted_ds.loc[i], max_length=280, min_length=140, do_sample=False)
            #raw_data.print(row,sorted_ds.loc[i].similarity,summarizer)
            raw_data.print(row,sorted_ds.loc[i].similarity)

    #****** for fun
    print('******* Bottom 3 *******')
    for opp in sorted_ds[-3:].index:
        fn = ds.loc[opp].filename
        row=ds.loc[opp].row
        source=fn.split('/')[-1].split('_')[0]
        funcname=eval('proposal_meter.'+source)
        raw_data = funcname(fn,target[source])
        line=raw_data.to_dict(row,sorted_ds.loc[opp].similarity)
        titles.append(line['Title'])
        raw_data.print_title(row,sorted_ds.loc[opp].similarity)
    #******
    if args.output:
        csv_output['Prompt']=prompt
        csv_output['QueryName']=args.title
        csv_output['Eligibility']='See URL'
        csv_output['ApplicantLocation']='See URL'
        csv_output['ActivityLocation']='See URL'
        csv_output['SubmissionDetails']='See URL'
        csv_output.to_csv(args.output,index=False, mode='a', header=not exists(args.output))

    usercmd='help'
    if args.interactive:
        while usercmd!='quit':
            if usercmd=='help':
                print('Menu Options: summarize, display, description, help, quit')
            if usercmd=='summarize':
                neighbor=int(input('kth neighbor= '))
                summarize(ds,sorted_ds,neighbor)
            if usercmd=='display':
                neighbor=int(input('kth neighbor= '))
                print(neighbor,type(neighbor))
                display(ds,sorted_ds,neighbor)
            if usercmd=='description':
                neighbor=int(input('kth neighbor= '))
                description(ds,sorted_ds,neighbor)
            usercmd=str(input('Next command: '))
