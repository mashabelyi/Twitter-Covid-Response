# COVID-19 Twitter Vizualization
Code for Info 247 final project: Mitigating The COVID-19 Infodemic with Twitter analysis

## Data
We use the [COVID-18-TweetIDs](https://github.com/echen102/COVID-19-TweetIDs) dataset.

## Preprocessing

The `scripts` directory contains pre-processing scripts that we use to process and clean the data.

We hydrate the COVID-18-TweetIDs dataset and filter for english tweets (`lang:en`). We the extract the following fields from the raw [Twitter API response](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object):
- `id_str`
- `lang`
- `full_text`
- `coordinates`
- `place`
- `retweet_count`
- `favorite_count`
- `entities` (hashtags, user_mentions, symbols, urls)
- `user:id_str`
- `user:screen_name`
- `user:location`
- `created_at`

**Additional Fields**

We use the [Vader](http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf) sentiment analysis tool (optimized for social media) to extract sentiment from each tweet. We store it in a `sentiment` column.

**Dependencies**

- vaderSentiment (for sentiment detection)
- tqdm (progress bar)
- emoji (to extract emojis from tweets)

Insallation:
```
pip install tqdm, vaderSentiment, emoji --upgrade
```

**Usage**
To preprocess hydrated `.jsonl.gz` files, call `process_raw_tweets.py` with an input directory that contains the `.jsonl.gz` files. Also specify start (inclusive) and end (exclusive) dates to process.
```
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-01 --end 2020-03-08
```

