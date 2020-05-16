"""

Process raw Twitter API response
- apply minimal cleaning
- separate tweets from retweets and quotes
- save select columns to 


USAGE:
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-15 --end 2020-03-22 \
    --tweetf tweets.0315-0321.csv.gz --retweetf retweets.0315-0321.csv.gz --quotef quotes.0315-0321.csv.gz
"""
from joblib import Parallel, delayed
import gzip, os, json
from parsers import Tweet, Retweet, QuoteTweet
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tqdm import tqdm

parser = ArgumentParser("ProcessTweets", formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve') #'2020-03'
parser.add_argument("--dir", help="Data directory.", required=True)
parser.add_argument("--start", help="start date (inclusive)", required=True) #2020-03-15
parser.add_argument("--end", help="end date (excusive)", required=True)# 2020-03-22

parser.add_argument("--njobs", default=1, type=int, help="num parallel jobs", required=False)# 2020-03-22

parser.add_argument("--tweetf", default='tweets.csv.gz', help="output file for tweets")
parser.add_argument("--retweetf", default='retweets.csv.gz', help="output file for tweets")
parser.add_argument("--quotef", default='quotes.csv.gz', help="output file for tweets")

args = parser.parse_args()

# NOTE: Saves a corrupt file when njobs is >1
args.njobs = 1

def process(fpath):
    tweets = []
    retweets = []
    quotes = []

    with gzip.open(fpath, 'rt', encoding='utf-8') as f:
        
        for line in f:        
            data = json.loads(line.strip())
            if data['lang']=='en':
                if 'retweeted_status' in data:
                    retweets.append(Retweet(data))
                # elif 'quoted_status_id' in data:
                #     quotes.append(QuoteTweet(data))
                # else:
                #     tweets.append(Tweet(data))

    # if len(tweets) > 0:
    #     with gzip.open(args.tweetf, 'a') as f:
    #         for tweet in tweets:
    #             f.write(tweet.to_csv().encode('utf8') + b"\n")

    if len(retweets) > 0:
        with gzip.open(args.retweetf, 'a') as f:
            for retweet in retweets:
                f.write(retweet.to_csv().encode('utf8') + b"\n")

    # if len(quotes) > 0:
    #     with gzip.open(args.quotef, 'a') as f:
    #         for quote in quotes:
    #             f.write(quote.to_csv().encode('utf8') + b"\n")

def main():

    data_dir = args.dir
    start = 'coronavirus-tweet-id-{}'.format(args.start)
    end = 'coronavirus-tweet-id-{}'.format(args.end)

    # with gzip.open(args.tweetf, 'w') as f:
    #     f.write(','.join(Tweet.column_names).encode('utf8') + b"\n")

    with gzip.open(args.retweetf, 'w') as f:
        f.write(','.join(Retweet.column_names).encode('utf8') + b"\n")

    # with gzip.open(args.quotef, 'w') as f:
    #     f.write(','.join(QuoteTweet.column_names).encode('utf8') + b"\n")


    files_to_parse = []
    for fname in os.listdir(data_dir):
        if (fname.endswith('gz') and fname >= start and fname < end):
            files_to_parse.append(os.path.join(data_dir, fname))

    print("{} files to parse".format(len(files_to_parse)))
    for fpath in tqdm(files_to_parse):
        process(fpath)

    # Parallel(n_jobs=args.njobs)(delayed(process)(fpath) for fpath in tqdm(files_to_parse))

if __name__=='__main__':
    main()



