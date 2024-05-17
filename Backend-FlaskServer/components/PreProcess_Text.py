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
    """
    Preprocess the given text to make it suitable for text analysis.
    
    Steps:
    1. Tokenization: Break the text into individual words.
    2. Case Normalization: Convert all the tokens into lowercase to ensure uniformity.
    3. Stopword Removal: Remove commonly used words (like 'and', 'the', etc.) which might not add significant meaning in text analysis.
    4. Lemmatization: Convert words to their base or dictionary form. For instance, 'running' becomes 'run'.
    
    Parameters:
    - text (str): The input string that needs to be preprocessed.
    
    Returns:
    - List[str]: A list of preprocessed and cleaned tokens.
    """
        
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
    """
    Generate n-grams from the provided text.
    
    An n-gram is a contiguous sequence of n items (in this case, words) from the given text.
    For example, for the text "I love programming", the 2-grams (bigrams) would be:
    ["I love", "love programming"]
    
    Parameters:
    - text (str): The input string from which n-grams need to be generated.
    - n (int): The number of items (words) in each generated n-gram.
    
    Returns:
    - List[str]: A list of n-grams generated from the input text. If the text has fewer tokens 
                 than 'n', the entire text is returned as the sole item in the list.
    
    Note:
    This function assumes that the text does not have any punctuation or special characters 
    that need to be handled separately. It's recommended to preprocess the text accordingly 
    before using this function for accurate n-gram generation.
    """
        
    tokens = text.split()

    if len(tokens) < n:
        return [text]

    ngrams = zip(*[tokens[i:] for i in range(n)])
    
    return [" ".join(ngram) for ngram in ngrams]


def extract_keywords(text, max_keywords=5):
    """
    Extracts keywords from the input text using the Rake algorithm, lemmatizes them, 
    and then generates 3-grams from the lemmatized keyword phrases.
    
    Parameters:
    - text (str): Input text for keyword extraction.
    - max_keywords (int, optional): Maximum number of keyword phrases to extract. Default is 5.
    
    Returns:
    - List[str]: 3-grams generated from the lemmatized keyword phrases.
    """
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
    """
    Cleans the provided text by performing the following steps:
    1. Removes punctuation.
    2. Converts to lowercase.
    3. Removes English stop words.
    4. Lemmatizes the words to their base form.
    5. Removes non-breaking space characters.
    
    Parameters:
    - text (str): The raw text input that needs to be cleaned.
    
    Returns:
    - str: The cleaned and preprocessed version of the input text.
    """
        
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
    """
    Removes common date formats from the given text.
    
    The function identifies dates in various forms such as "January 1, 2020", "Jan 1, 2020", 
    "1/1/2020", and "2020-01-01", and removes them from the provided text.
    
    Parameters:
    - text (str): Input text that may contain date values.
    
    Returns:
    - str: Text with date occurrences removed.
    
    Note:
    The function uses regular expressions for date pattern recognition and may not capture 
    all possible date variations. 
    """
        
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
    """
    Cleans a list of texts by removing common date formats and applying standard text preprocessing.
    
    The function applies two primary cleaning steps:
    1. Removes recognized date formats from each text.
    2. Conducts general text preprocessing (e.g., lemmatization, removal of punctuation and stop words).
    
    Parameters:
    - texts (List[str]): List of raw text strings to be cleaned.
    
    Returns:
    - List[str]: List of cleaned text strings.
    """
        
    return [clean_text(clean_dates(text)) for text in texts]

def split_into_segments(text, character_length=100, num_segments=3):
    """
    Splits a given text into a specified number of segments. Each segment tries to 
    break near the desired segment length, prioritizing breaks at spaces or periods.
    
    Parameters:
    - text (str): The input text to be segmented.
    - character_length (int, optional): Desired character length for each segment. Default is 100.
    - num_segments (int, optional): Number of segments to split the text into. Default is 3.
    
    Returns:
    - List[str]: List of segmented strings.
    
    Note:
    If the entire text length is less than the specified `character_length`, the original text 
    is returned as a single segment. Also, if no space or period is found near the desired 
    segment length, the segment might split at the specified `character_length`.
    """
        
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


text = "The solar system consists of the Sun and the objects including the planets, comets, and asteroids."
keywords = extract_keywords(text)
print(keywords)

# Example usage:
text = "The quick brown foxes are jumping over the lazy dogs."
print(preprocess_text(text))