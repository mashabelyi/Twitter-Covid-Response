#!/bin/bash

# MARCH
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-01 --end 2020-03-08 --tweetf tweets.0301-0307.csv.gz --retweetf retweets.0301-0307.csv.gz --quotef quotes.0301-0307.csv.gz
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-08 --end 2020-03-15 --tweetf tweets.0308-0314.csv.gz --retweetf retweets.0308-0314.csv.gz --quotef quotes.0308-0314.csv.gz
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-15 --end 2020-03-22 --tweetf tweets.0315-0321.csv.gz --retweetf retweets.0315-0321.csv.gz --quotef quotes.0315-0321.csv.gz
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-22 --end 2020-03-32 --tweetf tweets.0322-0331.csv.gz --retweetf retweets.0322-0331.csv.gz --quotef quotes.0322-0331.csv.gz

