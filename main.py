from os.path import exists
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faulthandler
from argparse import ArgumentParser
from warnings import filterwarnings
from datetime import datetime
from src import proposal_meter
from transformers import pipeline


IDIR = './index'
EMBEDDINGS=f'{IDIR}'+'/embeddings.pkl'
TARGET = {'NSF': 'Synopsis',
            'SCS': 'Brief Description',
            'SAM': 'Description',
            'GRANTS': 'Description',
            'GFORWARD': 'Description',
            'CMU': 'Summary',
            'PIVOT': 'Abstract',
            'EXTERNAL': 'Description'
            }


def display( ds, nearest_neighbors, i):
    #raw_data = read_raw_data(ds, nearest_neighbors, i)
    fn = ds.loc[nearest_neighbors.index[i]].filename
    row = ds.loc[nearest_neighbors.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval('proposal_meter.'+source)
    raw_data = funcname(fn,TARGET[source])
    raw_data.print(row,nearest_neighbors.iloc[i].similarity)


def description( ds, nearest_neighbors, i):
    #raw_data = read_raw_data(ds, nearest_neighbors, i)
    fn = ds.loc[nearest_neighbors.index[i]].filename
    row = ds.loc[nearest_neighbors.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval('proposal_meter.'+source)
    raw_data = funcname(fn,TARGET[source])
    proposal_meter.show_one_limitless(i,raw_data.df.loc[row].Description)


def summarize( ds, nearest_neighbors, i ):
    if not exists('summarizer.model'):
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summarizer.save_pretrained('summarizer.model')
    else:
        summarizer = pipeline("summarization", model='summarizer.model')
    #line = get_neighbor(ds, nearest_neighbors, i)
    fn = ds.loc[nearest_neighbors.index[i]].filename
    row = ds.loc[nearest_neighbors.index[i]].row
    source=fn.split('/')[-1].split('_')[0]
    funcname=eval('proposal_meter.'+source)
    raw_data = funcname(fn,TARGET[source])
    attname = raw_data.description_attribute
    line=raw_data.to_dict(row,nearest_neighbors.loc[i].similarity)
    summary = summarizer(line['Description'], max_length=280, min_length=140, do_sample=False)[0]['summary_text']
    proposal_meter.show_one_limitless(f'{line["Title"]} Summary',summary)#ds.loc[nearest_neighbors.index[i]].Description)


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
    rgb = [240, 245, 250, 255, 46, 33, 92, 226, 202, 199]
    for pidx in reversed(range(len(prizes))):
        color = rgb[pidx]
        low_lim = pidx/len(prizes)
        hi_lim = (pidx+1)/len(prizes)
        pname = prizes[pidx]
        metric = f'Cosine Similarity in [{low_lim:.1f},{hi_lim:.1f})'
        print(f' - \033[38;5;{color}m{metric}\033[0m -- {pname}')


def show_banner():
    """Show a color banner for the Proposal Test-O-Meter

    Args:
        None

    Returns:
        None: Prints to console
    """
    proposal_meter.show_color_banner_no_score(
        "Dr. Grant's Proposal Test-O-Meter!",
        0.99
    )
    proposal_meter.show_one(
        'How attractive is your idea to potential sponsors?',
        "Let's find out!"
    )


def show_prompt( prompt:str ):
    """Show the prompt supplied for the Proposal Test-O-Meter

    Args:
        prompt (str): The prompt supplied by the user

    Returns:
        None: Prints to console
    """
    print(f' - Prompt: {prompt}')


def show_flags(k: int, prompt: str, active: bool, output: str, title: str, interactive: bool):
    """Show the flags supplied for the Proposal Test-O-Meter

    Args:
        k (int): Number of matches to return
        active (bool): Restrict search to CFPs/FOAs that have not expired
        output (str): CSV file to store output
        title (str): Title for results if multiple queries
        interactive (bool): Allows user to explore/summarize results by hand
    """

    print(f'\033[38;5;84m\nSPECIFICATION: \033[0m')
    print(f'Search for {k} most cosine-similar funding opportunity descriptions based on the "{title}" prompt:')
    show_prompt(prompt)
    if active:
        print(' - Restricting search to opportunities that have not expired')
    if interactive:
        print(' - Interactive mode enabled')
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


def read_raw_data( ds, nearest_neighbors, i):
    fn = ds.loc[i].filename
    source = fn.split('/')[-1].split('_')[0]
    funcname = eval('proposal_meter.' + source)
    raw_data = funcname(fn, TARGET[source])
    return raw_data

def get_neighbor( ds, nearest_neighbors, i):
    raw_data = read_raw_data(ds, nearest_neighbors, i)
    row = ds.loc[i].row
    line = raw_data.to_dict(row, nearest_neighbors.loc[i].similarity)
    return line


if __name__ == "__main__":
    
    faulthandler.enable()
    filterwarnings('ignore')
    p = ArgumentParser()
    p.add_argument('-p', '--prompt', default='CLI',
                   help='Description of the work you want to do')
    p.add_argument('-k', '--k', default=-1,
                   help='Number of matches to return')
    p.add_argument('-a', '--active', default=False, action='store_true',
                   help='Restrict search to CFPs that have not expired.')
    p.add_argument('-o', '--output',
                   help='CSV file to store output')
    p.add_argument('-t', '--title', default='CLI prompt',
                   help='Title for results if multiple queries')
    p.add_argument('-i', '--interactive', default=False, action='store_true',
                   help='Allows user to explore/summarize results by hand')
    
    args = p.parse_args()
    k = int(args.k)
    prompt = args.prompt
    ds = read_narrative_embeddings(EMBEDDINGS)

    show_flags(k, prompt, args.active,
               args.output, args.title, args.interactive)
    show_data_stats(ds)
    print()

    nearest_neighbors = sort_by_similarity_to_prompt(prompt, ds, k)

    csv_output = None
    j = 0
    titles = []

    show_banner()
    show_prizes()
    print(f'******* Top {k} *******')
    for i in nearest_neighbors.index:
        #raw_data = read_raw_data(ds, nearest_neighbors, i)
        #line = get_neighbor(ds, nearest_neighbors, i)
        fn = ds.loc[i].filename
        row = ds.loc[i].row
        source = fn.split('/')[-1].split('_')[0]
        funcname = eval('proposal_meter.'+source)
        raw_data = funcname(fn,TARGET[source])
        line = raw_data.to_dict(row,nearest_neighbors.loc[i].similarity)
        if line['Similarity'] < .45 and j >= k or j > 8: break
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
            raw_data.print_title(row,nearest_neighbors.loc[i].similarity)
            if csv_output is None:
                csv_output = raw_data.to_csv(row, nearest_neighbors.loc[i].similarity)
            else:
                res = raw_data.to_csv(row, nearest_neighbors.loc[i].similarity).iloc[0]
                try:
                    res['DueDates']=str(res['DueDates'])
                except:
                    res['DueDates']='None on posting'
                csv_output.loc[len(csv_output)]=res
        else:
            raw_data.print_title(row,nearest_neighbors.loc[i].similarity)
            #raw_data.print(row,nearest_neighbors.loc[i].similarity)

    #****** for fun
    print('******* Bottom 3 *******')
    for opp in nearest_neighbors[-3:].index:
        fn = ds.loc[opp].filename
        row = ds.loc[opp].row
        source = fn.split('/')[-1].split('_')[0]
        funcname = eval('proposal_meter.' + source)
        raw_data = funcname(fn, TARGET[source])
        line = raw_data.to_dict(row, abs(nearest_neighbors.loc[opp].similarity))
        titles.append(line['Title'])
        raw_data.print_title(row, abs(nearest_neighbors.loc[opp].similarity))
    #******
    if args.output:
        csv_output['Prompt']=prompt
        csv_output['QueryName']=args.title
        csv_output['Eligibility']='See URL'
        csv_output['ApplicantLocation']='See URL'
        csv_output['ActivityLocation']='See URL'
        csv_output['SubmissionDetails']='See URL'
        csv_output.to_csv(args.output,index=False, mode='a', header=not exists(args.output))

    menu_option = 'help'
    if args.interactive:
        while menu_option != 'quit':
            if menu_option == 'help':
                print('Options: summarize, display, description, help, quit')
            if menu_option == 'summarize':
                neighbor = int(input('kth neighbor= '))
                summarize(ds, nearest_neighbors, neighbor)
            if menu_option == 'display':
                neighbor = int(input('kth neighbor= '))
                print(neighbor, type(neighbor))
                display(ds, nearest_neighbors, neighbor)
            if menu_option == 'description':
                neighbor = int(input('kth neighbor= '))
                description(ds, nearest_neighbors, neighbor)
            menu_option = str(input('Next command: '))
