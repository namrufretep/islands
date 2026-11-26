import sharp from 'sharp';
import {readFileSync,mkdirSync,existsSync,statSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('../',import.meta.url));
const source=readFileSync(`${root}src/main.js`,'utf8');
const editions=JSON.parse(source.match(/const previewEditions=(.*?);/)[1]);
mkdirSync(`${root}public/thumbnails`,{recursive:true});
// Keep the original files untouched. Gallery images have a bounded decode size.
for(const edition of editions){
 const original=`${root}public${edition.image}`;
 const target=`${root}public/thumbnails/${edition.id}.webp`;
 if(existsSync(target)&&statSync(target).mtimeMs>=statSync(original).mtimeMs)continue;
 await sharp(original).resize({width:640,height:640,fit:'inside',withoutEnlargement:true}).webp({quality:88}).toFile(target);
}
console.log(`Prepared ${editions.length} gallery thumbnails (maximum 640px).`);
