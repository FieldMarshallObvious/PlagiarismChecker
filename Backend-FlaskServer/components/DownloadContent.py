import requests
import json
from functools import lru_cache
from bs4 import BeautifulSoup

@lru_cache(maxsize=None)
def get_latest_index():
    """
    Retrieve the latest CDX (Common Data eXchange) index endpoint from Common Crawl's collection info.

    This function is memoized using an LRU cache for performance optimization.

    Returns:
    - str: The endpoint URL for the latest CDX index.
    - None: In case of request error or inability to fetch the index.
    """
    cdx_url = "http://index.commoncrawl.org/collinfo.json"
    try:
        colls = requests.get(cdx_url).json()
        return colls[0]['cdx-api']
    except requests.RequestException:
        print("Error fetching the latest index.")
        return None

def get_cdx_records(url, limit=1):
    """
    Get the latest CDX (Common Data eXchange) record for a given URL using a remote index service.

    Parameters:
    - url (str): The target URL for which the CDX records are fetched.
    - limit (int, optional): The maximum number of records to fetch. Defaults to 1.

    Returns:
    - dict: The latest CDX record for the provided URL, parsed from JSON.
    - None: If no record is found, an error occurs, or the latest index isn't available.
    """
    latest_index = get_latest_index()
    if not latest_index:
        return None
    
    params = {
        "url": url,
        "output": "json",
        "limit": limit
    }

    try:
        response = requests.get(latest_index, params=params)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.
        records = [json.loads(line) for line in response.content.strip().split(b"\n")]
        return records[0] if records else None
    except requests.RequestException:
        print(f"Error fetching CDX records for {url}.")
        return None


def download_common_crawl_data(record, out_file):
    """
    Download a WARC record from Common Crawl based on the CDX record and save it to an output file.

    Parameters:
    - record (dict): CDX record with 'offset', 'length', and 'filename'.
    - out_file (str): File path to save the WARC record.
    """
    offset, length = int(record['offset']), int(record['length'])
    warc_url = record['filename']

    headers = {
        "Range": f"bytes={offset}-{offset+length-1}"
    }

    response = requests.get(f"https://commoncrawl.s3.amazonaws.com/{warc_url}", headers=headers)

    with open(out_file, "wb") as f:
        f.write(response.content)

if __name__ == "__main__":
    target_url = "https://www.example.com/"  # Replace with your URL
    records = get_cdx_records(target_url)

    if records:
        first_record = records[0]
        download_common_crawl_data(first_record, "data.warc.gz")
        print(f"Data saved to data.warc.gz")
    else:
        print(f"No data found for {target_url}")

def get_text_from_link(url):
    """
    Fetch and extract textual content from the given URL, specifically from the <p> tags.

    Parameters:
    - url (str): The target URL to extract text from.

    Returns:
    - str: Extracted text from the provided URL.
    """
        
    # Fetch the content from the URL
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract text from the page
    # Here we're considering all the text inside <p> tags, but you can adjust based on your requirements.
    paragraphs = soup.find_all('p')
    text = ' '.join(paragraph.text for paragraph in paragraphs)

    return text
