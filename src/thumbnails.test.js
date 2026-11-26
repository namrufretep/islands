import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,statSync} from 'node:fs';
import sharp from 'sharp';

const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const editions=JSON.parse(source.match(/const previewEditions=(.*?);/)[1]);
test('every preview has a bounded gallery thumbnail and retains its full-size original',async()=>{
 for(const edition of editions){
  const thumbnail=new URL(`../public/thumbnails/${edition.id}.webp`,import.meta.url);
  const metadata=await sharp(thumbnail.pathname).metadata();
  assert.equal(metadata.format,'webp');assert.ok(metadata.width<=640);assert.ok(metadata.height<=640);
  const original=new URL('../public'+edition.image,import.meta.url);
  assert.ok(statSync(thumbnail).size<statSync(original).size,edition.id);
  assert.equal((await sharp(original.pathname).metadata()).width,2048);
 }
});
