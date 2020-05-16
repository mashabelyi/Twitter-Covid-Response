"""
Extract locations from pre-processed tweet files
Save only tweets from USA
"""
import os, json, re, gzip
import reverse_geocoder as rg

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

def bbox_string(bbox):
    if bbox is None:
        return ''
    return ' '.join(["lat{}lng{}".format(x[0], x[1]) for x in bbox])

def state_from_placename(tweet, name):

	# state codes
	res = re.search(r'\b({})\b'.format('|'.join(state_codes)), name, flags=re.IGNORECASE)
	if res:
		# return tweet[:-5] + [res[0].upper()]
		return res.group(0).upper()

	# state names
	res = re.search(r'\b({})\b'.format('|'.join(state_names)), name, flags=re.IGNORECASE)
	if res:
		# return tweet[:-5] + [state2code[res[0].lower()]] # convert to state code (CA, MA, IL,...)
		return state2code[res.group(0).lower()] # convert to state code (CA, MA, IL,...)

	# check USA cities
	res_city = re.search(r'\b({})\b'.format('|'.join(us_cities)), name, flags=re.IGNORECASE)
	if res_city:
		return state2code[city2state[res_city.group(0).lower()]] # convert to state code (CA, MA, IL,...)

	# is it at least in the USA?
	res = re.search(r'\b({})\b'.format('|'.join(usa_country_names)), name, flags=re.IGNORECASE)
	if res:
		return '' # return empty state

	# to check other countries:
	# res = re.search(r'\b({})\b'.format('|'.join(countries)), row['name'], flags=re.IGNORECASE)
	# if res:
	# 	return tweet[:-5] + [res[0].lower()]

	# everything else
	return None


def parser(tweet):
	# Input: Tweet object with attributes:
	# lat, long, place_bbox, place_name, user_name
	#
	# Try to extract location from tweet
	# if succeed, and tweet is in the USA, 
	# return updated tweet object

	# has lat, long?
	if tweet.lat and tweet.long:
		lat = float(tweet.lat)
		lng = float(tweet.long)
		try:
			result = rg.search((lt,ln))[0]
			if result['cc']=='US':
				return result['admin1']
			else:
				return None
		except:
			pass

	# has place_bbox?
	bbox = tweet.place_bbox
	if bbox and len(bbox) > 1:
		# use center of bbox

		# corners = bbox.split()
		# res = [re.match('lat([\d.-]*)lng([\d.-]*)', c) for c in corners]

		# # WARNING: lat and lngs are accidentally reversed in the bbox entry!
		# lngs = [float(x[1]) for x in res]
		# lats = [float(x[2]) for x in res]

		lngs = [x[0] for x in bbox]
		lats = [x[1] for x in bbox]

		lat = (min(lats) + max(lats))/2
		lng = (min(lngs) + max(lngs))/2

		try:
			result = rg.search((lt,ln))[0]
			if result['cc']=='US':
				return result['admin1']
			else:
				return None
		except:
			pass


	# has place name?
	place_name = tweet.place_name
	if place_name and len(place_name) > 1:
		try:
			return state_from_placename(tweet, place_name)
		except:
			return None

	# has user_location?
	user_location = tweet.user_location
	if user_location and len(user_location) > 1:
		# return state_from_placename(tweet, user_location)
		try:
			return state_from_placename(tweet, user_location)
		except:
			return None

	return None
