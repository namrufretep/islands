export function sharePagePath(id) {
  if (!/^\d{6}-[NS]$/.test(id)) throw new Error('Invalid artwork edition');
  return `/share/${id}.html`;
}

export function editionUrl(id, origin) {
  sharePagePath(id);
  const url = new URL('/', origin);
  url.searchParams.set('edition', id);
  return url.href;
}

export function xShareUrl(edition, origin) {
  const intent = new URL('https://x.com/intent/tweet');
  intent.searchParams.set('text', `${edition.name} · ${edition.orientation}\n${edition.mood}\n\nDiscover ISLANDS — collect the world, one island at a time. Artwork preview.`);
  intent.searchParams.set('url', new URL(sharePagePath(edition.id), origin).href);
  return intent.href;
}
