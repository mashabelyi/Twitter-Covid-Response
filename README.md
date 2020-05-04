# COVID-19 Twitter Visualization
Code for Info 247 final project: Mitigating The COVID-19 Infodemic with Twitter analysis

## Data
We use the [COVID-19-TweetIDs](https://github.com/echen102/COVID-19-TweetIDs) dataset.

## Preprocessing

The `scripts` directory contains pre-processing scripts that we use to process and clean the data.

We hydrate the COVID-19-TweetIDs dataset and filter for english tweets (`lang:en`). We then extract the following fields from the raw [Twitter API response](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object):
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

We use the `emoji` python library to extract emojis from each tweet and store them in a separate `emojis` column.

**Topic Clustering**

- Work in Progress...
- Empath library - frames


### Dependencies:

- `vaderSentiment` (for sentiment detection)
- `tqdm` (progress bar)
- `emoji` (to extract emojis from tweets)
- `reverse_geocoder` (lat, long -> state)

```
pip install tqdm, vaderSentiment, emoji reverse_geocoder --upgrade
```

### Usage
To preprocess hydrated `.jsonl.gz` files, call `process_raw_tweets.py` with a path to the directory that contains the `.jsonl.gz` files. Also specify start (inclusive) and end (exclusive) dates to process.
```
python3 scripts/process_raw_tweets.py --dir 2020-03/ --start 2020-03-01 --end 2020-03-08
```


### Location Extraction
We further filter our dataset to include only tweets from the USA.

Due to a recent [change](https://twitter.com/TwitterSupport/status/1141039841993355264) in the way Twitter collects data, geolocation of most tweets is unavailable in the Twitter API response. We use a three-fold process to extract state-level location tags for as many tweets as possible:

1. For tweets that have `latitude` and `longitude` coordinates we [reverse geocode](https://github.com/thampiman/reverse-geocoder) these coordinates. If the returned address is in the USA, we label the tweet with the returned state label. (~0.1% of all tweets)
2. When users decide to assign a location to a Tweet, they choose from a list of candidate [Places](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/geo-objects#place-dictionary). ~3% of all tweets in our dataset are assigned a place with a bounding box. We reverse geocode the center of this bounding box and save returned state label.
3. User accounts of ~70% of the tweets in our dataset have a location associated with them. The location is user-specified, which means it does not always stand for an attested geographical region. Perhaps for privacy reasons, many users choose made-up locations such as "La-La land", "The Moon", "Hogwarts". 

We sequentially search the user specified location string for occurences of (1) state abbreviations (CA, AL, MA, ..), (2) full state names, (3) USA cities, and (4) various spellings of "the united states of America" (e.g. usa, us, america). If there is a match at any step, we convert the matching string to a 2-letter state abbreviation and label the tweet with that location. 
 
We find that using this method with a list of other countries included as step (5), we are able to resolve 51% of the `user_location` strings in the dataset into a valid location. The unresolved 50% of the strings fall into one of two categories: (1) names of foreign cities that we did not include in our processing step, and (2) made up locations such as 
```
'SkyDome','Iberoamérica', 'Khar West; Mumbai', 'Bde maka ska', 'Chiraq', 'Concrete Jungle; Tomorrowland', 'On the river; UK', 'Blood Harmony', 'EVERYWHERE! ', 'The Sawbones', 'ATX', 'The Chamber; Chi-Raq', 'ig:henys_muva  snap:kiababe', 'Yeah', 'Raisin lil bo', 'i Rock Earth', 'Close to the end of the Earth'
 ```


Running the location processing script
```
cd scripts
python3 process_locations.py --dir ../path/to/preprocessed/tweets/dir/ --out tweets.0301-0331.usa.csv
```

