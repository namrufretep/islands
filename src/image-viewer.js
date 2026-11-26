export function createArtworkViewer(){
 const dialog=document.createElement('dialog');
 dialog.className='artwork-viewer';
 dialog.setAttribute('aria-labelledby','artworkViewerTitle');
 dialog.innerHTML='<div class="artwork-viewer-header"><button type="button" class="outline" aria-label="Close enlarged image">Close ×</button><h2 id="artworkViewerTitle"></h2><p>Pinch to zoom · <a target="_blank" rel="noopener">Open original ↗</a></p></div><div class="artwork-viewer-stage"><img alt="" decoding="async"><p role="status" hidden>Image unavailable. Please try again.</p></div>';
 document.body.append(dialog);
 const img=dialog.querySelector('img'),title=dialog.querySelector('h2'),original=dialog.querySelector('a'),error=dialog.querySelector('[role=status]');
 let previousOverflow='';
 img.onerror=()=>{error.hidden=false};
 dialog.querySelector('button').onclick=()=>dialog.close();
 dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
 dialog.addEventListener('close',()=>{
  img.removeAttribute('src');img.alt='';original.removeAttribute('href');error.hidden=true;
  document.body.style.overflow=previousOverflow;
 });
 return edition=>{
  title.textContent=edition.name+' · '+edition.orientation;
  img.alt=edition.name+' '+edition.orientation;error.hidden=true;
  original.href=edition.image;
  if(!dialog.open){previousOverflow=document.body.style.overflow;document.body.style.overflow='hidden';dialog.showModal()}
  img.src=edition.image;
 };
}
