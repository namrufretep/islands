import sharp from 'sharp';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const svg=(width,height,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}"><rect width="100%" height="100%" fill="#ff2a16"/>${body}</svg>`;
await sharp(Buffer.from(svg(1024,1024,'<path d="M512 150 844 512 512 874 180 512Z" fill="none" stroke="#092b1c" stroke-width="24"/><text x="512" y="566" fill="#092b1c" font-family="monospace" font-size="160" font-weight="bold" text-anchor="middle">I</text>'))).png().toFile(root+'public/icon.png');
await sharp(Buffer.from(svg(1200,800,'<path d="M50 680 420 70 840 720 1150 120M40 220 1160 630M120 730 1060 60" stroke="#103321" opacity=".22" stroke-width="3" fill="none"/><text x="600" y="370" fill="#092b1c" font-family="monospace" font-size="160" font-weight="bold" text-anchor="middle">ISLANDS</text><text x="600" y="470" fill="#092b1c" font-family="monospace" font-size="35" font-weight="bold" text-anchor="middle">COLLECT THE WORLD</text><text x="600" y="660" fill="#092b1c" font-family="monospace" font-size="26" text-anchor="middle">ATLAS · INDEX · COLLECTION</text>'))).png().toFile(root+'public/app-preview.png');
console.log('Prepared app icon and Farcaster launch preview.');
