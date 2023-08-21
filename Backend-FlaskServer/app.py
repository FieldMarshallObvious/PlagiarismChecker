from flask import Flask, request, jsonify
from flask_cors import CORS
from components.SearchWeb import query_clean_results
from components.PreProcess_Text import extract_keywords, clean_texts, preprocess_text, segment_text_by_sentences, split_into_segments
from components.Similarity import calculate_cosine_similarity, calculate_cosine_similarity_model, TFID
from components.utils import check_request_data, extract_keywords_from_text, process_all_paragraphs
from components.DownloadContent import get_cdx_records, download_common_crawl_data, get_text_from_link
import nltk
nltk.download('punkt')
import logging

import gensim.downloader as api

word_vectors = api.load("word2vec-google-news-300")
#word_vectors = api.load("glove-wiki-gigaword-50")
#word_vectors = api.load("fasttext-wiki-news-subwords-300")

app = Flask(__name__)
CORS(app)

@app.route('/extract_keywords', methods=['GET']) 
def extract_keywords_route():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Text not provided"}), 400
    response = extract_keywords_from_text(data)

    if 'error' in response:
        return jsonify(response), 400
    
    return jsonify({"results": response})
    

@app.route('/search', methods=['POST'])
def search_content():
    data = request.json
    if not data or 'text' not in data or not isinstance(data['text'], list) or not data['text']:
        return jsonify({"error": "Array of tokens not provided"}), 400

    tokens = data['text']
    results = query_clean_results(tokens)
    
    return jsonify({"results": results})

@app.route('/cosine-similarity', methods=['POST'])
def cosine_similarity_route(data=None):
    if not data:
        data = request.json
    required_fields = {
        'input_texts': list    
    }
    error = check_request_data(data, required_fields)
    if error:
        return error
    
    search_data = []
    clean_input_texts = []
    clean_target_texts = []
    sorted_similaritiy = []
    
    if not data.get('target_texts'):     
        input_data = {"text": data['input_texts'][0]}          
        keywords = extract_keywords_from_text(input_data)
        search_data = query_clean_results(keywords)
        clean_target_texts = [{'content': clean_texts([item['content']]), **{k: v for k, v in item.items() if k != 'content'}} for item in search_data]


    clean_input_texts = clean_texts(data['input_texts'])
    if data.get('target_texts'):       
        clean_target_texts = [{'content': clean_texts([item['content']]), **{k: v for k, v in item.items() if k != 'content'}} for item in data['target_texts']]

    results = []
    seen_links = set()
    topNLinks = []
    for input_text in clean_input_texts:
        average_similarity, max_similarity, individual_similarity, sorted_similaritiy = calculate_cosine_similarity(input_text, clean_target_texts, True if data.get('target_texts') else False)
        
        for item in sorted(sorted_similaritiy, key=lambda x: x['similarity'], reverse=True):
            if item['link'] not in seen_links:
                topNLinks.append(item)
                seen_links.add(item['link'])
            if len(topNLinks) == 5:
                break

        print("Sorted URls", topNLinks)
        
        results.append({
            'input_text': input_text,
            'average_similarity': average_similarity,
            'similarity': max_similarity,
            'individual_similarity': individual_similarity,
            'SortedUrls': topNLinks
        })

    return jsonify(results[0])

@app.route('/cosine-similarity-model', methods=['GET'])
def cosine_similarity_model_route(data=None):
    if not data:
        data = request.json
    required_fields = {
        'input_texts': list,
        'target_texts': list
    }
    error = check_request_data(data, required_fields)
    if error:
        return error
    

    input_text_sentence = segment_text_by_sentences(data['input_texts'][0])
    clean_input_texts = clean_texts(input_text_sentence)
    clean_target_texts = clean_texts(data['target_texts'])

    results = []
    topNLinks = []
    sorted_similarity = []
    seen_links = []
    

    for input_text in clean_input_texts:
            average_similarity, max_similarity, individual_similarity, sorted_similarity = calculate_cosine_similarity_model(input_text, clean_target_texts, word_vectors, True)
            
            for item in sorted(sorted_similarity, key=lambda x: x['similarity'], reverse=True):
                if item['link'] not in seen_links:
                    topNLinks.append(item)
                    seen_links.add(item['link'])
                if len(topNLinks) == 5:
                    break
            
            results.append({
                'input_text': input_text,
                'average_similarity': average_similarity,
                'max_similarity': max_similarity,
                'individual_similarity': individual_similarity,
                'SortedUrls': topNLinks
            })

    return jsonify(results)

@app.route('/download-text', methods=['GET'])
def download_text_route():
    data = request.json
    required_fields = {
        'urls': list
    }
    error = check_request_data(data, required_fields)
    if error:
        return error
    
    urls = data['urls']

    print("Urls are", urls)
    
    errors = []
    for i, url in enumerate(urls):
        try:
            file_name = f"data_{i}.warc.gz"
            record = get_cdx_records(url)
            print("Record is", record)
            if not record:
                errors.append(f"No CDX record found for URL: {url}")
                continue

            download_common_crawl_data(record, file_name)
            logging.info(f"Data saved to {file_name}")
        except Exception as e:
            errors.append(f"Error processing URL {url}: {str(e)}")
            logging.error(f"Failed to process {url}. Reason: {str(e)}")

    if errors:
        return jsonify({"errors": errors}), 500

    return jsonify({"message": "Data download completed."}), 200

@app.route('/find_plagiarism', methods=['POST'])
def find_plagiarism_route():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Text not provided"}), 400
        
    paragraphs = split_into_segments(data["text"], 150, 3)

    processed_data = []
    errors = []
    all_sorted_similarities = []
    topNLinks = []
    max_similarity_overall = 0 
    total_similarities = 0 
    total_paragraphs_processed = 0
    global_search_data = []

    print("Segments")

    processed_data, max_similarity_overall, total_similarities, total_paragraphs_processed, all_sorted_similarities, global_search_data, errors = process_all_paragraphs(paragraphs)

    if max_similarity_overall > 0.3:
        processed_data, max_similarity_overall, total_similarities, total_paragraphs_processed, all_sorted_similarities, global_search_data, errors = process_all_paragraphs(paragraphs, use_model=True, word_vectors=word_vectors, input_search_data=global_search_data)

    average_similarity_overall = total_similarities / total_paragraphs_processed if total_paragraphs_processed else 0

    seen_links = set()
    topNLinks = []

    for item in sorted(all_sorted_similarities, key=lambda x: x['similarity'], reverse=True):
        if item['link'] not in seen_links:
            topNLinks.append(item)
            seen_links.add(item['link'])
        if len(topNLinks) == 5:
            break

    response_data = {"results": processed_data, "similarity": max_similarity_overall, "max_similarity": max_similarity_overall, "SortedUrls": topNLinks}
    if errors:
        response_data['errors'] = errors


    return jsonify(response_data)



if __name__ == '__main__':
    app.run(debug=True)
    app.debug = True