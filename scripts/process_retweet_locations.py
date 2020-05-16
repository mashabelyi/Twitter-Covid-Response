"""
Extract locations from pre-processed tweet files
Save only tweets from USA
"""
import os, json, re, gzip
import reverse_geocoder as rg
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from joblib import Parallel, delayed
from tqdm import tqdm

parser = ArgumentParser("ProcessTweets", formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve') #'2020-03'
parser.add_argument("--dir", help="Data directory.", required=True)
parser.add_argument("--out", help="Output file", required=True)
parser.add_argument("--njobs", default=1, type=int, help="num parallel jobs", required=False)
args = parser.parse_args()


# load state:[cities list] json
with open('us_state_cities.json', 'r') as f:
	state_cities = json.load(f)

# map each city to its state
city2state = {city.lower():state.lower() for state in state_cities for city in state_cities[state]}

# get just a list of cities
us_cities = [x.lower() for state, cities in state_cities.items() for x in cities ]

# load us state abbreviations
with open('us_states.json', 'r') as f:
	data = json.load(f)
	state2code = {v.lower():k for k,v in data.items()}
	
# load list of countries
# with open('countries.txt', 'r') as f:
#     countries = []
#     for line in f:
#         countries.append(line.strip())

state_codes = ['AL','AK','AZ','AR','CA','CO','CT','DE', 'DC', 'FL',
			 'GA','HI','ID','IL','IN','IA','KS','KY','LA',
			 'ME','MD','MA','MI','MN','MS','MO','MT','NE',
			 'NV','NH','NJ','NM','NY','NC','ND','OH','OK',
			 'OR','PA','RI','SC','SD','TN','TX','UT','VT',
			 'VA','WA','WV','WI','WY']

state_names = ['Alabama','Alaska',
			 'Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia',
			 'Hawaii','Idaho','Illinois', 'Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland',
			 'Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana', 'Nebraska','Nevada',
			 'New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota',
			 'Ohio','Oklahoma','Oregon','Pennsylvania', 'Rhode Island','South Carolina','South Dakota',
			 'Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']


usa_country_names = ['America', 'US', 'USA', 'U.S', 'U.S.A', 'estados unidos']


def state_from_placename(tweet, name):

	# state codes
	res = re.search(r'\b({})\b'.format('|'.join(state_codes)), name, flags=re.IGNORECASE)
	if res:
		# return tweet[:-5] + [res[0].upper()]
		return tweet[:-5] + [res.group(0).upper()]

	# state names
	res = re.search(r'\b({})\b'.format('|'.join(state_names)), name, flags=re.IGNORECASE)
	if res:
		# return tweet[:-5] + [state2code[res[0].lower()]] # convert to state code (CA, MA, IL,...)
		return tweet[:-5] + [state2code[res.group(0).lower()]] # convert to state code (CA, MA, IL,...)

	# check USA cities
	res_city = re.search(r'\b({})\b'.format('|'.join(us_cities)), name, flags=re.IGNORECASE)
	if res_city:
		return tweet[:-5] + [state2code[city2state[res_city.group(0).lower()]]] # convert to state code (CA, MA, IL,...)

	# is it at least in the USA?
	res = re.search(r'\b({})\b'.format('|'.join(usa_country_names)), name, flags=re.IGNORECASE)
	if res:
		return tweet[:-5] + [''] # return empty state

	# to check other countries:
	# res = re.search(r'\b({})\b'.format('|'.join(countries)), row['name'], flags=re.IGNORECASE)
	# if res:
	# 	return tweet[:-5] + [res[0].lower()]

	# everything else
	return None


def process_location(tweet):
	# Try to extract location from tweet
	# if succeed, and tweet is in the USA, 
	# return updated tweet object

	# has lat, long?
	if tweet[-5] and tweet[-4]:
		lat = float(tweet[-5])
		lng = float(tweet[-4])
		try:
			result = rg.search((lt,ln))[0]
			if result['cc']=='US':
				return tweet[:-5] + [result['admin1']]
			else:
				return None
		except:
			pass

	# has place_bbox?
	bbox = tweet[-1]
	if bbox and len(bbox) > 1:
		# use center of bbox
		corners = bbox.split()
		res = [re.match('lat([\d.-]*)lng([\d.-]*)', c) for c in corners]

		# WARNING: lat and lngs are accidentally reversed in the bbox entry!
		lngs = [float(x[1]) for x in res]
		lats = [float(x[2]) for x in res]

		lat = (min(lats) + max(lats))/2
		lng = (min(lngs) + max(lngs))/2

		try:
			result = rg.search((lt,ln))[0]
			if result['cc']=='US':
				return tweet[:-5] + [result['admin1']]
			else:
				return None
		except:
			pass


	# has place name?
	place_name = tweet[-2]
	if place_name and len(place_name) > 1:
		try:
			return state_from_placename(tweet, place_name)
		except:
			return None

	# has user_location?
	user_location = tweet[-3]
	if user_location and len(user_location) > 1:
		# return state_from_placename(tweet, user_location)
		try:
			return state_from_placename(tweet, user_location)
		except:
			return None


column_names = [
			'tweetId', 'retweeted_id',
			'userId', 'user_screen_name','retweeted_userId', 'retweeted_user_screen_name',
			'year', 'month', 'date', 'day', 'hour', 'minute', 'utc_offset',
			'text', 'hashtags', 'user_mentions', 'symbols', 'urls', 'emojis', 'sentiment',
			'retweet_cont', 'favorite_count',
			'state']

# retweet_column_names = [
#     'tweetId', 'retweeted_id',
#     'userId', 'user_screen_name','retweeted_userId', 'retweeted_user_screen_name',
#     'year', 'month', 'date', 'day', 'hour', 'minute', 'utc_offset',
#     'lat', 'long', 'user_location', 'place_name', 'place_bbox'
# ]

with open(args.out, 'w') as f:
	f.write(','.join(column_names) + '\n')

# usa_tweets = []

# cycle through all pre-processed retweet files
for fname in os.listdir(args.dir):
	if fname.startswith('retweets') and fname.endswith('.csv.gz'):
		print(fname)
		
		# process file
		tweets_to_parse = []
		with gzip.open(os.path.join(args.dir, fname), 'rt', encoding='utf-8') as f:
			for line in f:
				if line.startswith('tweetId'):
					continue

				tweet = line.split(',')
				tweet[-1] = tweet[-1].strip() # remove the newline char
				if len(tweet) != 18:
					continue

				# res = process_location(tweet)
				# if res:
				# 	with open(args.out, 'a') as fout:
				# 		fout.write('{},,,,,,,,,,{}\n'.format(','.join(res[:-1]), res[-1]))

				tweets_to_parse.append(tweet)
				
				# save every 100,000
				if len(tweets_to_parse) >= 500000:
					for tweet in tqdm(tweets_to_parse):
						res = process_location(tweet)
						if res:
							with open(args.out, 'a') as f:
								f.write('{},,,,,,,,,,{}\n'.format(','.join(res[:-1]), res[-1]))

					tweets_to_parse = []

					# PARALLEL JOBS ARE SLOW FOR THIS!
					# results = Parallel(n_jobs=args.njobs)(delayed(process_location)(tweet) for tweet in tqdm(tweets_to_parse))
					# tweets_to_parse = []

					# with open(args.out, 'a') as f:
					# 	for res in results:
					# 		if res:
					# 			with open(args.out, 'a') as f:
					# 				f.write('{},,,,,,,,,,{}\n'.format(','.join(res[:-1]), res[-1]))

					
		for tweet in tqdm(tweets_to_parse):
			res = process_location(tweet)
			if res:
				with open(args.out, 'a') as f:
					f.write('{},,,,,,,,,,{}\n'.format(','.join(res[:-1]), res[-1]))

		

# # save output to file
# with open(args.out, 'w') as f:
# 	# TODO: add header
# 	for tw in usa_tweets:
# 		f.write(','.join(tw),'\n')


