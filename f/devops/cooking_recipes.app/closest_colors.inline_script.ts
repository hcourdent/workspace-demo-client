//nobundling

import sharp from 'sharp';

// Define the TailwindCSS color dictionary
const tailwind_colors = {
  "red-500": [239, 68, 68],
  "sky-500": [14, 165, 233],
  "blue-500": [59, 130, 246],
  "cyan-500": [6, 182, 212],
  "teal-500": [20, 184, 166],
  "green-500": [34, 197, 94],
  "orange-500": [249, 115, 22],
  "yellow-300": [253, 224, 71],
  "emerald-500": [16, 185, 129],
};

// Helper function to calculate Euclidean distance between two RGB colors
function calculateColorDistance(color1: [number, number, number], color2: [number, number, number]): number {
  return Math.sqrt(
    Math.pow(color1[0] - color2[0], 2) +
    Math.pow(color1[1] - color2[1], 2) +
    Math.pow(color1[2] - color2[2], 2)
  );
}

// Helper function to find the closest Tailwind color
function findClosestTailwindColor(rgb: [number, number, number]): string {
  let closestColor = "white";
  let minDistance = Infinity;

  for (const [colorName, colorValue] of Object.entries(tailwind_colors)) {
    const distance = calculateColorDistance(rgb, colorValue as [number, number, number]);
    if (distance < minDistance) {
      minDistance = distance;
      closestColor = colorName;
    }
  }

  return closestColor;
}

// Helper function to extract the dominant color from the central region of an image
async function extractDominantColor(imageUrl: string): Promise<[number, number, number]> {
  // Fetch the image data from the URL
  const response = await fetch(imageUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch image: ${response.statusText}`);
  }
  const imageBuffer = await response.arrayBuffer();

  const image = sharp(Buffer.from(imageBuffer));
  const metadata = await image.metadata();

  const { width, height } = metadata;
  if (!width || !height) {
    throw new Error('Unable to retrieve image dimensions');
  }

  // Define the central region (e.g., a 10% square in the center)
  const centerX = width / 2;
  const centerY = height / 2;
  const regionSize = Math.min(width, height) * 0.1;

  // Extract the central region
  const centralRegion = await image
    .extract({
      left: Math.floor(centerX - regionSize / 2),
      top: Math.floor(centerY - regionSize / 2),
      width: Math.floor(regionSize),
      height: Math.floor(regionSize),
    })
    .resize(1, 1) // Resize to 1x1 to get the average color
    .raw()
    .toBuffer();

  // Convert the color to RGB
  const [r, g, b] = centralRegion;

  return [r, g, b];
}

// Main function to fetch and process recipes
export async function main() {
  const response = await fetch('https://api.sampleapis.com/recipes/recipes');
  const recipes = await response.json();

  const results = await Promise.all(recipes.map(async (recipe: { id: number, photoUrl?: string }) => {
    let tailwindColor = "white";

    if (recipe.photoUrl) {
      const dominantColor = await extractDominantColor(recipe.photoUrl);
      tailwindColor = findClosestTailwindColor(dominantColor);
    }

    return {
      id: recipe.id,
      tailwindColor: tailwindColor
    };
  }));

  return results;
}