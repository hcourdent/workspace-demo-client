import requests

def main(num_stories: int) -> list[dict[str, str]]:
    # Define the base URL for the Hacker News API
    base_url = "https://hacker-news.firebaseio.com/v0"

    # Fetch the top stories IDs
    top_stories_url = f"{base_url}/topstories.json"
    response = requests.get(top_stories_url)
    top_stories_ids = response.json()

    # Initialize a list to store the top stories
    top_stories = []

    # Fetch details for the specified number of top stories
    for story_id in top_stories_ids[:num_stories]:
        story_url = f"{base_url}/item/{story_id}.json"
        story_response = requests.get(story_url)
        story_data = story_response.json()
        
        # Append the title and URL of the story to the list
        top_stories.append({
            "title": story_data.get("title", "No Title"),
            "url": story_data.get("url", "No URL")
        })

    return top_stories