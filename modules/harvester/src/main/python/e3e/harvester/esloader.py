import logging
import json
 
from elasticsearch import Elasticsearch

logging.basicConfig()
from datetime import datetime

####
# ElasticSearch loader utility class
#
class EsLoader:
    
    def __init__(self, esConfig):
        self.esConfig = esConfig
        self.client = Elasticsearch(esConfig['hosts'])
        # Define a default Elasticsearch client

    def saveTweet(self, tweet):
        # create and save and article
        res = self.client.index(index="tweets", doc_type='tweet', id=tweet.id, body={ \
                                                'text':tweet.text,'location': {'lat':float(tweet.location.lat), 'lon':float(tweet.location.lon)}, 'location_name':tweet.location_name, 'created_at': tweet.created_at} )
        
        
        print(res['created'])


    