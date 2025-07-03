export async function main(url: string) {
  if (!url) {
    throw new Error('URL is required');
  }
  
  try {
    // Fetch the content from the URL
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const content = await response.text();
    
    // Basic HTML content extraction - remove scripts, styles, and get text content
    const cleanContent = content
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    
    return {
      url: url,
      content: cleanContent,
      contentLength: cleanContent.length,
      originalLength: content.length
    };
  } catch (error) {
    throw new Error(`Failed to fetch content from ${url}: ${error.message}`);
  }
}