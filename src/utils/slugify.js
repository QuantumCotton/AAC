/**
 * Convert animal names to URL-friendly slugs
 * Example: "Red-Eyed Tree Frog" -> "red_eyed_tree_frog"
 */
export function slugify(name) {
  return name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters except spaces and hyphens
    .replace(/\s+/g, '_')     // Replace spaces with underscores
    .replace(/-+/g, '_')      // Replace hyphens with underscores
    .replace(/^_+|_+$/g, ''); // Remove leading/trailing underscores
}

/**
 * Generate asset paths for an animal
 */
export function getAssetPaths(animalId) {
  return {
    toyImage: `/assets/images/toy_mode/${animalId}.webp`,
    realImage: `/assets/images/real_mode/${animalId}.webp`,
    nameAudio: `/assets/audio/names/${animalId}_name.mp3`,
    factAudioSimple: `/assets/audio/facts/${animalId}_fact_simple.mp3`,
    factAudioDetailed: `/assets/audio/facts/${animalId}_fact_detailed.mp3`,
    factAudioLegacy: `/assets/audio/facts/${animalId}_fact.mp3`,
    phonicsAudio: `/assets/audio/phonics/letter_${animalId.charAt(0).toUpperCase()}.mp3`
  };
}
