"""Draft artwork renderer. Requires explicitly reviewed coastline metadata."""
import argparse, json, hashlib, random, math
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
import io

p=argparse.ArgumentParser()
p.add_argument('coastline',type=Path)
p.add_argument('metadata',type=Path)
p.add_argument('output',type=Path)
a=p.parse_args()
meta=json.loads(a.metadata.read_text())
if meta.get('status')!='verified_coastline':
    raise SystemExit('Coastline must be reviewed and approved before rendering.')
raw=a.coastline.read_bytes()
if meta.get('svg_sha256')!=hashlib.sha256(raw).hexdigest():
    raise SystemExit('Coastline checksum mismatch')
path=ET.fromstring(raw).find('{http://www.w3.org/2000/svg}path').attrib['d']
from xml.sax.saxutils import quoteattr
d=quoteattr(path)
a.output.mkdir(parents=True,exist_ok=True)
palette=['#145764','#278c99','#61c8c9','#afe5df','#edf7f5']
for edition,angle in [('N',0),('S',180)]:
    rng=random.Random(meta['id']+edition+'glacial-turquoise-v1')
    shapes=[]
    # Broad asymmetric patches, no internal strokes or contour bands.
    # Coordinates are composition guides, not geographic terrain measurements.
    patches=[
        ('#145764','M 0 0 L 690 0 C 660 260 490 430 515 650 C 540 820 380 960 490 1180 C 600 1360 780 1420 850 2048 L 0 2048 Z'),
        ('#278c99','M 0 1530 C 340 1320 540 1390 710 1500 C 900 1650 1130 1530 1390 1430 C 1640 1340 1850 1430 2048 1250 L 2048 2048 L 0 2048 Z'),
        ('#0c3541','M 0 1240 C 330 1250 370 1470 580 1560 C 800 1690 920 1720 960 2048 L 0 2048 Z'),
        ('#afe5df','M 1050 0 L 2048 0 L 2048 910 C 1840 830 1720 650 1560 620 C 1430 610 1430 460 1320 390 C 1150 300 1190 160 1050 0 Z'),
        ('#edf7f5','M 1530 0 L 2048 0 L 2048 540 C 1880 510 1810 370 1680 330 C 1590 270 1600 130 1530 0 Z'),
    ]
    for color,curve in patches:
        transform='' if edition=='N' else 'transform="translate(2048 0) scale(-1 1) rotate(12 1024 1024)"'
        shapes.append(f'<path d="{curve}" fill="{color}" {transform}/>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs><radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="url(#bg)"/>
<g clip-path="url(#coast)"><rect width="2048" height="2048" fill="#61c8c9"/>{''.join(shapes)}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="#080b0d" stroke-width="13" stroke-linejoin="round"/>
</svg>'''
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':'Glacial Turquoise','art_status':'experimental_draft','terrain_guided':False},indent=2))
