import animalsData from './animals.json';
import factsData from './facts_clean.json';

// Merge animals with their facts
export function loadAnimalsWithFacts() {
  const factsMap = new Map();
  
  // Create a map of animal names to facts
  factsData.forEach(animal => {
    factsMap.set(animal.name, animal);
  });
  
  // Merge data
  const mergedAnimals = animalsData.map(animal => {
    // animals.json is authoritative if it already has levels
    if (animal.fact_level_1 || animal.fact_level_2) {
      return {
        ...animal,
        fact_level_1: animal.fact_level_1 || animal.fact || "",
        fact_level_2: animal.fact_level_2 || null
      };
    }

    const facts = factsMap.get(animal.name);
    if (facts) {
      return {
        ...animal,
        fact_level_1: facts.fact_level_1 || animal.fact || "",
        fact_level_2: facts.fact_level_2 || null
      };
    }
    // Fallback if no fact found
    return {
      ...animal,
      fact_level_1: animal.fact || "",
      fact_level_2: null
    };
  });
  
  return mergedAnimals;
}

export default loadAnimalsWithFacts();
