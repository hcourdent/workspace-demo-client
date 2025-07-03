export async function main() {
  // Fetch HackerNews top stories
  const response = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
  const topStoryIds = await response.json();
  
  // Get the top 5 story IDs
  const top5StoryIds = topStoryIds.slice(0, 5);
  
  // Fetch details for all top 5 stories
  const stories = [];
  for (const storyId of top5StoryIds) {
    const storyResponse = await fetch(`https://hacker-news.firebaseio.com/v0/item/${storyId}.json`);
    const story = await storyResponse.json();
    
    // Only include stories that have URLs (some might be text posts)
    if (story.url) {
      stories.push({
        id: story.id,
        title: story.title,
        url: story.url,
        score: story.score,
        by: story.by,
        time: story.time
      });
    }
  }
  
  return stories;
}