// Import the necessary Slack WebClient from the @slack/web-api package
import { WebClient } from '@slack/web-api';

// Define the Slack resource type
type Slack = {
  token: string
}

// this is modified :)

// Export the main function which sends a message to a Slack channel
export async function main(slack: Slack, channel: string, message: string): Promise<void> {

  // Initialize the Slack WebClient with the provided token
  const webClient = new WebClient(slack.token);

  // Use the chat.postMessage method to send a message to the specified channel
  const result = await webClient.chat.postMessage({
    channel: channel, // The channel ID where the message will be sent
    text: message     // The message text to send
  });

  // Return the result of the message sending operation
  return result;
}