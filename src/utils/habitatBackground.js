export function habitatSlug(name) {
  return (name || '')
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '_')
    .replace(/-+/g, '_')
    .replace(/^_+|_+$/g, '');
}

export function getHabitatBackgroundStyle(habitatName, mode) {
  const slug = habitatSlug(habitatName);

  const habitatTints = {
    farm: { base: '#D9F99D', accent: '#16A34A' },
    domestic: { base: '#FEF08A', accent: '#F59E0B' },
    forest: { base: '#BBF7D0', accent: '#059669' },
    jungle: { base: '#A7F3D0', accent: '#16A34A' },
    nocturnal: { base: '#E9D5FF', accent: '#7C3AED' },
    arctic: { base: '#BFDBFE', accent: '#2563EB' },
    shallow_water: { base: '#A5F3FC', accent: '#0891B2' },
    coral_reef: { base: '#BAE6FD', accent: '#0284C7' },
    deep_sea: { base: '#CBD5E1', accent: '#334155' },
    ultra_deep_sea: { base: '#E2E8F0', accent: '#0F172A' }
  };

  const tint = habitatTints[slug] || { base: '#E2E8F0', accent: '#334155' };

  const kidOverlay = `linear-gradient(135deg, rgba(255, 255, 255, 0.35), ${tint.base}CC)`;
  const eduOverlay = `linear-gradient(135deg, rgba(15, 23, 42, 0.10), rgba(226, 232, 240, 0.90))`;

  const overlay = mode === 'education' ? eduOverlay : kidOverlay;

  const pattern =
    slug === 'forest'
      ? `radial-gradient(circle at 20% 30%, ${tint.accent}22 0 18px, transparent 19px),
         radial-gradient(circle at 70% 20%, ${tint.accent}18 0 22px, transparent 23px),
         radial-gradient(circle at 40% 80%, ${tint.accent}1A 0 26px, transparent 27px),
         repeating-linear-gradient(90deg, ${tint.accent}10 0 10px, transparent 10px 26px)`
      : `radial-gradient(circle at 25% 25%, ${tint.accent}14 0 14px, transparent 15px),
         radial-gradient(circle at 75% 35%, ${tint.accent}12 0 18px, transparent 19px),
         repeating-linear-gradient(45deg, ${tint.accent}0E 0 10px, transparent 10px 26px)`;

  const imageUrl = `/assets/backgrounds/${slug}.webp`;

  return {
    backgroundColor: tint.base,
    backgroundImage: `${overlay}, ${pattern}, url('${imageUrl}')`,
    backgroundSize: `cover, 220px 220px, 320px 320px`,
    backgroundPosition: `center, center, center`,
    backgroundRepeat: `no-repeat, repeat, repeat`
  };
}
