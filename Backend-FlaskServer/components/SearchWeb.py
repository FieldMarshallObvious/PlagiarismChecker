import os
import json
import urllib.request
import urllib.parse

def search_google_content(tokens, pages=1):
    """
    Search for content from Google Custom Search Engine (CSE) based on the provided query tokens.

    This function uses Google's CSE API to fetch search results, constructs the search query using 
    the provided tokens, and fetches the specified number of pages of search results. The results 
    are then parsed to extract relevant information.

    Parameters:
    - tokens (list of str): List of keywords to form the search query.
    - pages (int, optional): Number of search result pages to fetch. Defaults to 1.

    Returns:
    - list of dict: List of search results where each result is represented by a dictionary 
                    containing the content, link, and title of the search result. 
                    An example of the returned item:
                    {
                        'content': 'This is a snippet of the search result.',
                        'link': 'https://www.example.com',
                        'title': 'Example Title'
                    }
    - None: In case of an error while parsing or fetching results.

    Environment Variables:
    - GOOGLE_API_KEY: The API key for accessing Google CSE.
    - GOOGLE_CSE_ID: The Custom Search Engine ID.

    Notes:
    - Google CSE API provides up to 10 results per page, so the start index for each page is calculated accordingly.
    - The function assumes that the necessary modules (os, urllib, json) have been imported.
    """
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
    """
    Query the Google Custom Search Engine (CSE) and obtain the raw contents based on the provided text.

    This function is a simple wrapper around the `search_google_content` function. It fetches raw search 
    results for the given text. If no results are found or an error occurs, it returns an empty list.

    Parameters:
    - text (str): The text or query to search for.

    Returns:
    - list of dict: List of search results where each result is represented by a dictionary containing 
                    the content, link, and title of the search result. 
                    An example of the returned item:
                    {
                        'content': 'This is a snippet of the search result.',
                        'link': 'https://www.example.com',
                        'title': 'Example Title'
                    }
    - []: An empty list if no results are found or in case of an error.

    Notes:
    - The function leverages the `search_google_content` function to perform the actual query.
    """
    raw_contents = search_google_content(text)

    if not raw_contents:
        return []

    return raw_contents