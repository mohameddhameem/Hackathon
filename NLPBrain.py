#  Copyright (c) 2019. Created for UBS Hackathon. Intended to use within UBS network.
#  Author - UBS MMS Team


#Lets try to import some of the required packages
from datetime import datetime
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

#for Cloud provider, lets use IBM Watson for now
import watson_developer_cloud
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, ConceptsOptions

#for NLP process in local we can use NLTK
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize

#for processing datetime
import parsedatetime

import config

#To begin we need to download the NLTK corpus for local processing
localNLTK = nltk.downloader.Downloader()
localNLTK._update_index()

nltk.download('punkt', halt_on_error=False)
nltk.download('averaged_perceptron_tagger', halt_on_error=False)
nltk.download('maxent_ne_chunker', halt_on_error=False)
nltk.download('words', halt_on_error=False)

#Before proceeding further, create a Watson Developer account.
#Refer https://cloud.ibm.com/ for furter instruction

""" Define all your Constant variable here. create a config file and store all the required password"""
API_USERNAME = config.IBM_API_USERNAME
API_PASSWORD = config.IBM_API_PASSWORD

#Below class is for base NLP
class NLPBrain:
    nlp_engine = NaturalLanguageUnderstandingV1(
        version='2017-02-27',
        username=API_USERNAME,
        password= API_PASSWORD
    )

    def __init__(self, transcript_file_path, summary_number):
        self.transcript_file = transcript_file_path
        with open(transcript_file_path, 'r') as f1:
            data = f1.read()
            #print(data)
        full_transcript_text = data
        #print('type ->', type(full_transcript_text))


        self.tokenized_transcript = sent_tokenize(full_transcript_text);

        LANGUAGE = "English"
        parser = PlaintextParser.from_file(self.transcript_file, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        self.summary = summarizer(parser.document, summary_number)

    def _sentence_entity_finder(self, sentence):

        try:
            response = self.nlp_engine.analyze(
                text=sentence,
                features=Features(entities=EntitiesOptions(), keywords=KeywordsOptions()))
            if response.get("entities") == []:
                return None
            return ((response.get("entities")[0]).get("text"))
        except watson_developer_cloud.watson_service.WatsonApiException:
            return None

    def _concept_finder(self, sentence):
        try:
            response = self.nlp_engine.analyze(text=sentence,
                                               features=Features(concepts=ConceptsOptions(limit=5)))
            #print('Response from Concept Finder ->', response)
            if response.get("concepts") == []:
                return None
            return (response.get("concepts")[0]).get("text")
        except watson_developer_cloud.watson_service.WatsonApiException:
            return None

    def _keyword_detector(self, sentence):
        try:
            response = self.nlp_engine.analyze(
                text=sentence,
                features=Features(
                    keywords=KeywordsOptions(
                        sentiment=False,
                        emotion=True,
                        limit=2)))
            keywords = []
            for item in response.get("keywords"):
                keywords += [item.get("text")];
            return keywords
        except watson_developer_cloud.watson_service.WatsonApiException:
            return []

    def frequently_discussed_topics(self):
        topics = []
        for sentence in self.summary:
            topics += [self._keyword_detector(str(sentence))]
            entity = self._sentence_entity_finder(str(sentence))
            if entity is not None:
                topics += [entity]
        important_topics = []
        for item in topics:
            if topics.count(item) > 1:
                important_topics += [item]
        return set(important_topics)

    def concepts_discussed(self):
        concepts = []
        for sentence in self.summary:
            concept = (self._concept_finder(str(sentence)))
            if concept is not None:
                concepts += [concept]
        return concepts

    def retrieve_calendar_items(self):
        calendar_items = []
        for sentence in self.tokenized_transcript:
            possible_date = self._date_parser(sentence.decode("utf-8"))
            if possible_date is not None:
                calendar_items += [(sentence, possible_date, self._keyword_detector(str(sentence)))]
        return calendar_items

    def retrieve_action_items(self):
        action_items = []
        for sentence in self.tokenized_transcript:
            possible_command = self._command_detected(str(sentence))
            if possible_command is True:
                action_items += [(str(sentence).replace('\n',' <br>'))]
        return action_items

    command_words = ["can you", "would you", "can we", "you should", "we should", "we need to",
                     "you need to", "ensure", "make sure", "make it", "we want to", "we must",
                     "you must", "you have to", "we have to" "homework"]
    prohibited_command_words = ["Let me", "?"]

    def _command_detected(self, sentence):
        tagged_sentence = pos_tag(word_tokenize(sentence));
        first_word = tagged_sentence[0];
        #print('first_word ->', first_word)
        pos_first = first_word[1];
        first_word = first_word[0].lower()
        for word in self.prohibited_command_words:
            if word in sentence:
                return False
        for word in self.command_words:
            if word in sentence:
                return True

        if (pos_first == "VB" or pos_first == "VBZ" or pos_first == "VBP") and first_word[-3:] != "ing":
            return True
        return False

    schedule_words = [" by ", " due ", "plan", "setup", "schedule", "complete by", "complete on", "next", " on ",
                      " in "]
    prohibited_schedule_words = ["today"]

    def _date_parser(self, sentence):
        cal = parsedatetime.Calendar()
        time_struct, parse_status = cal.parse(sentence)
        time_struct_null, parse_status_null = cal.parse("")

        # If the time detected is the same as the current time, discard.
        if datetime(*time_struct[:6]) == datetime(*time_struct_null[:6]):
            return None

        for word in self.prohibited_schedule_words:
            if word in sentence:
                return None
        # Events cannot be schedule in the past.
        tagged_sentence = pos_tag(word_tokenize(sentence));
        for word in tagged_sentence:
            if word[1] == "VBD":
                return None

        for word in self.schedule_words:
            if word in sentence:
                return datetime(*time_struct[:6])
        return None

    def text_summary(self):
        transcript_summary = ""
        for sentence in self.summary:
            transcript_summary = transcript_summary + " <br>&#9658;" + str(sentence)
        return transcript_summary