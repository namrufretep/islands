import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';
import {editionUrl, sharePagePath, xShareUrl, farcasterShareUrl, farcasterEmbed} from '../src/sharing.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = readFileSync(`${root}src/main.js`, 'utf8');
const editions = JSON.parse(source.match(/const previewEditions=(.*?);/)[1]);
const origin = new URL(process.env.ISLANDS_PUBLIC_URL || 'https://islands-kappa.vercel.app').origin;
const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
mkdirSync(`${root}public/share`, {recursive:true});
mkdirSync(`${root}public/share-images`, {recursive:true});
for (const edition of editions) {
  const title = `${edition.name} · ${edition.orientation} | ISLANDS`;
  const description = `${edition.mood} · Soft Stone island artwork. Preview edition ${edition.id}; not minted or offered for sale.`;
  const image = new URL(edition.image, origin).href;
  const url = new URL(sharePagePath(edition.id), origin).href;
  const alt = `${edition.name}, ${edition.orientation}, ${edition.mood}`;
  const metadata = JSON.parse(readFileSync(`${root}public${edition.image.replace(/\.png$/, '.json')}`, 'utf8'));
  const embed = farcasterEmbed(edition, origin);
  const legacyEmbed = {...embed, button: {...embed.button, action: {...embed.button.action, type:'launch_frame'}}};
  const background = typeof metadata.background==='string' && /^#[\da-f]{6}$/i.test(metadata.background) ? metadata.background : '#102323';
  // Preserve the entire square original, centered in Farcaster's 3:2 canvas.
  await sharp(`${root}public${edition.image}`).resize({width:1200,height:800,fit:'contain',background}).png().toFile(`${root}public/share-images/${edition.id}.png`);
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escape(title)}</title><meta name="description" content="${escape(description)}">
<link rel="canonical" href="${escape(url)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="ISLANDS">
<meta property="og:title" content="${escape(title)}"><meta property="og:description" content="${escape(description)}">
<meta property="og:url" content="${escape(url)}"><meta property="og:image" content="${escape(image)}">
<meta property="og:image:width" content="2048"><meta property="og:image:height" content="2048"><meta property="og:image:alt" content="${escape(alt)}">
<meta name="fc:miniapp" content="${escape(JSON.stringify(embed))}"><meta name="fc:frame" content="${escape(JSON.stringify(legacyEmbed))}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${escape(title)}">
<meta name="twitter:description" content="${escape(description)}"><meta name="twitter:image" content="${escape(image)}"><meta name="twitter:image:alt" content="${escape(alt)}">
<style>body{margin:0;background:#102323;color:#eee9d8;font:16px/1.6 system-ui,sans-serif}main{max-width:720px;margin:0 auto;padding:32px 20px}img{width:100%;height:auto;display:block;border-radius:12px}h1{font-size:2rem;line-height:1.2}a{color:inherit}nav{display:flex;gap:14px;flex-wrap:wrap;margin:24px 0}nav a{border:1px solid #92a59c;border-radius:8px;padding:10px 16px;text-decoration:none}small{display:block;opacity:.75;overflow-wrap:anywhere}</style>
</head><body><main><p>◈ ISLANDS · ${escape(edition.id)}</p><h1>${escape(edition.name)}</h1>
<p>${escape(edition.orientation)} · ${escape(edition.mood)}</p><img src="${escape(image)}" alt="${escape(alt)}" width="2048" height="2048">
<p>Artwork preview · not minted or offered for sale.</p>
<nav><a href="${escape(editionUrl(edition.id, origin))}">Explore this island</a><a href="${escape(xShareUrl(edition, origin))}" target="_blank" rel="noopener noreferrer">Share on X ↗</a><a href="${escape(farcasterShareUrl(edition, origin))}" target="_blank" rel="noopener noreferrer">Share on Farcaster ↗</a></nav>
<small>${escape(metadata.attribution || '')}</small></main></body></html>`;
  writeFileSync(`${root}public${sharePagePath(edition.id)}`, html);
}
console.log(`Built ${editions.length} artwork share pages with image metadata.`);
