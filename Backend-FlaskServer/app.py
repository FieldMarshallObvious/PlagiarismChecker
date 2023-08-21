# Standard libraries
import logging

# Third-party libraries
import nltk
from flask import Flask, jsonify, request
from flask_cors import CORS
import gensim.downloader as api


# Local application imports
from components.DownloadContent import (download_common_crawl_data, get_cdx_records, get_text_from_link)
from components.PreProcess_Text import (clean_texts, extract_keywords, preprocess_text,
                                        segment_text_by_sentences, split_into_segments)
from components.SearchWeb import query_clean_results
from components.Similarity import (TFID, calculate_cosine_similarity, 
                                   calculate_cosine_similarity_model)
from components.utils import (check_request_data, extract_keywords_from_text, 
                              process_all_paragraphs)

#Download necessary data
nltk.download('punkt')

word_vectors = api.load("word2vec-google-news-300")
#word_vectors = api.load("glove-wiki-gigaword-50")
#word_vectors = api.load("fasttext-wiki-news-subwords-300")

app = Flask(__name__)
CORS(app)

@app.route('/extract_keywords', methods=['GET']) 
def extract_keywords_route():
    """
    Endpoint to extract keywords from a given text.

    URL: /extract_keywords
    Method: GET

    Request Body:
    {
        "text": "sample text from which keywords need to be extracted"
    }

    Requirements:
    - The `text` field must be provided and should be a non-empty string

    Responses:
    1. If 'text' is not provided in the request body:
        {
            "error": "Text not provided"
        }
       Status Code: 400

    2. If there's any internal error during keyword extraction:
        {
            "error": "specific error message"
        }
       Status Code: 400

    3. Successful keyword extraction:
        {
            "results": { keyword1, keyword2, ... }
        }
       Status Code: 200 
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Text not provided"}), 400
    response = extract_keywords_from_text(data)

    if 'error' in response:
        return jsonify(response), 400
    
    return jsonify({"results": response})
    

@app.route('/search', methods=['POST'])
def search_content():
    """
    Endpoint to search content based on a list of provided tokens.

    URL: /search
    Method: POST

    Request Body:
    {
        "text": ["token1", "token2", ...]
    }

    Requirements:
    - The `text` field must be provided and should be a non-empty list of strings (tokens).
    - Each token is used to query the content.

    Responses:
    1. If the `text` field is not provided, is not a list, or is an empty list:
        {
            "error": "Array of tokens not provided"
        }
       Status Code: 400

    2. Successful search:
        {
            "results": { {"content": ..., "link": ..., "title": ...} ... }
        }
       Status Code: 200 (implicitly set by Flask if not specified)
    """
    data = request.json
    if not data or 'text' not in data or not isinstance(data['text'], list) or not data['text']:
        return jsonify({"error": "Array of tokens not provided"}), 400

    tokens = data['text']
    results = query_clean_results(tokens)
    
    return jsonify({"results": results})

@app.route('/cosine-similarity', methods=['POST'])
def cosine_similarity_route(data=None):
    """
    Route: '/cosine-similarity'
    Method: POST

    This endpoint calculates the cosine similarity between input texts and a set of target texts. 
    If the target texts are not provided, the route will extract keywords from the input texts and search for relevant data to use as target texts.

    Requirements:
    - The `text` field must be provided and should be a non-empty list of strings

    Expected Input:
    - input_texts (list): A list of strings which are the texts for which the cosine similarity needs to be calculated.
    - target_texts (optional list): A list of target texts against which the cosine similarity is calculated. 
                                    Each item is a dictionary containing content and other metadata.
                                    If not provided, relevant target_texts will be determined from the input_texts keywords.

    Expected Output:
    1. Successful  Request
    A JSON object with the following structure:
    {
        'input_text': <cleaned input text string>,
        'average_similarity': <float representing average similarity of input text with all target_texts>,
        'similarity': <float representing max similarity of input text with any of the target_texts>,
        'individual_similarity': <list of similarities for each target text>,
        'SortedUrls': <top 5 URLs sorted by relevance based on similarity>
    }

    2. If the `text` field is not provided, is not a list, or is an empty list:
    {
        "error": "Array of strings expected"
    }
    Status Code: 400
    Notes:
    - If target_texts is not provided, the route extracts keywords from the first input text and searches for 
    relevant data, which is then used as the target_texts.
    - The function `clean_texts` is used to preprocess both input_texts and target_texts before calculation.
    - For each input text, the endpoint also returns the top 5 most relevant URLs based on cosine similarity.
    """
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
        clean_target_texts = clean_texts(data['target_texts'])

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
        
        results.append({
            'input_text': input_text,
            'average_similarity': average_similarity,
            'similarity': max_similarity,
            'individual_similarity': individual_similarity,
            'SortedUrls': topNLinks
        })

    return jsonify(results[0])

@app.route('/cosine-similarity-model', methods=['POST'])
def cosine_similarity_model_route(data=None):
    """
    Route: '/cosine-similarity-model'
    Method: POST

    This endpoint calculates the cosine similarity between input texts and a set of target texts. 
    If the target texts are not provided, the route will extract keywords from the input texts and search for relevant data to use as target texts.

    Requirements:
    - The `input_texts` and `target_texts` fields must be provided. Both should be non-empty lists of strings.

    Expected Input:
    - input_texts (list): A list of strings which are the texts for which the cosine similarity needs to be calculated.
    - target_texts (list): A list of target texts against which the cosine similarity is calculated. 
                        If not provided, the route uses the keywords from the input_texts to determine relevant target_texts.

    Expected Output:
    1. Successful Request:
    A list of JSON objects with the following structure for each input text:
    {
        'input_text': <cleaned input text string>,
        'average_similarity': <float representing average similarity of input text with all target_texts>,
        'max_similarity': <float representing max similarity of input text with any of the target_texts>,
        'individual_similarity': <list of similarities for each target text>,
        'SortedUrls': <top 5 URLs sorted by relevance based on similarity>
    }

    2. If the `input_texts` or `target_texts` field is not provided, is not a list, or is an empty list:
    {
        "error": <error message detailing the missing or incorrect data>
    }
    Status Code: 400

    Notes:
    - If target_texts is not provided, the route extracts keywords from the first input text and searches for 
    relevant data, which is then used as the target_texts.
    - The function `clean_texts` is used to preprocess both input_texts and target_texts before calculation.
    - For each input text, the endpoint also returns the top 5 most relevant URLs based on cosine similarity.
    """
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
    """
    Route: '/download-text'
    Method: GET

    This endpoint allows the download of content from a list of URLs using the Common Crawl database. 
    Each URL's data is saved in a separate .warc.gz file.

    Requirements:
    - The `urls` field must be provided and should be a non-empty list of strings representing valid URLs.

    Expected Input:
    - urls (list): A list of URLs from which the data is to be downloaded.

    Expected Output:
    1. Successful Request:
    {
        "message": "Data download completed."
    }

    2. If the `urls` field is not provided, is not a list, or is an empty list:
    {
        "error": <error message detailing the missing or incorrect data>
    }
    Status Code: 400

    3. If errors are encountered during processing:
    {
        "errors": [<list of error messages for each failed URL>]
    }
    Status Code: 500

    Notes:
    - The function uses the Common Crawl database to fetch data related to each URL.
    - If the URL's record is not found in the Common Crawl database (CDX), an error message is added for that URL.
    - For each URL, data is saved in a unique .warc.gz file named in the format "data_<index>.warc.gz", where <index> represents the index of the URL in the list.
    - If any URL fails to be processed, an error message is logged, and the processing continues for the next URL.
    - All encountered errors during processing are aggregated and returned in the `errors` list of the JSON response.
    """

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
    """
    Route: '/find_plagiarism'
    Method: POST

    This endpoint analyzes a given text for potential plagiarism by comparing its content against a set of reference sources. 
    Each comparison returns a similarity score and based on these scores, the system identifies potential sources of plagiarism.

    Requirements:
    - The `text` field must be provided and should be a non-empty string.

    Expected Input:
    - text (string): The content that needs to be checked for potential plagiarism.

    Expected Output:
    1. Successful Request:
    {
        "results": [<list of processed data for each segment of the text>],
        "similarity": <maximum similarity score observed across all segments>,
        "max_similarity": <same as "similarity">,
        "SortedUrls": <top 5 URLs that are most similar to the provided text, sorted by relevance based on similarity>
    }
    Optionally, if there are errors:
    {
        "errors": [<list of error messages>]
    }
    Status Code: 200

    2. If the `text` field is not provided:
    {
        "error": "Text not provided"
    }
    Status Code: 400

    Notes:
    - The given text is first split into segments 3 equal length segments if the text exceeds 150 characters.
    - Each segment is then processed to compute its similarity against reference sources.
    - If any segment's TFIDF similarity exceeds a threshold of 0.3, an enhanced analysis mode is triggered where word2vec is applied to analyze semantic similarity.
    - The endpoint aggregates the results of all segments, computes an average similarity, and identifies the top 5 most similar URLs.
    - Errors encountered during processing are captured and returned in the `errors` field of the response.

    Potential Drawbacks of the Dual-Stage Plagiarism Detection Method:

    1. Dependency on Initial Structural Similarity: The method starts with TFIDF for assessing structural similarity 
                                                    against Google search results. TFIDF, while efficient with word frequencies, 
                                                    can overlook the broader meaning of text. Consequently, a heavily paraphrased 
                                                    text might slip through the initial TFIDF scrutiny even if its content is 
                                                    reminiscent of an existing source.

    2. Sensitivity of word2vec: Word2vec's prowess lies in capturing semantic content. However, its high sensitivity can 
                                sometimes falsely interpret semantic similarity even when sentences or paragraphs differ in 
                                real-world implications. This sensitivity might lead to false positives.

    3. Arbitrary Text Segmentation: Splitting the text into three segments is a somewhat arbitrary decision. While beneficial for 
                                    computational efficiency, it risks losing vital context. This segmentation can alter the essence or 
                                    narrative of lengthier paragraphs, potentially affecting similarity detection's accuracy.

    4. Potential for Contextual Loss: Both TFIDF and word2vec tend to consider words or n-grams within their immediate vicinity, 
                                    possibly overlooking longer narratives or thematic nuances. Two texts might discuss a topic 
                                    from entirely different angles, but due to shared terminology, they might be flagged as similar by this dual-stage method.

    5. Over-reliance on Thresholds: The 0.3 threshold, which activates the enhanced word2vec analysis, is heuristic. 
                                    Depending on the texts' diversity and nature, this threshold could either be overly lenient, 
                                    letting plagiarized content pass, or overly stringent, frequently invoking the more computationally 
                                    intensive word2vec analysis.
    """

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