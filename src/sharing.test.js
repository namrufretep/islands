import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {editionUrl,sharePagePath,xShareUrl,farcasterShareOptions,farcasterShareUrl,farcasterEmbed} from './sharing.js';
import sharp from 'sharp';

const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const editions=JSON.parse(source.match(/const previewEditions=(.*?);/)[1]);
const origin='https://islands-kappa.vercel.app';

test('X composer and app links preserve the chosen orientation and Unicode name',()=>{
 const edition=editions.find(e=>e.id==='000059-S');
 const intent=new URL(xShareUrl(edition,origin));
 assert.equal(intent.origin,'https://x.com');
 assert.equal(intent.pathname,'/intent/tweet');
 assert.equal(intent.searchParams.get('url'),origin+'/share/000059-S.html');
 assert.ok(intent.searchParams.get('text').includes('René-Levasseur Island · South-Up'));
 assert.equal(new URL(editionUrl(edition.id,origin)).searchParams.get('edition'),edition.id);
 assert.throws(()=>sharePagePath('../../unknown'));
});

test('every crawler share page contains the correct existing artwork without JavaScript',()=>{
 for(const edition of editions){
  const html=readFileSync(new URL('../public'+sharePagePath(edition.id),import.meta.url),'utf8');
  assert.ok(html.includes('name="twitter:card" content="summary_large_image"'),edition.id);
  assert.ok(html.includes(`name="twitter:image" content="${origin}${edition.image}"`),edition.id);
  assert.ok(html.includes(`href="${editionUrl(edition.id,origin)}"`),edition.id);
  assert.ok(html.includes(`property="og:url" content="${origin}${sharePagePath(edition.id)}"`));
  assert.ok(readFileSync(new URL('../public'+edition.image,import.meta.url)).length<5_000_000);
  assert.ok(html.includes('not minted or offered for sale'));
 }
});

test('Farcaster native and web composers preserve the selected edition and Unicode text',()=>{
 const edition=editions.find(e=>e.id==='000059-S');
 const options=farcasterShareOptions(edition,origin),intent=new URL(farcasterShareUrl(edition,origin));
 assert.equal(intent.origin,'https://farcaster.xyz');assert.equal(intent.pathname,'/~/compose');
 assert.equal(intent.searchParams.get('text'),options.text);
 assert.ok(options.text.includes('René-Levasseur Island · South-Up'));
 assert.deepEqual(intent.searchParams.getAll('embeds[]'),options.embeds);
 assert.deepEqual(options.embeds,[origin+'/share/000059-S.html']);
});

test('every Farcaster embed has a complete 3:2 image and opens its own N/S edition',async()=>{
 const decode=value=>value.replaceAll('&quot;','"').replaceAll('&#39;',"'").replaceAll('&lt;','<').replaceAll('&gt;','>').replaceAll('&amp;','&');
 for(const edition of editions){
  const html=readFileSync(new URL('../public'+sharePagePath(edition.id),import.meta.url),'utf8');
  const embed=JSON.parse(decode(html.match(/name="fc:miniapp" content="([^"]+)"/)[1]));
  assert.deepEqual(embed,farcasterEmbed(edition,origin));
  assert.equal(embed.button.action.type,'launch_miniapp');
  assert.equal(new URL(embed.button.action.url).searchParams.get('edition'),edition.id);
  const image=readFileSync(new URL('../public'+new URL(embed.imageUrl).pathname,import.meta.url));
  const metadata=await sharp(image).metadata();
  assert.equal(metadata.width,1200);assert.equal(metadata.height,800);assert.ok(image.length<10_000_000);
 }
});
