from components.PreProcess_Text import extract_keywords, segment_text_by_sentences, clean_texts
from components.SearchWeb import query_clean_results
from components.Similarity import calculate_cosine_similarity_model, TFID


def check_request_data(data, required_fields):
    """
    Validates the presence and type of required fields in the provided data.
    
    Parameters:
    - data (dict): The data to validate.
    - required_fields (dict): A dictionary mapping required field names to their expected types.

    Returns:
    - tuple: A message and status code indicating an error, or None if validation passes.
    """

    if not data:
        return "Invalid data", 400

    for key, expected_type in required_fields.items():
        if key not in data:
            return f"Missing {key}", 400
        if not isinstance(data[key], expected_type):
            return f"{key} is not of type {expected_type.__name__}", 400
        if expected_type == list and not data[key]:
            return f"{key} is empty", 400

    return None

def extract_keywords_from_text(data):
    """
    Wrapper to extract keywords from dict text obeject.
    
    Parameter:
    - data (dict): Dictionary containing the 'text' key with textual data.

    Returns:
    - dict: A dictionary with extracted keywords under the 'results' key.
    """

    text = data['text']
    results = extract_keywords(text)
    return {"results": results}


def process_paragraph(paragraph, global_search_data=None, word_vectors=None):
    """
    Processes a given paragraph: extracts keywords, queries results based on these keywords, 
    segments the paragraph by sentences, and computes cosine similarity between the paragraph 
    and search results using either word vectors or TF-IDF.
    
    Parameters:
    - paragraph (str): Text paragraph to process.
    - global_search_data (dict, optional): Precomputed search data to use, if available.
    - word_vectors (model, optional): Pre-trained word vectors, if available.

    Returns:
    - tuple: Contains processed paragraph data, average similarity, maximum similarity, and 
             sorted list of similarities.
    """
        
    all_sorted_similarities = []
    sentence_similarities = []

    keyword_data = extract_keywords_from_text({"text": paragraph})
    if 'error' in keyword_data:
        return {"error": keyword_data}
    
    search_data = query_clean_results(keyword_data['results']) if not global_search_data else global_search_data
    if 'error' in search_data:
        raise Exception(search_data['error'])

    paragraph_data = {
        'paragraph': paragraph,
        'keywords': keyword_data['results'],
        'search_results': search_data
    }

    if search_data:
        paragraph_sentences = segment_text_by_sentences(paragraph)
        clean_paragraphs = clean_texts(paragraph_sentences)
        clean_search_data = [{'content': clean_texts([item['content']]), **{k: v for k, v in item.items() if k != 'content'}} for item in search_data]

        current_paragraph_similarity = 0
        current_paragraph_similarity_max = 0

        print("Paragraph sentences", clean_paragraphs)

        for clean_paragraph in clean_paragraphs:
            if word_vectors:
                average_similarity, max_similarity, individual_similarity, sorted_similarity = calculate_cosine_similarity_model(clean_paragraph, clean_search_data, word_vectors)
                all_sorted_similarities.extend(sorted_similarity)

            else:
                average_similarity, max_similarity, individual_similarity, sorted_similarity = TFID(clean_paragraph, clean_search_data)
                all_sorted_similarities.extend(sorted_similarity)

            cosine_data = {
                'sentence': clean_paragraph,
                'average_similarity': average_similarity,
                'max_similarity': max_similarity,
                'sorted_similarity': sorted_similarity
            }
            sentence_similarities.append(cosine_data)
            paragraph_data['cosine_similarity'] = cosine_data
            current_paragraph_similarity_max = max(max_similarity, current_paragraph_similarity_max)
            current_paragraph_similarity += average_similarity

        print("Length of paragraph similarities in paragraph proccess is", len(sentence_similarities))

        current_paragraph_similarity /= len(clean_paragraphs)
        #current_paragraph_similarity_max /= len(clean_paragraphs)
    return paragraph_data, current_paragraph_similarity, current_paragraph_similarity_max, all_sorted_similarities, sentence_similarities


def process_all_paragraphs(paragraphs, use_model=False, word_vectors=None, input_search_data=None):
    """
    Processes a list of paragraphs to extract keywords, compute cosine similarities, and capture any errors.
    Can utilize a provided word vector model or default to TF-IDF for similarity calculations.

    Parameters:
    - paragraphs (list): List of text paragraphs to process.
    - use_model (bool, optional): Flag to determine if word vectors should be used for similarity calculation.
    - word_vectors (model, optional): Pre-trained word vectors, if available.
    - input_search_data (dict, optional): Precomputed search data, if available.

    Returns:
    - tuple: Contains processed data for each paragraph, maximum similarity across all paragraphs, total 
             similarities, number of paragraphs processed, a sorted list of similarities, global search data, 
             overall entence similarities, and any errors encountered during processing.
    """
        
    processed_data = []
    errors = []
    all_sorted_similarities = []
    sentence_similarities_overall = []
    max_similarity_overall = 0
    total_similarities = 0
    total_paragraphs_processed = 0
    global_search_data = []

    for index, paragraph in enumerate(paragraphs):
        try:
            if use_model:
                paragraph_data, current_paragraph_similarity, current_paragraph_similarity_max, sorted_similarities, sentence_similarities = process_paragraph(paragraph, input_search_data, word_vectors)
                all_sorted_similarities.extend(sorted_similarities)
                sentence_similarities_overall.extend(sentence_similarities)
            else:
                paragraph_data, current_paragraph_similarity, current_paragraph_similarity_max, sorted_similarities, sentence_similarities = process_paragraph(paragraph)
                global_search_data = paragraph_data['search_results']
                all_sorted_similarities.extend(sorted_similarities)
                sentence_similarities_overall.extend(sentence_similarities)



            total_similarities += current_paragraph_similarity
            max_similarity_overall = max(max_similarity_overall, current_paragraph_similarity_max)
            total_paragraphs_processed += 1

            processed_data.append(paragraph_data)
        except Exception as e:
            errors.append({"paragraph_index": index, "error_message": str(e)})

        print("Lengh of in loop sentence similarities ", len(sentence_similarities_overall))

    print("Final Length of sentence similarities is", len(sentence_similarities_overall))

    return processed_data, max_similarity_overall, total_similarities, total_paragraphs_processed, all_sorted_similarities, global_search_data, sentence_similarities_overall, errors
