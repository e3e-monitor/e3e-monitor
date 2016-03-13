import logging
import json
 
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

logging.basicConfig()

####
# ElasticSearch lookup utility class
#
class EsLookup:
    
    def __init__(self, esConfig):
        self.esConfig = esConfig
        self.client = Elasticsearch(esConfig['hosts'])

    def lookupLocations(self, locationsList):
        result = dict()
        
#         for location in locationsList:
#             s = Search(using=self.client, index="geojson") \
#                 .query("match", name=location)
#             response = s.execute()
#             for hit in response:
#                 print(hit.meta.score, hit.name, hit.location) # perform a GEOJSON lookup
        for location in locationsList:
            s = Search(using=self.client, index="geonames") \
                .query("match", asciiname=location)
            response = s.execute()
            for hit in response:
#                 print(hit.meta.score, hit.name, hit.location) # perform a GEOJSON lookup
                if(not(result.has_key(location))):
                    result[location] = []
                result[location].append([hit.meta.score, hit.name, hit.asciiname, hit.location])
             # perform a GEONAME lookup
        # return a dictionary associating the initial location name to its confirmed
        return result