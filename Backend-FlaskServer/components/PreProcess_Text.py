import nltk
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from rake_nltk import Rake




# Download required datasets
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    # Tokenize
    tokens = word_tokenize(text)
    
    # Convert to lowercase
    tokens = [word.lower() for word in tokens]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    return tokens

def generate_ngrams(text, n):
    tokens = text.split()

    if len(tokens) < n:
        return [text]

    ngrams = zip(*[tokens[i:] for i in range(n)])
    
    return [" ".join(ngram) for ngram in ngrams]


def extract_keywords(text, max_keywords=5):
    r = Rake()
    r.extract_keywords_from_text(text)
    
    ranked_phrases = r.get_ranked_phrases()[:max_keywords]
    
    # Lemmatizing the results
    lemmatizer = WordNetLemmatizer()
    lemmatized_phrases = []
    for phrase in ranked_phrases:
        words = phrase.split()
        lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
        lemmatized_phrases.append(' '.join(lemmatized_words))
        
    all_ngrams = []
    for phrase in lemmatized_phrases:
        all_ngrams.extend(generate_ngrams(phrase, 3))
            
    return all_ngrams

def clean_text(text):
    # Initialize the lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Remove punctuation
    text_no_punctuation = ''.join([char for char in text if char not in string.punctuation])
    # Convert to lowercase
    text_lowercase = text_no_punctuation.lower()

    # Remove stop words
    words = text_lowercase.split()
    words_without_stopwords = [word for word in words if word not in set(stopwords.words('english'))]
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words_without_stopwords]
    clean_text = ' '.join(lemmatized_words)
    
    return clean_text.replace("\xa0", "")


def clean_dates(text):
    # Regular expression to detect various date formats
    date_patterns = [
        r'\bJan(?:uary)? \d{1,2}, \d{4}\b',
        r'\bFeb(?:ruary)? \d{1,2}, \d{4}\b',
        r'\bMar(?:ch)? \d{1,2}, \d{4}\b',
        r'\bApr(?:il)? \d{1,2}, \d{4}\b',
        r'\bMay \d{1,2}, \d{4}\b',
        r'\bJun(?:e)? \d{1,2}, \d{4}\b',
        r'\bJul(?:y)? \d{1,2}, \d{4}\b',
        r'\bAug(?:ust)? \d{1,2}, \d{4}\b',
        r'\bSep(?:tember)? \d{1,2}, \d{4}\b',
        r'\bOct(?:ober)? \d{1,2}, \d{4}\b',
        r'\bNov(?:ember)? \d{1,2}, \d{4}\b',
        r'\bDec(?:ember)? \d{1,2}, \d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{2,4}-\d{1,2}-\d{1,2}\b'
    ]

    # Find all date tokens
    date_tokens = [match.group(0) for pattern in date_patterns for match in re.finditer(pattern, text)]
    
    # Remove date tokens from the text
    for date_token in date_tokens:
        text = text.replace(date_token, '', 1)  # Only remove one occurrence at a time
    
    return text.strip()

def clean_texts(texts):
    return [clean_text(clean_dates(text)) for text in texts]

text = "The solar system consists of the Sun and the objects including the planets, comets, and asteroids."
keywords = extract_keywords(text)
print(keywords)

# Example usage:
text = "The quick brown foxes are jumping over the lazy dogs."
print(preprocess_text(text))


def split_into_segments(text, character_length=100, num_segments=3):
    # Create a list to store the segments
    desired_segment_length = len(text) // num_segments
    segments = []

    if ( len(text) < character_length ):
        return [text]

    for _ in range(num_segments - 1):
        # Find the last space or punctuation near the desired segment length
        split_index = text.rfind(' ', 0, desired_segment_length)
        if split_index == -1:
            split_index = text.rfind('.', 0, desired_segment_length)
        if split_index == -1:
            split_index = desired_segment_length
        
        # Append the segment to our list
        segments.append(text[:split_index].strip())
        # Remove the segment from the text
        text = text[split_index:].strip()

    # Add any remaining text as the last segment
    if text:
        segments.append(text)

    return segments

def segment_text_by_sentences(text):
    sentences = sent_tokenize(text)
    for sentence in sentences:
        yield sentence
