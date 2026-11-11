const el=id=>document.getElementById(id);
el('translate').addEventListener('click',async()=>{
 el('status').textContent='Processing…';el('output').value='';el('warnings').textContent='';
 try{
 const response=await fetch('/api/translate',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':el('key').value},body:JSON.stringify({source:el('source').value,target_language:el('language').value,target_platform:el('platform').value})});
 const data=await response.json();if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:'Request rejected');
 el('output').value=data.output;el('status').textContent=data.status;
 const list=document.createElement('ul');for(const warning of data.warnings){const li=document.createElement('li');li.textContent=warning;list.append(li)}el('warnings').replaceChildren(list);
 }catch(e){el('status').textContent='Error: '+e.message}
});
el('copy').addEventListener('click',async()=>{if(el('output').value){await navigator.clipboard.writeText(el('output').value);el('status').textContent='Output copied.'}});
