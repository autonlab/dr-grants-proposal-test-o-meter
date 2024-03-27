import textwrap
from typing import List
from os.path import exists
from sys import argv
from os import system, environ
import subprocess
from glob import glob
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from argparse import ArgumentParser
from datetime import datetime
from math import isnan
from transformers import pipeline
from src import data as DATA


environ["TOKENIZERS_PARALLELISM"]="false" #parallel GPU encoding makes subprocess run statement throw warning over parllelism
N_TIERS=11
PRIZES_RGB = [240,245,250,255,46,33,92,226,202,199]
PRINTMAXCHARS=80
PRINTMAXLINES=12
TARGET = {'NSF': 'Synopsis',
            'SCS': 'Brief Description',
            'SAM': 'Description',
            'GRANTS': 'Description',
            'GFORWARD': 'Description',
            'CMU': 'Summary',
            'PIVOT': 'Abstract',
            'EXTERNAL': 'Description'
            }
DRGRANT = 'all-mpnet-base-v2'
DRGIST = 'facebook/bart-large-cnn'


def results2console(results:pd.DataFrame,print_summary=False):
    show_testometer_banner()
    show_prizes()
    print(f'\n*** Dr. Grant\'s ({DRGRANT}) top {len(results)} picks and Dr. Gist\'s ({DRGIST}) summaries ***')
    for i in range(len(results)):
        x = results.iloc[i]
        show_prize_banner(f'{x.Title}',x.Similarity)
        show_one('URL',x['URL'])
        if print_summary:
            description = summarize(x['Description'])
            show_one('AI Summary',description)
        else:
            description = x['Description']
            show_one('FOA Description', description, limit=True)
        

def results2csv(results: pd.DataFrame, output_fn: str, prompt: str, qname: str):
    show_testometer_banner()
    show_prizes()
    print(f'\n*** Dr. Grant\'s ({DRGRANT}) top {len(results)} picks ***')
    #print(f'\n*** Top {len(results)} nearest neighbors according to {DRGRANT} ***')
    for i in range(len(results)):
        x = results.iloc[i]
        show_prize_banner(f'{x.Title}', x.Similarity, show_score=True, limit=False)
    results['Prompt'] = prompt
    results['QueryName'] = qname
    results['Eligibility'] = 'See URL'
    results['ApplicantLocation'] = 'See URL'
    results['ActivityLocation'] = 'See URL'
    results['SubmissionDetails'] = 'See URL'
    results.to_csv(output_fn, index=False, header=results.columns)


