import json, os, re
from datetime import datetime
# For sentiment analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sent = SentimentIntensityAnalyzer()
# emoji extractor
import emoji

def domain(url):
    try:
        res = re.match('^(?:https?:)?(?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)', url)
        return res.group(1)
    except:
        return url.replace(',', '')

def clean_text(text):
    # remove urls
    text = re.sub('https?:\/\/.*[\r\n]*', '', text)
    # remove commas and new lines
    text = re.sub('[\n\r,]', ' ', text)
    return text.strip()

def bbox_string(bbox):
    if bbox is None:
        return ''
    return ' '.join(["lat{}lng{}".format(x[0], x[1]) for x in bbox])

def extract_emojis(str):
    return ' '.join(c for c in str if c in emoji.UNICODE_EMOJI)

class Tweet:
    column_names = [
            'tweetId', 'lang',
            'userId', 'user_screen_name',
            'year', 'month', 'date', 'day', 'hour', 'minute', 'utc_offset',
            'text', 'hashtags', 'user_mentions', 'symbols', 'urls', 'emojis', 'sentiment',
            'retweet_cont', 'favorite_count',
            'lat', 'long', 'user_location', 'place_name', 'place_bbox'
        ]
    def __init__(self, json):
        self.parse(json)
    def bbox_string(self, bbox):
        if bbox is None:
            return ''
        return ' '.join(["lat{}lng{}".format(x[0], x[1]) for x in bbox])
    def from_string(self, str):
        data = str.split(',')
        self.id = data[0]

    def parse(self, data):
        # Tweet
        self.id = data['id_str']
        self.lang = data['lang']
        self.text = clean_text(data['full_text']) if 'full_text' in data else clean_text(data['text'])
        # overall sentiment
        try:
            self.sentiment = sent.polarity_scores(self.text)['compound']
        except:
            self.sentiment = None

        try:
            self.emojis = extract_emojis(self.text)
        except:
            self.emojis = ''
                
        #LOCATION
        self.long = None
        self.lat = None
        if 'coordinates' in data and data['coordinates'] is not None:
            self.long = data['coordinates']['coordinates'][0]
            self.lat = data['coordinates']['coordinates'][1]

        # PLACE
        self.place_bbox = None
        self.place_name = None
        if 'place' in data and data['place'] is not None:
            try:
                self.place_bbox = data['place']['bounding_box']['coordinates'][0]
            except:
                pass

            try:
                self.place_name = data['place']['full_name'].replace(',', ';')
            except:
                pass

        
        # RETWEETS, LIKES
        self.retweet_count = data['retweet_count']
        self.favorite_count = data['favorite_count']
        
        # ENTITIES
        self.hashtags = [x['text'] for x in data['entities']['hashtags']]
        self.user_mentions = [x['screen_name'] for x in data['entities']['user_mentions']]
        self.symbols = [x['text'] for x in data['entities']['symbols']]
        self.urls = [domain(x['expanded_url']) for x in data['entities']['urls']] # note: grab only the domain
                
        # User
        self.userId = data['user']['id_str']
        self.user_screen_name = data['user']['screen_name']
        self.user_location = data['user']['location'].replace(',', ';')
        
        # Date
        self.datetime = data['created_at']
        self.dt = datetime.strptime(self.datetime, '%a %b %d %H:%M:%S %z %Y')
#         print(dt.year, dt.month, dt.day, dt.weekday(), dt.hour, dt.minute, dt.utcoffset())

    def to_csv(self):
        return ",".join([
            self.id, self.lang,
            self.userId, self.user_screen_name,
            str(self.dt.year), str(self.dt.month), str(self.dt.day), str(self.dt.weekday()),
            str(self.dt.hour), str(self.dt.minute), str(self.dt.utcoffset()),
            self.text, ' '.join(self.hashtags), ' '.join(self.user_mentions),
            ' '.join(self.symbols), ' '.join(self.urls), self.emojis, str(self.sentiment) if not self.sentiment is None else '',
            str(self.retweet_count), str(self.favorite_count),
            str(self.lat or ''), str(self.long or ''), str(self.user_location or ''),
            (self.place_name or ''), bbox_string(self.place_bbox)
        ]).replace('\n', '')

