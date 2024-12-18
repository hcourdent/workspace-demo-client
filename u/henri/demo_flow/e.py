import requests
from bs4 import BeautifulSoup

def main(url: str) -> str:
    # Send a GET request to the specified URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all text from the page
        text = soup.get_text()
        
        # Split the text into words
        words = text.split()
        
        # Get the first 300 words
        first_300_words = ' '.join(words[:300])
        
        return first_300_words
    else:
        # Return an error message if the request was not successful
        return f"Failed to retrieve the page. Status code: {response.status_code}"