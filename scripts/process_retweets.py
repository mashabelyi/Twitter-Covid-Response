"""
Process retweet file

Save two outputs
nodes.tsv - one line per user account + number of times this account was retweeted
edges.tsv - sourceAccountId | targetAccountId | numTimesTargetRetweetedSource

"""
from joblib import Parallel, delayed
import gzip, os, json
from collections import Counter
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tqdm import tqdm

parser = ArgumentParser("ProcessTweets", formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve') #'2020-03'
parser.add_argument("--dir", help="Data directory.", required=True)
parser.add_argument("--start", help="start date (inclusive)", required=True) #2020-03-15
parser.add_argument("--end", help="end date (excusive)", required=True)# 2020-03-22

parser.add_argument("--nodes", default='retweets.nodes.csv.gz', help="output file for nodes")
parser.add_argument("--edges", default='retweets.edges.csv.gz', help="output file for edges")

parser.add_argument("--njobs", default=1, type=int, help="num parallel jobs", required=False)



args = parser.parse_args()

# NOTE: Saves a corrupt file when njobs is >1
# args.njobs = 1-


def process(fpath):

    nodes = Counter() # userId: # times userId was retweeted
    edges = Counter() # dictionary of (source A, target B): # times B retweeted A
    accounts = {}

    with gzip.open(fpath, 'rt', encoding='utf-8') as f:
        
        for line in f:        
            data = json.loads(line.strip())
            if data['lang']=='en':
                if 'retweeted_status' in data:
                    source_id = data['retweeted_status']['user']['id_str']
                    target_id = data['user']['id_str']

                    source_name = data['retweeted_status']['user']['screen_name']
                    target_name = data['user']['screen_name']

                    nodes[source_id] += 1
                    nodes[target_id] += 1
                    edges[(source_id, target_id)] += 1

                    accounts[source_id] = source_name
                    accounts[target_id] = target_name



    return nodes, edges, accounts
                
def main():

    data_dir = args.dir
    start = 'coronavirus-tweet-id-{}'.format(args.start)
    end = 'coronavirus-tweet-id-{}'.format(args.end)


    if args.dir:
        files_to_parse = []
        for fname in os.listdir(data_dir):
            if (fname.endswith('gz') and fname >= start and fname < end):
                files_to_parse.append(os.path.join(data_dir, fname))
    elif args.fin:
        files_to_parse = [args.fin]

    print("{} files to parse".format(len(files_to_parse)))

    nodes = Counter() # userId: # times userId was retweeted
    edges = Counter() # dictionary of (source A, target B): # times B retweeted A
    accounts = {} # map of userId: screenName
    
    result = Parallel(n_jobs=args.njobs)(delayed(process)(fpath) for fpath in tqdm(files_to_parse))
    for n, e, acc in result:
        nodes.update(n)
        edges.update(e)
        accounts.update(acc)


    # for fpath in tqdm(files_to_parse):
    #     n, e, acc = process(fpath)

    #     nodes.update(n)
    #     edges.update(e)
    #     accounts.update(acc)

    print("{} nodes, {} edges".format(len(nodes), len(edges)))

    # write to file
    with gzip.open(args.nodes, 'w') as f:
        f.write('userId,screenName,numRetweets'.encode('utf8') + b"\n")
        for id, num in nodes.most_common():
            f.write('{},{},{}'.format(id, accounts[id], num).encode('utf8') + b"\n")

    with gzip.open(args.edges, 'w') as f:
        f.write('source,target,weight'.encode('utf8') + b"\n")
        for (source, target), num in edges.most_common():
            f.write('{},{},{}'.format(source, target, num).encode('utf8') + b"\n")
        

    # Parallel(n_jobs=args.njobs)(delayed(process)(fpath) for fpath in tqdm(files_to_parse))

if __name__=='__main__':
    main()