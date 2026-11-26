import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {editionUrl} from '../src/sharing.js';

const root=fileURLToPath(new URL('../',import.meta.url));
const source=readFileSync(`${root}src/main.js`,'utf8');
const editions=JSON.parse(source.match(/const previewEditions=(.*?);/)[1]);
const traits=JSON.parse(source.match(/const draftTraits=(.*?);/)[1]);
const registry=JSON.parse(source.match(/const registry=(.*?);/)[1]);
const origin=new URL(process.env.ISLANDS_PUBLIC_URL||'https://islands-kappa.vercel.app').origin;
const creator='0xfc5708cb64604dcf6f62de5d63a051ed577e10c1';
const directory=`${root}public/nft`;mkdirSync(directory,{recursive:true});
const write=(name,value)=>writeFileSync(`${directory}/${name}.json`,JSON.stringify(value,null,2)+'\n');
const manifest=[];
for(const edition of editions){
 const art=JSON.parse(readFileSync(`${root}public${edition.image.replace(/\.png$/,'.json')}`,'utf8'));
 const imageHash=createHash('sha256').update(readFileSync(`${root}public${edition.image}`)).digest('hex');
 const t=traits[edition.name],country=registry.find(r=>r[0]===edition.name)?.[1];
 const values={'Island ID':edition.islandId,'Artwork ID':edition.id,'Island':edition.name,'Country':country,'Region':t[0],'Island Type':t[1],'Water Type':t[2],'Ocean':t[3],'Water Body':t[4],'Largest Settlement':t[9],'Orientation':edition.orientation,'Color Palette':edition.mood,'Color Family':t[5+(edition.id.endsWith('-S')?1:0)],'Background':art.background_name||t[7+(edition.id.endsWith('-S')?1:0)],'Area (km²)':art.area_km2,'Scale':art.artwork_print_scale_denominator?`1:${Math.round(art.artwork_print_scale_denominator)}`:null};
 const attributes=Object.entries(values).filter(([,value])=>value!==undefined&&value!==null).map(([trait_type,value])=>({trait_type,value}));
 write(edition.id,{name:`ISLANDS #${edition.id} · ${edition.name}`,description:`${edition.name} · ${edition.orientation}. A Soft Stone island artwork based on physical shoreline and elevation data. Artistic relief; approximate geographic scale. ${art.attribution||''}`,image:new URL(edition.image,origin).href,external_url:editionUrl(edition.id,origin),attributes,properties:{artwork_sha256:imageHash,canvas_px:2048,dpi:300}});
 manifest.push({artwork_id:edition.id,metadata_uri:`${origin}/nft/${edition.id}.json`,image_sha256:imageHash});
}
write('collection',{name:'ISLANDS',description:'Collect the world, one island at a time. Geographic Soft Stone artworks in individually designed North-Up and South-Up orientations.',image:new URL(editions[0].image,origin).href,external_link:origin,seller_fee_basis_points:1000,fee_recipient:creator});
// This catalog prepares URIs; it is not released mint inventory or token-ID allocation.
write('manifest',{release_status:'not_released',preferred_creator_fee_bps:1000,preferred_creator_fee_recipient:creator,creator_fee_enforcement:'not_configured',editions:manifest});
console.log(`Prepared ${manifest.length} NFT metadata documents and collection metadata.`);
