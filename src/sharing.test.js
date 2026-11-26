import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {editionUrl,sharePagePath,xShareUrl} from './sharing.js';

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
