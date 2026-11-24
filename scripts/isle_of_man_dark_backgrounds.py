from pathlib import Path
import json
import cairosvg
base=Path("public/drafts/000011")
out=base/"dark"
out.mkdir(exist_ok=True)
for edition,old,new,name in [("N","#c8a0a5","#302033","Black Plum"),("S","#b3c9ce","#123b40","Deep Petrol")]:
    stem=f"000011-{edition}-draft"
    svg=(base/(stem+".svg")).read_text()
    assert svg.count(old)==1, "Expected exactly one background color"
    svg=svg.replace(old,new,1)
    (out/(stem+".svg")).write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(out/(stem+".png")),dpi=300,output_width=2048,output_height=2048)
    from PIL import Image
    p=out/(stem+".png")
    with Image.open(p) as im: image=im.copy()
    image.save(p,dpi=(300,300))
    meta=json.loads((base/(stem+".json")).read_text())
    meta.update(background=new,background_name=name,study="Dark background only; original island unchanged")
    (out/(stem+".json")).write_text(json.dumps(meta,indent=2))
