from .PreProcess_Text import  preprocess_text
from collections import Counter
from math import sqrt
import np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



def tokens_to_vector(tokens, model):
    """
    Converts a space-separated string of tokens into an averaged word vector representation using a given word embedding model.

    The function calculates the vector representation of each token present in the model and 
    then averages these vectors to get a single vector representation for the entire input.

    Parameters:
    - tokens (str): Space-separated string of words/tokens to be converted.
    - model (Word2Vec-like model): A word embedding model which provides vector representations of words.
    
    Returns:
    - ndarray: Averaged vector representation of the input tokens. If none of the tokens are found in the model, 
               a zero vector of the model's vector size is returned.
    
    Note:
    It is assumed that the provided model has a 'vector_size' attribute and supports indexing by word tokens 
    (e.g., a Word2Vec model). The function prints each token being processed which can be helpful for debugging.
    """
        
    vector_size = model.vector_size
    text_vector = np.zeros(vector_size)
    count = 0

    tokens_list = tokens.split()

    for token in tokens_list:
        if token in model: 
            text_vector += model[token]
            count += 1

    if count == 0:
        return np.zeros(vector_size)
    else:
        return text_vector / count
    

def tokens_to_vector_with_tfidf(tokens, model, tfidf_vectorizer):
    """
    Converts tokens into a vector representation using a word embedding model, weighted by their TF-IDF values.

    Parameters:
    - tokens (str): Space-separated tokens to be converted.
    - model: Word embedding model providing vector representations.
    - tfidf_vectorizer: TF-IDF vectorizer for weighing tokens.

    Returns:
    - ndarray: Vector representation of the tokens, weighted by their TF-IDF values.
    """

    vector_size = model.vector_size
    text_vector = np.zeros(vector_size)

    # Transform the list of tokens to a single string
    tokens_list = tokens.split()
    text = ' '.join(tokens_list)
    
    # Compute tf-idf values
    tfidf_values = tfidf_vectorizer.transform([text]).toarray()[0]

    # Get the mapping of token to its index
    feature_names = tfidf_vectorizer.get_feature_names_out()
    total_tfidf = 0

    feature_names_list = feature_names.tolist()

    for token in tokens_list:
        if token in model and token in feature_names:
            index = feature_names_list.index(token)
            text_vector += model[token] * tfidf_values[index]
            total_tfidf += tfidf_values[index]

    if total_tfidf == 0:
        return np.zeros(vector_size)
    else:
        return text_vector / total_tfidf
    
def segment_by_fixed_length(text, token_length=20):
    """
    Splits the input text into segments, each containing a fixed number of tokens.

    Parameters:
    - text (str): The input text to be segmented.
    - token_length (int, optional): The desired number of tokens in each segment. Default is 20.

    Returns:
    - List[str]: List of segments, each containing approximately 'token_length' tokens.
    
    Note:
    The last segment may contain fewer tokens if the total number of tokens in the input is not a 
    multiple of 'token_length'.
    """

    tokens = text.split()
    segments = []
    
    for i in range(0, len(tokens), token_length):
        segment = tokens[i: i + token_length]
        segments.append(' '.join(segment))
    
    return segments

def cosine_similarity_continuous(vector1, vector2):
    """
    Computes the cosine similarity between two vectors.

    Parameters:
    - vector1, vector2 (ndarray): Input vectors for comparison.

    Returns:
    - float: Cosine similarity value ranging from -1 (dissimilar) to 1 (similar). 
             Returns 0 if either vector magnitude is zero.
    """
        
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    
    if magnitude1 * magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)


def cosine_similarity_tokens(counter1, counter2, all_tokens):
    """
    Computes the cosine similarity between two token counters based on a defined set of tokens.

    Parameters:
    - counter1, counter2 (collections.Counter): Counters representing token frequencies.
    - all_tokens (list): List of all possible tokens for consideration.

    Returns:
    - float: Cosine similarity value between -1 (dissimilar) and 1 (similar). 
             Returns 0 if either counter's magnitude is zero.
    """

    # Create vectors
    vector1 = [counter1[token] for token in all_tokens]
    vector2 = [counter2[token] for token in all_tokens]

    # Compute dot product
    dot_product = sum([vector1[i]*vector2[i] for i in range(len(all_tokens))])

    # Compute magnitudes
    magnitude1 = sqrt(sum([vector1[i]*vector1[i] for i in range(len(all_tokens))]))
    magnitude2 = sqrt(sum([vector2[i]*vector2[i] for i in range(len(all_tokens))]))
    
    if magnitude1 * magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

