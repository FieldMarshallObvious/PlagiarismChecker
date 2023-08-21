from .PreProcess_Text import  preprocess_text
from collections import Counter
from math import sqrt
import np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



def tokens_to_vector(tokens, model):
    vector_size = model.vector_size
    text_vector = np.zeros(vector_size)
    count = 0

    tokens_list = tokens.split()

    print("token list", tokens_list)


    for token in tokens_list:
        print("token is", token)
        if token in model: 
            text_vector += model[token]
            count += 1

    if count == 0:
        return np.zeros(vector_size)
    else:
        return text_vector / count
    

def tokens_to_vector_with_tfidf(tokens, model, tfidf_vectorizer):
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
    Segments the text into chunks with a fixed number of tokens.
    """
    tokens = text.split()
    segments = []
    
    for i in range(0, len(tokens), token_length):
        segment = tokens[i: i + token_length]
        segments.append(' '.join(segment))
    
    return segments

def cosine_similarity_continuous(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    
    if magnitude1 * magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)


def cosine_similarity_tokens(counter1, counter2, all_tokens):

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

def calculate_cosine_similarity(input_text, target_texts):
    num_targets = len(target_texts)
    total_similarity = 0.0
    max_similarity = 0.0
    individual_similarity = []
    
    tokens1 = preprocess_text(input_text)
    counter1 = Counter(tokens1)

    for index, target_text in enumerate(target_texts):
        tokens2 = preprocess_text(target_text)
        counter2 = Counter(tokens2)

        # Get unique tokens
        all_tokens = set(tokens1).union(tokens2)
        current_similarity = cosine_similarity_tokens(counter1, counter2, all_tokens)
        total_similarity += current_similarity
        individual_similarity.append({f"{index}": current_similarity})
        max_similarity = max(max_similarity, current_similarity)

    average_similarity = total_similarity / num_targets if num_targets > 0 else 0
    return average_similarity, max_similarity, individual_similarity

def segment_text(text, segment_length):
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
    corpus = [input_text]
    for target_text in target_texts:
        corpus.append(target_text["content"][0] if not notJSON else target_text)
    return corpus

def TFID(input_text, target_texts, notJSON = False):
    num_targets = len(target_texts)
    total_similarity = 0.0
    max_similarity = 0.0
    individual_similarity = []

    #print("Input text", input_text)
    #print("input text type", type(input_text))
    #print("Target texts", target_texts)
    #print("Target text type", type(target_texts))

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
        print("Segment is:", input_segments[i])

        for j, target_vector in enumerate(target_vectors):
            target_content = target_texts[j]["content"][0] if not notJSON else target_texts[j]
            print("Target text:", target_content)

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
            print("Similarity is", current_similarity)

    average_similarity = total_similarity / (num_targets * len(input_segments)) if num_targets > 0 else 0

    sorted_similarity = sorted(individual_similarity, key=lambda x: x['similarity'], reverse=True)

    return average_similarity, max_similarity, individual_similarity, sorted_similarity

def calculate_cosine_similarity_model(input_text, target_texts, model, notJSON = False):
    num_targets = len(target_texts)
    total_similarity = 0.0
    max_similarity = 0.0
    individual_similarity = []

    #print("Input text", input_text)
    #print("input text type", type(input_text))
    #print("Target texts", target_texts)
    #print("Target text type", type(target_texts))

    input_segments = [input_text]

    corpus = build_corpus(input_text, target_texts, notJSON)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

    for i, segment in enumerate(input_segments):
        #print("Segment is:", segment)
        vector1 = tokens_to_vector_with_tfidf(segment, model, tfidf_vectorizer)
        #print("Vector 1", vector1)

        for j, target_text in enumerate(target_texts):
            #print("Target text:", target_text["content"][0] if not notJSON else target_text)
            vector2 = tokens_to_vector_with_tfidf(target_text["content"][0] if not notJSON else target_text, model, tfidf_vectorizer)   
            #print("Vector 2", vector2)
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
            #print("Similarity is", current_similarity)

    average_similarity = total_similarity / (num_targets * len(input_segments)) if num_targets > 0 else 0

    sorted_similarity = sorted(individual_similarity, key=lambda x: x['similarity'], reverse=True)

    return average_similarity, max_similarity, individual_similarity, sorted_similarity

