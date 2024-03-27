"""
This script is used to run the Dr. Grants Proposal Test-O-Meter, which analyzes and summarizes Call for Proposals (CFP) or Funding Opportunity Announcement (FOA) descriptions.

The script takes command-line arguments to customize the analysis and output. It uses the `proposal_meter` module to perform the analysis and generate the results.

Command-line Arguments:
    - `-p, --prompt`: Description of the work you want to do (default: 'CLI')
    - `-k, --k`: Number of matches to return (default: -1)
    - `-a, --active`: Restrict search to CFPs that have not expired (default: False)
    - `-o, --output`: CSV file to store output
    - `-t, --title`: Title for results if multiple queries (default: 'CLI prompt')
    - `-i, --interactive`: Allows user to explore/summarize results by hand (default: False)
    - `-s, --summary`: Prints AI-generated summary of CFP/FOA descriptions (default: False)

Usage:
    python main.py [-p PROMPT] [-k K] [-a] [-o OUTPUT] [-t TITLE] [-i] [-s]

Example:
    python main.py -p "Research on climate change" -k 5 -a -o results.csv -t "Climate Change Research" -i -s
"""
import faulthandler
from argparse import ArgumentParser
from warnings import filterwarnings
from src import proposal_meter

IDIR = './index'
EMBEDDINGS = f'{IDIR}'+'/embeddings.pkl'
TARGET = {'NSF': 'Synopsis',
          'SCS': 'Brief Description',
          'SAM': 'Description',
          'GRANTS': 'Description',
          'GFORWARD': 'Description',
          'CMU': 'Summary',
          'PIVOT': 'Abstract',
          'EXTERNAL': 'Description'
          }


if __name__ == "__main__":
    faulthandler.enable()
    filterwarnings('ignore')
    p = ArgumentParser()
    p.add_argument('-p', '--prompt', default='CLI',
                   help='Description of the work you want to do')
    p.add_argument('-k', '--k', default=-1, type=int,
                   help='Number of matches to return')
    p.add_argument('-a', '--active', default=False, action='store_true',
                   help='Restrict search to CFPs that have not expired.')
    p.add_argument('-o', '--output',
                   help='CSV file to store output')
    p.add_argument('-t', '--title', default='CLI prompt',
                   help='Title for results if multiple queries')
    p.add_argument('-s', '--summary', default=False, action='store_true',
                   help='Prints AI-generated summary of CFP/FOA descriptions')
    args = p.parse_args()

    proposal_meter.show_flags(args.k,
                              args.prompt,
                              args.active,
                              args.output,
                              args.title
                              )

    experiment = proposal_meter.Experiment(args.prompt, EMBEDDINGS, args.k)
    experiment.run()
    results = experiment.select_results(range(10*args.k),args.active)
    results.drop_duplicates(subset=['Title'],
                            keep='first',
                            inplace=True,
                            ignore_index=True
                            )
    if not args.output:
        proposal_meter.results2console(results.iloc[:args.k],args.summary)
    else:
        proposal_meter.results2csv(results.iloc[:args.k], args.output, args.prompt, args.title)


    #if args.output:
        #csv_output['Prompt']=prompt
        #csv_output['QueryName']=args.title
        #csv_output['Eligibility']='See URL'
        #csv_output['ApplicantLocation']='See URL'
        #csv_output['ActivityLocation']='See URL'
        #csv_output['SubmissionDetails']='See URL'
        #csv_output.to_csv(args.output,index=False, mode='a', header=not exists(args.output))

    #menu_option = 'help'
    #if args.interactive:
        #while menu_option != 'quit':
            #if menu_option == 'help':
                #print('Options: summarize, display, description, help, quit')
            #if menu_option == 'summarize':
                #neighbor = int(input('kth neighbor= '))
                #proposal_meter.summarize(ds, nearest_neighbors, neighbor)
            #if menu_option == 'display':
                #neighbor = int(input('kth neighbor= '))
                #print(neighbor, type(neighbor))
                #proposal_meter.display(ds, nearest_neighbors, neighbor)
            #if menu_option == 'description':
                #neighbor = int(input('kth neighbor= '))
                #proposal_meter.description(ds, nearest_neighbors, neighbor)
            #menu_option = str(input('Next command: '))
