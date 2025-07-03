export async function main(
  title: string,
  url: string,
  by: string,
  score: number
) {
  return {
    title: title,
    summary: "Yet another blog post",
    url: url,
    by: by,
    score: score,
    originalContentLength: 0,
    truncatedContentLength: 0,
    tokensUsed: 0
  };
}