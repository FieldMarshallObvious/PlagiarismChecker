from flask import Flask, request, jsonify
from flask_cors import CORS
from components.SearchWeb import query_clean_results
from components.PreProcess_Text import extract_keywords, clean_texts,preprocess_text
from components.Similarity import calculate_cosine_similarity, calculate_cosine_similarity_model, TFID
from components.utils import check_request_data, extract_keywords_from_text
from components.DownloadContent import get_cdx_records, download_common_crawl_data, get_text_from_link
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import logging

import gensim.downloader as api

word_vectors = api.load("word2vec-google-news-300")
#word_vectors = api.load("glove-wiki-gigaword-50")
#word_vectors = api.load("fasttext-wiki-news-subwords-300")


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

@app.route('/cosine-similarity', methods=['GET'])
def cosine_similarity_route(data=None):
    if not data:
        data = request.json
    required_fields = {
        'input_texts': list,
        'target_texts': list
    }
    error = check_request_data(data, required_fields)
    if error:
        return error

    clean_input_texts = clean_texts(data['input_texts'])
    clean_target_texts = [{'content': clean_texts([item['content']]), **{k: v for k, v in item.items() if k != 'content'}} for item in data['target_texts']]

    results = []
    for input_text in clean_input_texts:
        average_similarity, max_similarity, individual_similarity = calculate_cosine_similarity(input_text, clean_target_texts)
        results.append({
            'input_text': input_text,
            'average_similarity': average_similarity,
            'max_similarity': max_similarity,
            'individual_similarity': individual_similarity
        })

    return jsonify(results)

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
    print("texts type", type(data['input_texts']))
    print("Clean input texts", clean_input_texts)
    results = []
    for input_text in clean_input_texts:
            average_similarity, max_similarity, individual_similarity, sorted_similarity = calculate_cosine_similarity_model(input_text, clean_target_texts, word_vectors, True)
            results.append({
                'input_text': input_text,
                'average_similarity': average_similarity,
                'max_similarity': max_similarity,
                'individual_similarity': individual_similarity
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

    print("Segments")

    for index, paragraph in enumerate(paragraphs):
        try:
            keyword_data = extract_keywords_from_text({"text":paragraph})
            if 'error' in keyword_data:
                return jsonify(keyword_data), 400
            
            search_data = query_clean_results(keyword_data['results'])
            if 'error' in search_data:
                print("exception occured when searchin data")
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

                for clean_paragraph in clean_paragraphs:
                    average_similarity, max_similarity, individual_similarity, sorted_similarity = calculate_cosine_similarity_model(clean_paragraph, clean_search_data, word_vectors)
                    cosine_data = {
                        'average_similarity': average_similarity, 
                        'max_similarity': max_similarity, 
                        'sorted_similarity': sorted_similarity
                    }
                    paragraph_data['cosine_similarity'] = cosine_data
                    current_paragraph_similarity_max += max_similarity 
                    all_sorted_similarities.extend(sorted_similarity)        
                    current_paragraph_similarity += average_similarity
                    print("Max similarity is ", max_similarity)


                current_paragraph_similarity /= len(clean_paragraphs)
                current_paragraph_similarity_max /= len(clean_paragraphs)
                total_similarities += current_paragraph_similarity
                max_similarity_overall = max(max_similarity_overall, current_paragraph_similarity_max)
                total_paragraphs_processed += 1
                    
                print("Calculated similarity")

            processed_data.append(paragraph_data)
        except Exception as e:
            errors.append({"paragraph_index": index, "error_message": str(e)})


    average_similarity_overall = total_similarities / total_paragraphs_processed if total_paragraphs_processed else 0

    seen_links = set()
    topNLinks = []

    for item in sorted(all_sorted_similarities, key=lambda x: x['similarity'], reverse=True):
        if item['link'] not in seen_links:
            topNLinks.append(item)
            seen_links.add(item['link'])
        if len(topNLinks) == 5:
            break

    response_data = {"results": processed_data, "similarity": average_similarity_overall, "max_similarity": max_similarity_overall, "SortedUrls": topNLinks}
    if errors:
        response_data['errors'] = errors


    return jsonify(response_data)



if __name__ == '__main__':
    app.run(debug=True)
    app.debug = True