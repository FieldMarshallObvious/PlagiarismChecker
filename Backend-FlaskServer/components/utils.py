from components.PreProcess_Text import extract_keywords, segment_text_by_sentences, clean_texts
from components.SearchWeb import query_clean_results
from components.Similarity import calculate_cosine_similarity_model, TFID


def check_request_data(data, required_fields):
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
    text = data['text']
    results = extract_keywords(text)
    return {"results": results}


def process_paragraph(paragraph, global_search_data=None, word_vectors=None):
    all_sorted_similarities = []
    keyword_data = extract_keywords_from_text({"text": paragraph})
    if 'error' in keyword_data:
        return {"error": keyword_data}
    
    print("Global search data", global_search_data)

    search_data = query_clean_results(keyword_data['results']) if not global_search_data else global_search_data
    if 'error' in search_data:
        raise Exception(search_data['error'])

    paragraph_data = {
        'paragraph': paragraph,
        'keywords': keyword_data['results'],
        'search_results': search_data
    }

    if search_data:
        print("Paragraph type", type(paragraph))
        print("Search data type", type(search_data))
        paragraph_sentences = segment_text_by_sentences(paragraph)
        clean_paragraphs = clean_texts(paragraph_sentences)
        clean_search_data = [{'content': clean_texts([item['content']]), **{k: v for k, v in item.items() if k != 'content'}} for item in search_data]

        current_paragraph_similarity = 0
        current_paragraph_similarity_max = 0
        print("Clean paragraphs", clean_paragraphs)

        for clean_paragraph in clean_paragraphs:
            print("Clean paragraph", clean_paragraph)
            if word_vectors:
                print("using word vectors")
                average_similarity, max_similarity, individual_similarity, sorted_similarity = calculate_cosine_similarity_model(clean_paragraph, clean_search_data, word_vectors)
                all_sorted_similarities.extend(sorted_similarity)

            else:
                print("Not using word vectors")
                average_similarity, max_similarity, individual_similarity, sorted_similarity = TFID(clean_paragraph, clean_search_data)
                all_sorted_similarities.extend(sorted_similarity)

            cosine_data = {
                'average_similarity': average_similarity,
                'max_similarity': max_similarity,
                'sorted_similarity': sorted_similarity
            }
            paragraph_data['cosine_similarity'] = cosine_data
            current_paragraph_similarity_max = max(max_similarity, current_paragraph_similarity_max)
            current_paragraph_similarity += average_similarity

        current_paragraph_similarity /= len(clean_paragraphs)
        #current_paragraph_similarity_max /= len(clean_paragraphs)
    return paragraph_data, current_paragraph_similarity, current_paragraph_similarity_max, all_sorted_similarities


def process_all_paragraphs(paragraphs, use_model=False, word_vectors=None, input_search_data=None):
    processed_data = []
    errors = []
    all_sorted_similarities = []
    max_similarity_overall = 0
    total_similarities = 0
    total_paragraphs_processed = 0
    global_search_data = []

    for index, paragraph in enumerate(paragraphs):
        try:
            if use_model:
                paragraph_data, current_paragraph_similarity, current_paragraph_similarity_max, sorted_similarities = process_paragraph(paragraph, input_search_data, word_vectors)
                all_sorted_similarities.extend(sorted_similarities)
            else:
                paragraph_data, current_paragraph_similarity, current_paragraph_similarity_max, sorted_similarities = process_paragraph(paragraph)
                global_search_data = paragraph_data['search_results']
                all_sorted_similarities.extend(sorted_similarities)


            total_similarities += current_paragraph_similarity
            max_similarity_overall = max(max_similarity_overall, current_paragraph_similarity_max)
            total_paragraphs_processed += 1

            processed_data.append(paragraph_data)
        except Exception as e:
            errors.append({"paragraph_index": index, "error_message": str(e)})

    return processed_data, max_similarity_overall, total_similarities, total_paragraphs_processed, all_sorted_similarities, global_search_data, errors
