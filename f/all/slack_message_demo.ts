import * as wmill from "windmill-client"

// adding stuff from VS Code

export async function main(
  slack: RT.Slack,
  channel: string,
  message: string
) {
  const response = await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${slack.token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      channel: channel,
      text: message
    })
  });

  const result = await response.json();
  
  if (!result.ok) {
    throw new Error(`Slack API error: ${result.error}`);
  }
  
  return {
    success: true,
    message: "Message sent successfully",
    timestamp: result.ts,
    channel: result.channel
  };
}