def calculate_cosine_similarity(input_text, target_texts, notJSON = False):
    """
    Calculates cosine similarities between an input text and a list of target texts.

    Parameters:
    - input_text (str): Text for which similarity needs to be computed.
    - target_texts (list): List of texts (or JSON-like objects) to compare against the input.
    - notJSON (bool, optional): If True, considers target_texts as plain text; otherwise as JSON-like objects.

    Returns:
    - average_similarity (float): Average similarity across all target texts.
    - max_similarity (float): Maximum similarity value among target texts.
    - individual_similarity (list): List containing similarity scores for each target text.
    - sorted_similarity (list): List of target texts sorted by their similarity scores in descending order.

    Note:
    If target_texts contain JSON-like objects, they are expected to have "content", "link", and "title" keys.
    """
        
    num_targets = len(target_texts)
    total_similarity = 0.0
    max_similarity = 0.0
    individual_similarity = []
    
    tokens1 = preprocess_text(input_text)
    counter1 = Counter(tokens1)

    for index, target_text in enumerate(target_texts):
        tokens2 = preprocess_text(target_text["content"][0] if not notJSON else target_text)
        counter2 = Counter(tokens2)

        # Get unique tokens
        all_tokens = set(tokens1).union(tokens2)
        current_similarity = cosine_similarity_tokens(counter1, counter2, all_tokens)
        total_similarity += current_similarity
        individual_similarity.append({
                    'link_index': index,
                    'similarity': current_similarity,
                    'link': target_texts[index]["link"] if not notJSON else "",
                    'title': target_texts[index]["title"] if not notJSON else "",
                })        
        max_similarity = max(max_similarity, current_similarity)

    average_similarity = total_similarity / num_targets if num_targets > 0 else 0
    sorted_similarity = sorted(individual_similarity, key=lambda x: x['similarity'], reverse=True)

    return average_similarity, max_similarity, individual_similarity, sorted_similarity

def segment_text(text, segment_length):
    """
    Segments a given text into chunks of a specified length after preprocessing.

    Parameters:
    - text (str): The input text to be segmented.
    - segment_length (int): The desired number of tokens in each segment.

    Returns:
    - list: A list of segmented texts, each containing up to the specified number of tokens.

    Note:
    The text is preprocessed (tokenized, lowercased, stopwords removed, etc.) before segmentation.
    """
    tokens = preprocess_text(text)
    segments = []

    if len(tokens) <= segment_length:
        segments.append(' '.join(tokens))
        return segments

    for i in range(0, len(tokens), segment_length):
        segment = tokens[i: i + segment_length]
        segments.append(' '.join(segment))

    return segments

def build_corpus(input_text, target_texts, notJSON=False):
    """
    Constructs a corpus comprising an input text followed by a list of target texts.

    Parameters:
    - input_text (str): Initial text to be added to the corpus.
    - target_texts (list): List of texts or JSON-like objects to append to the corpus.
    - notJSON (bool, optional): If True, treats target_texts as plain texts; otherwise as JSON-like objects with a "content" key.

    Returns:
    - list: A corpus consisting of the input text followed by the target texts.

    Note:
    If target_texts contain JSON-like objects, they are expected to have "content" keys.
    """
    corpus = [input_text]
    for target_text in target_texts:
        corpus.append(target_text["content"][0] if not notJSON else target_text)
    return corpus

