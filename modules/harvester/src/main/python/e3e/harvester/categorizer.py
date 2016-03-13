import nltk
import numpy as np

from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist, ELEProbDist
from nltk.classify.util import apply_features, accuracy


class Categorizer(object):
    def __init__(self, category_dictionary):
#         self.bomb_trig = ['bomb','bombings','bombs','explosion','explosions']
#         self.airstrike_trig = ['airstrike','airstrikes']
#         self.jet_trig = ['jet','jets']
#         self.drone_trig = ['drone','drones']
        self.category_dictionary = category_dictionary
        self.trigger_words = []
        for value in self.category_dictionary.values():
            self.trigger_words.extend(value.split(","))  # bomb_trig + airstrike_trig + jet_trig + trigger_words
        self.attack_vec = np.array([0, 0, 0, 0])
        self.predictedLocation = []

    def get_words_in_tweet(self, tweet):
        all_words = []
        filtered_words = (word for word in word_tokenize(tweet) if word in self.trigger_words)
        if any(filtered_words):
            all_words.extend(word_tokenize(tweet))
        return all_words

    def classify_attack(self, tweet):
        all_words = self.get_words_in_tweet(tweet)
        categories = []
        for key, value in  self.category_dictionary.items():
            if any(x for x in value.split(",") if x in all_words):
                categories.append(key)
        return categories

    def get_word_features(self, wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()  # For training purposes
        return wordlist

    
    def analyse(self, tweet):
        words_at_tweet = self.get_words_in_tweet(tweet)
        tagged_words_at_tweet = pos_tag(words_at_tweet)
        predictedLocation = [x for x, y in tagged_words_at_tweet if y == 'NNP']
        attack_vec = self.classify_attack(tweet)
        return [predictedLocation,attack_vec]

    def get_attack_vec(self):
        return self.attack_vec

    def get_predictedLocation(self):
        return self.predictedLocation
