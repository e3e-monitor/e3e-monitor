import tweepy
from config import Config
from categorizer import Categorizer
import logging
import json
from eslookup import EsLookup
from esloader import EsLoader

logging.basicConfig()

class Harvester:
    
    def __init__(self):
        self.config = Config()
        self.categorizer = Categorizer(self.config.yaml['categories'])
        self.esLoader = EsLoader(self.config.yaml['elasticsearch'])
        self.esLookup = EsLookup(self.config.yaml['elasticsearch'])

      
    def start(self):
        auth = tweepy.OAuthHandler(self.config.yaml['twitter']['consumer_key'], self.config.yaml['twitter']['consumer_secret'])
        auth.set_access_token(self.config.yaml['twitter']['access_token'], self.config.yaml['twitter']['access_token_secret'])
#         
        api = tweepy.API(auth)
#                 
        tweets = api.search("drone", lang = "en", geocode="36.53,38.21,500km")
        for tweet in tweets:
            print tweet.text
            print "Location : "+",".join(self.categorizer.analyse(tweet.text)[0])
            geonameMatches = self.esLookup.lookupLocations((self.categorizer.analyse(tweet.text)[0]))
            if (len(geonameMatches.keys()) > 0):
                firstKey = geonameMatches.keys()[0]
                tweet.location = geonameMatches[firstKey][0][3]
                tweet.location_name = geonameMatches[firstKey][0][1]
                print "location : "+tweet.location_name
                self.esLoader.saveTweet(tweet)
#                 print json.dumps(tweet)
            print "Vector : "+",".join(self.categorizer.analyse(tweet.text)[1])
            
            
#           print self.categorizer.analyse(tweet.text)[1]
#             
#             print tweet.text 
            
#         eslookup = EsLookup(self.config.yaml["elasticsearch"])
#         print eslookup.lookupLocations(["Aleppo", "Shaytalun"])

#         f1=open('./explosions.json', 'w+')
#         f1.write("[")
#         for tweet in tweets:

#             f1.write("{'author':")
#             json.dump(tweet.author,f1)
#             f1.write(", 'tweet':")
#             json.dump(tweet.text,f1)
#             f1.write("}")
#         f1.write("]")
#         f1.close()
#       

        # categorize
        
        # dump as JSON


if __name__ == '__main__':
    harvester = Harvester()
    harvester.start()
