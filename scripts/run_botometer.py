"""
Run botometer on input list of twitter users

"""
import botometer
import os, json, re, gzip
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tqdm import tqdm

parser = ArgumentParser("ProcessTweets", formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve') #'2020-03'
# parser.add_argument("--in", help="Data directory.", required=True)
parser.add_argument("--out", help="Output file", required=True)
parser.add_argument("--u", help="User file", required=True)
args = parser.parse_args()

MIN_TWEETS = 20 # don't check users with less than this tweets

botometer_api_url = 'botometer-pro.p.rapidapi.com'

rapidapi_key = "e347deb455msha49d2421717ce37p14d25djsnd0a886875693" # now it's called rapidapi key
twitter_app_auth = {
    'consumer_key': 'phUthlyGshmPYD4Z1Hd72DPUU',
    'consumer_secret': 'mrkyBIIUjFatLmhxU4hLjcaznWQRFxWleivEyPvR1HyasAJI4P',
    'access_token': '717748976926085120-Kn9RWiTxFQn6nmrgrKAK2Sgnsdp4Por',
    'access_token_secret': '2unbfGZbmGX24We8zkCobkL3osdROBSM2dCDSFSTdLvQu',
  }

botometer_api_url = 'https://botometer-pro.p.rapidapi.com'
bom = botometer.Botometer(botometer_api_url=botometer_api_url,
                          wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)


# with open(args.out, 'w') as f:
# 	f.write("userId,user_screen_name,pBot\n")

accounts = []
## Load in list of users
with open(args.u, 'r') as f:
	for line in f:
		uid, handle, count = line.strip().split(',')
		
		if int(count) >= MIN_TWEETS:
			accounts.append(uid)

accounts = accounts[13935:] # DEV
print("checking {} accounts".format(len(accounts)))

for uid, result in bom.check_accounts_in(accounts):

	if 'error' in result:
		continue

	with open(args.out, 'a') as f:
		f.write("{},{},{}\n".format(
			result['user']['id_str'],
			result['user']['screen_name'],
			result['cap']['english'])
		)



