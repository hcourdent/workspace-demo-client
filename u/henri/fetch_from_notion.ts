type Notion = {
  token: string
}

export async function main(notion: Notion, databaseId: string): Promise<any> {
  const databaseUrl = `https://api.notion.com/v1/databases/${databaseId}/query`;

  // Set up the request headers
  const headers = {
    'Authorization': `Bearer ${notion.token}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  };

  try {
    const response = await fetch(databaseUrl, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Notion database: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    return data;
  } catch (error) {
    console.error('Error fetching Notion database:', error);
    throw error;
  }
}