def TFID(input_text, target_texts, notJSON = False):
    """
    Computes the TF-IDF cosine similarity between an input text and a list of target texts.

    Parameters:
    - input_text (str): The main text to compare against target texts.
    - target_texts (list): A list of texts or JSON-like objects to compare against the input text.
    - notJSON (bool, optional): If True, treats target_texts as plain texts; otherwise, as JSON-like objects.

    Returns:
    - average_similarity (float): The average cosine similarity across all comparisons.
    - max_similarity (float): The highest cosine similarity from the comparisons.
    - individual_similarity (list): A list of dictionaries detailing similarities for each pair.
    - sorted_similarity (list): A sorted version of individual_similarity in descending order.


    Note:
    If target_texts contain JSON-like objects, they are expected to have "content", "link", and "title" keys.
    """
        
    num_targets = len(target_texts)
    total_similarity = 0.0
    max_similarity = 0.0
    individual_similarity = []

    input_segments = [input_text]

    # Prepare the corpus for TF-IDF Vectorizer
    corpus = input_segments + [text["content"][0] if not notJSON else text for text in target_texts]

    # Create and fit the TF-IDF model
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Assuming your input_segments and target_texts are of considerable length, 
    # we need to slice the matrix to get vectors for segments and target_texts
    segment_vectors = tfidf_matrix[:len(input_segments)]
    target_vectors = tfidf_matrix[len(input_segments):]

    for i, segment_vector in enumerate(segment_vectors):

        for j, target_vector in enumerate(target_vectors):

            current_similarity = cosine_similarity(segment_vector, target_vector)[0][0]
            
            total_similarity += current_similarity
            individual_similarity.append({
                'segment_index': i,
                'link_index': j,
                'similarity': current_similarity,
                'link': target_texts[j]["link"] if not notJSON else "",
                'title': target_texts[j]["title"] if not notJSON else "",
            })

            max_similarity = max(max_similarity, current_similarity)

    average_similarity = total_similarity / (num_targets * len(input_segments)) if num_targets > 0 else 0

    sorted_similarity = sorted(individual_similarity, key=lambda x: x['similarity'], reverse=True)

    return average_similarity, max_similarity, individual_similarity, sorted_similarity

def calculate_cosine_similarity_model(input_text, target_texts, model, notJSON = False):
    """
    Computes the cosine similarity between an input text and target texts using a given model and TF-IDF weighting.

    Parameters:
    - input_text (str): The main text to compare against target texts.
    - target_texts (list): A list of texts or JSON-like objects to compare against the input text.
    - model (Model): The word embedding model used for vector representations.
    - notJSON (bool, optional): If True, treats target_texts as plain texts; otherwise, as JSON-like objects with "content", "link", and "title" keys.

    Returns:
    - average_similarity (float): The average cosine similarity across all comparisons.
    - max_similarity (float): The highest cosine similarity from the comparisons.
    - individual_similarity (list): A list of dictionaries detailing similarities for each pair.
    - sorted_similarity (list): A sorted version of individual_similarity in descending order.


    Note:
    If target_texts contain JSON-like objects, they are expected to have "content", "link", and "title" keys.
    """
        
    num_targets = len(target_texts)
    total_similarity = 0.0
    max_similarity = 0.0
    individual_similarity = []


    input_segments = [input_text]

    corpus = build_corpus(input_text, target_texts, notJSON)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_vectorizer.fit_transform(corpus)

    for i, segment in enumerate(input_segments):
        vector1 = tokens_to_vector_with_tfidf(segment, model, tfidf_vectorizer)

        for j, target_text in enumerate(target_texts):
            vector2 = tokens_to_vector_with_tfidf(target_text["content"][0] if not notJSON else target_text, model, tfidf_vectorizer)   

            current_similarity = cosine_similarity_continuous(vector1, vector2)
            total_similarity += current_similarity
            individual_similarity.append({
                        'segment_index': i,
                        'link_index': j,
                        'similarity': current_similarity,
                        'link': target_texts[j]["link"] if not notJSON else "",
                        'title': target_texts[j]["title"] if not notJSON else "",
                    })
            
            max_similarity = max(max_similarity, current_similarity)

    average_similarity = total_similarity / (num_targets * len(input_segments)) if num_targets > 0 else 0

    sorted_similarity = sorted(individual_similarity, key=lambda x: x['similarity'], reverse=True)

    return average_similarity, max_similarity, individual_similarity, sorted_similarity

