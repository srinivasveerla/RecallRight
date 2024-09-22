import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
import json

class TextProcessor:

	def generate_tag_metadata(self, tags):
		# Load English language model
		nlp = spacy.load("en_core_web_sm")
		# Process the text with spaCy
		doc = nlp(tags)
		# Extract named entities and their labels
		meta_data = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
		# Convert meta data to JSON format
		meta_data_json = json.dumps(meta_data)
		return meta_data_json


	def preprocess_content(self, text):
		# Tokenization
		tokens = word_tokenize(text)
		
		# Remove Noise
		cleaned_tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
		
		# Normalization (convert to lowercase)
		cleaned_tokens = [token.lower() for token in cleaned_tokens]
		
		# Remove Stopwords
		stop_words = set(stopwords.words('english'))
		cleaned_tokens = [token for token in cleaned_tokens if token not in stop_words]
		
		# Lemmatize data
		formatted_text = ' '.join(cleaned_tokens)
		nlp = spacy.load("en_core_web_sm")
		lemmatized_tokens = [token.lemma_ for token in nlp(formatted_text)]
		
		return ' '.join(lemmatized_tokens)