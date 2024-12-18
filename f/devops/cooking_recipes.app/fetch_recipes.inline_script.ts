export async function main(selected_cuisine: string = 'All') { // Default parameter set to 'All' if undefined or empty
  const getData = async (cuisine: string): Promise<any[]> => {
    const resp = await fetch('https://api.sampleapis.com/recipes/recipes');
    const json = await resp.json();
    // Filter out objects where "calories", "cookingTime", or "photoUrl" are empty
    // Additionally, filter by "cuisine" if "selected_cuisine" is not "All"
    return json.filter((item: any) =>
      item.calories !== '' &&
      item.cookingTime !== '' &&
      item.photoUrl !== '' &&
      (cuisine === 'All' || item.cuisine === cuisine)
    );
  }

  const effectiveCuisine = selected_cuisine || 'All';
  const data = await getData(effectiveCuisine);
  return data;
}