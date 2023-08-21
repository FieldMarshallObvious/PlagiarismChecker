import os
import json
import urllib.request
import urllib.parse

def search_google_content(tokens, pages=1):
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")

    # Combine query tokens into one query
    combined_query = " OR ".join(tokens)

    # Encode the text to UTF-8
    try:
        combined_query = combined_query.encode('utf-8')
    except:
        pass

    # URL encode the query
    query = urllib.parse.quote_plus(combined_query)

    # Store all the content
    contents = []

    # Fetch results page by page
    for page in range(pages):
        start_index = 1 + (page * 10)  # Google results start index at 1
        base_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&start={start_index}"
        request = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        results = json.load(response)

        # Extract the content from the results
        try:
            items = results.get('items', [])
            for ele in items:
                content = ele.get('snippet', '')
                link = ele.get('link', '')
                title = ele.get('title', '')
                contents.append({
                    'content': content,
                    'link': link,
                    'title': title
                })
        except:
            return None

    return contents



def query_clean_results(text):
    raw_contents = search_google_content(text)

    if not raw_contents:
        return []

    # Extract all text content using Beautiful soup
    # processed_contents = [extract_content(content) for content in raw_contents]

    return raw_contents