class Retweet:
    column_names = [
            'tweetId', 'retweeted_id',
            'userId', 'user_screen_name',
            'year', 'month', 'date', 'day', 'hour', 'minute', 'utc_offset',
            'lat', 'long', 'user_location', 'place_name', 'place_bbox'
        ]
    def __init__(self, json):
        self.parse(json)
    def parse(self, data):
        # Tweet
        self.id = data['id_str']
        
        # Date
        self.datetime = data['created_at']
        self.dt = datetime.strptime(self.datetime, '%a %b %d %H:%M:%S %z %Y')
        
        # User
        self.userId = data['user']['id_str']
        self.user_screen_name = data['user']['screen_name']
        self.user_location = data['user']['location'].replace(',', ';')
        
        #LOCATION
        self.long = None
        self.lat = None
        if 'coordinates' in data and data['coordinates'] is not None:
            self.long = data['coordinates']['coordinates'][0]
            self.lat = data['coordinates']['coordinates'][1]

        # PLACE
        self.place_bbox = None
        self.place_name = None
        if 'place' in data and data['place'] is not None:
            try:
                self.place_bbox = data['place']['bounding_box']['coordinates'][0]
            except:
                pass

            try:
                self.place_name = data['place']['full_name'].replace(',', ';')
            except:
                pass
            
        # RETWEET ID
        self.retweeted_id = data['retweeted_status']['id_str']        
    
    def to_csv(self):
        return ",".join([
            self.id, self.retweeted_id,
            self.userId, self.user_screen_name,
            str(self.dt.year), str(self.dt.month), str(self.dt.day), str(self.dt.weekday()),
            str(self.dt.hour), str(self.dt.minute), str(self.dt.utcoffset()),
            str(self.lat or ''), str(self.long or ''), str(self.user_location or ''),
            (self.place_name or ''), bbox_string(self.place_bbox)
        ]).replace('\n', '')

class QuoteTweet:
    column_names = [
            'tweetId', 'quoted_id',
            'userId', 'user_screen_name',
            'year', 'month', 'date', 'day', 'hour', 'minute', 'utc_offset',
            'lat', 'long', 'user_location', 'place_name', 'place_bbox'
        ]
    def __init__(self, json):
        self.parse(json)
    def parse(self, data):
        # Tweet
        self.id = data['id_str']
        
        # Date
        self.datetime = data['created_at']
        self.dt = datetime.strptime(self.datetime, '%a %b %d %H:%M:%S %z %Y')
        
        # User
        self.userId = data['user']['id_str']
        self.user_screen_name = data['user']['screen_name']
        self.user_location = data['user']['location'].replace(',', ';')
        
        #LOCATION
        self.long = None
        self.lat = None
        if 'coordinates' in data and data['coordinates'] is not None:
            self.long = data['coordinates']['coordinates'][0]
            self.lat = data['coordinates']['coordinates'][1]

        # PLACE
        self.place_bbox = None
        self.place_name = None
        if 'place' in data and data['place'] is not None:
            try:
                self.place_bbox = data['place']['bounding_box']['coordinates'][0]
            except:
                pass

            try:
                self.place_name = data['place']['full_name'].replace(',', ';')
            except:
                pass
        
        self.quoted_id = data['quoted_status_id_str']
    
    def to_csv(self):
        return ",".join([
            self.id, self.quoted_id,
            self.userId, self.user_screen_name,
            str(self.dt.year), str(self.dt.month), str(self.dt.day), str(self.dt.weekday()),
            str(self.dt.hour), str(self.dt.minute), str(self.dt.utcoffset()),
            str(self.lat or ''), str(self.long or ''), str(self.user_location or ''),
            (self.place_name or ''), bbox_string(self.place_bbox)
        ]).replace('\n', '')