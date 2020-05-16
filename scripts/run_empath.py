import os, json, re
from tqdm import tqdm
from joblib import Parallel, delayed
from empath import Empath
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


frames = ['social_media','trust','friends','help','body','office','dance','money','wedding',
          'domestic_work','sleep','medical_emergency','cold','hate','cheerfulness','aggression',
          'occupation','envy','anticipation','family','vacation','crime','attractive','masculine',
          'prison','health','pride','dispute','nervousness','government','weakness','horror',
          'swearing_terms','leisure','suffering','royalty','wealthy','tourism','furniture','school',
          'magic','beach','journalism','morning','banking','exercise','night','kill','blue_collar_job',
          'art','ridicule','play','computer','college','optimism','stealing','real_estate',
          'home','divine','sexual','fear','irritability','superhero','business','driving','pet',
          'childish','cooking','exasperation','religion','hipster','internet','surprise','reading',
          'worship','leader','independence','movement','noise','eating','medieval','zest','confusion',
          'water','sports','death','healing','legend','heroic','celebration','restaurant','violence',
          'programming','dominant_heirarchical','military','neglect','swimming','exotic','love',
          'hiking','communication','hearing','order','sympathy','hygiene','weather','anonymity',
          'ancient','deception','fabric','air_travel','fight','dominant_personality','music','vehicle',
          'politeness','toy','farming','meeting','war','speaking','listen','urban','shopping','disgust',
          'fire','tool','phone','gain','sound','injury','sailing','rage','science','work','appearance',
          'valuable','warmth','youth','sadness','fun','emotional','joy','affection','traveling','fashion',
          'ugliness','lust','shame','torment','economics','anger','politics','ship','clothing','car',
          'strength','technology','breaking','shape_and_size','power','white_collar_job','animal','party',
          'terrorism','smell','disappointment','poor','plant','pain','beauty','timidity','philosophy',
          'negotiate','negative_emotion','cleaning','messaging','competing','law','payment','achievement',
          'alcohol','liquid','feminine','weapon','children','monster','ocean','giving','contentment',
          'writing','rural','positive_emotion','musical']


parser = ArgumentParser("Run Empath", formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve')
parser.add_argument("--inp", help="Input file", required=True)
parser.add_argument("--out", help="Output file", required=True)
parser.add_argument("--njobs", default=1, type=int, help="num parallel jobs", required=False)
args = parser.parse_args()

def process(tw):
	lexicon = Empath()
	result = lexicon.analyze(tw[11].lower(), normalize=True)
	if result:
		data = [result[fr] for fr in frames]

		with open(args.out, 'a') as f:
			f.write(tw[0] + ',' + ','.join([str(x) for x in data]) + '\n')


def main():
	# load all tweets
	tweets = []
	with open(args.inp, 'r') as f:
	    for line in f:
	        if line.startswith('tweetId'):
	            continue
	        tweets.append(line.split(','))
	print("loaded {} tweets".format(len(tweets)))

	with open(args.out, 'w') as f:
		f.write('tweetId,' + ','.join(frames) + '\n')


	Parallel(n_jobs=args.njobs)(delayed(process)(tw) for tw in tqdm(tweets))

if __name__=='__main__':
    main()