def summarize(text: str):
    if not exists('summarizer.model'):
        summarizer = pipeline("summarization", model=DRGIST)
        summarizer.save_pretrained('summarizer.model')
    else:
        summarizer = pipeline("summarization", model='summarizer.model')
    if len(text.split(' '))>=256:
        t = ' '.join(text.split(' ')[:256])
        return summarizer(t,max_length=t.count(' ')//2,min_length=t.count(' ')//3)[0]['summary_text']
    else:
        return summarizer(text,max_length=text.count(' ')//2,min_length=text.count(' ')//3)[0]['summary_text']


def show_prize_banner(message: str, prize: float, show_score=False, limit=True):
    header = f'[{prize:0.4f}] '
    color = PRIZES_RGB[int(prize*100)//N_TIERS]

    clean_val1 = message.replace("'", "\'").replace("\n", " -- ")
    if limit:
        text = '\n'.join(textwrap.wrap(header+clean_val1, PRINTMAXCHARS, break_long_words=True))
    else:
        text = header+clean_val1
    if show_score:
        print(f'\033[1;38;5;{color}m{header} {text[len(header)-1:]}\033[0m')
    else:
        print(f'\033[1;38;5;{color}m{text[len(header):]}\033[0m')


def show_one(key1: str, val1: str, limit=False):
    """Print a formatted key-value pair to the console

    Args:
        key1 (str): Bolded text for the key
        val1 (str): Grey text for the value
        limit (bool): Whether to limit the number of lines printed
    """
    header = f'{key1}: '
    clean_val1 = val1.replace("'", "\'").replace("\n", " -- ")
    if limit:
        text = '\n'.join(textwrap.wrap(header+clean_val1, PRINTMAXCHARS, break_long_words=True, max_lines=PRINTMAXLINES))
    else:
        text = '\n'.join(textwrap.wrap(header+clean_val1, PRINTMAXCHARS, break_long_words=True))
    print(f'\033[1m{key1}:\033[0m\033[38;5;8m{text[len(header)-1:]}\033[0m')


def description( ds, nearest_neighbors, i):
    #raw_data = read_raw_data(ds, nearest_neighbors, i)
    fn = ds.loc[nearest_neighbors.index[i]].filename
    row = ds.loc[nearest_neighbors.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval(source)
    raw_data = funcname(fn,TARGET[source])
    show_one(i,raw_data.df.loc[row].Description)



def encode_prompt( prompt ):
    model = SentenceTransformer(DRGRANT)
    return model.encode([prompt])


def read_narrative_embeddings( filename:str ):
    return pd.read_pickle(filename)


def sort_by_similarity_to_prompt( prompt, embedded_narratives, k):
    embedded_prompt = encode_prompt(prompt)
    similarity = [_[0] for _ in cosine_similarity(embedded_narratives.iloc[:,4:],embedded_prompt.reshape(1,-1))]
    result = pd.DataFrame({'similarity':similarity},index=embedded_narratives.index)
    result.sort_values('similarity',inplace=True,ascending=False)
    return result


def human_readable_dollars(num: float):
    """Convert a number of dollars to a human-readable string

    Args:
        num (float): Number of dollars

    Returns:
        str: Human-readable string e.g. '1.2M'
    """
    for unit in ('', 'K', 'M', 'B'):
        if abs(num) < 1024.0:
            return f'{num:3.1f}{unit}'
        num /= 1024.0
    return f'{num:.1f}T'


def show_prizes():
    """Show a color-coded tier list for the Proposal Test-O-Meter

    Args:
        None: Uses hard-coded values for prizes and colors

    Returns:
        None: Prints to console
    """
    prizes = ['poor fish, try again!', 'clammy', 'harmless', 'mild',
              'naughty,  but nice', 'Wild', 'Burning!', 'Passionate!!',
              'Hot Stuff!!!', 'UNCONTROLLABLE!!!!']
    for pidx in reversed(range(len(prizes))):
        color = PRIZES_RGB[pidx]
        low_lim = pidx/len(prizes)
        hi_lim = (pidx+1)/len(prizes)
        pname = prizes[pidx]
        metric = f'Cosine Similarity in [{low_lim:.1f},{hi_lim:.1f})'
        print(f' - \033[38;5;{color}m{metric}\033[0m -- {pname}')


def show_testometer_banner():
    """Show a color banner for the Proposal Test-O-Meter

    Args:
        None

    Returns:
        None: Prints to console
    """
    print()
    show_prize_banner(
        "Dr. Grant's Proposal Test-O-Meter!",
        0.99
    )
    show_one(
        'How attractive is your idea to potential sponsors?',
        "Let's find out!"
    )


def show_prompt(prompt: str):
    """Show the prompt supplied for the Proposal Test-O-Meter

    Args:
        prompt (str): The prompt supplied by the user

    Returns:
        None: Prints to console
    """
    print(f'Prompt: {prompt}')


def show_flags(k: int, prompt: str, active: bool, output: str, title: str):
    """Show the flags supplied for the Proposal Test-O-Meter

    Args:
        k (int): Number of matches to return
        active (bool): Restrict search to CFPs/FOAs that have not expired
        output (str): CSV file to store output
        title (str): Title for results if multiple queries
    """

    print(f'\033[38;5;84m\nSPECIFICATION: \033[0m')
    print(f'Search for {k} most cosine-similar funding opportunity descriptions based on the "{title}" prompt:')
    show_prompt(prompt)
    if active:
        print(' - Restricting search to opportunities that have not expired')
    if output:
        print(f' - Results will be saved to {output}')


def show_data_stats(ds):
    """Show statistics about the data

    Args:
        ds (pd.DataFrame): The data

    Returns:
        None: Prints to console
    """
    print(f' - Searching {len(ds)} opportunities:')
    feeds = []
    for source in ds.filename.unique():
        feed = source.split('_')[0].split('/')[-1]
        if feed not in feeds:
            feeds.append(feed)
    for feed in feeds:
        print(f'   -- {feed}: {len(ds[ds.filename.str.contains(feed)])} opportunities')
    print(' - \033[38;5;202mData Sources Last Updated: 03/25/2024\033[0m')


class Experiment():
    def __init__(self, prompt:str, embeddingsFN:str, k:int):
        self.prompt = prompt
        self.embeddingsFN = embeddingsFN
        self.k = k
        self.active = False
    def run(self):
        self.embeddings = read_narrative_embeddings(self.embeddingsFN)
        show_data_stats(self.embeddings)
        self.nearest_neighbors = sort_by_similarity_to_prompt(self.prompt,self.embeddings,self.k)

    def select_results(self, neighbors, active=False):
        df = pd.DataFrame([self.read_neighbor(i) for i in neighbors])
        df['CloseDate'] = pd.to_datetime(df['CloseDate'])
        if active:
            df.dropna(subset=['CloseDate'],inplace=True)
            df = df[~(df['CloseDate'] < datetime.now())]
        return df

    def read_neighbor(self, i):
        x=self.embeddings.loc[self.nearest_neighbors.index[i]]
        return getattr(DATA,x.source)(x.filename,TARGET[x.source]).to_dict(x.row,self.nearest_neighbors.iloc[i].similarity)