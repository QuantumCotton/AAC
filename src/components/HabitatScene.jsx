import React from 'react';
import HabitatBook from './HabitatBook';

export default function HabitatScene({ selectedHabitat, onAnnounceHabitat }) {
  return <HabitatBook habitat={selectedHabitat} onAnnounceHabitat={onAnnounceHabitat} />;
}
