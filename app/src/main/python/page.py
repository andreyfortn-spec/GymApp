HTML = r"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Gym Log</title>
<style>
:root{--ink:#1B1F27;--paper:#ECEDEF;--card:#fff;--plate:#D7263D;--steel:#7B8494;--line:#D5D8DE}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,Roboto,sans-serif;padding-bottom:110px}
header{background:var(--ink);color:#fff;padding:22px 18px 16px;position:sticky;top:0;z-index:5}
header h1{margin:0;font-size:28px;font-weight:900;letter-spacing:-.02em}
header p{margin:4px 0 0;color:#AAB1BF;font-size:14px}
main{padding:14px;display:grid;gap:14px}
.ex{background:var(--card);border-radius:6px;border-left:8px solid var(--plate);overflow:hidden}
.ex-head{display:flex;align-items:center;padding:14px 8px 10px 14px}
.ex-head h2{flex:1;margin:0;font-size:20px;font-weight:800}
.set{display:flex;align-items:baseline;width:100%;border:0;background:none;text-align:left;font:inherit;color:inherit;padding:12px 14px;border-top:1px solid var(--line)}
.set:active{background:#F3F4F6}
.set .n{width:28px;color:var(--steel);font-variant-numeric:tabular-nums}
.set .v{font-size:19px;font-weight:700;font-variant-numeric:tabular-nums}
.set .v small{font-weight:500;color:var(--steel);font-size:14px}
.add{display:block;width:100%;border:0;border-top:1px solid var(--line);background:none;padding:13px 14px;text-align:left;font:inherit;font-weight:700;color:var(--plate)}
.icon{border:0;background:none;color:var(--steel);font-size:20px;padding:8px 12px}
.empty{padding:40px 10px;text-align:center;color:var(--steel);line-height:1.5}
.fab{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom));background:var(--plate);color:#fff;border:0;border-radius:6px;padding:16px 22px;font:inherit;font-weight:800;font-size:17px;box-shadow:0 6px 16px rgba(0,0,0,.25)}
dialog{border:0;border-radius:10px 10px 0 0;padding:20px;width:100%;max-width:100%;margin:auto 0 0;color:var(--ink)}
dialog::backdrop{background:rgba(27,31,39,.55)}
dialog h3{margin:0 0 14px;font-size:20px}
label{display:block;font-size:14px;color:var(--steel);margin-bottom:12px}
input{display:block;width:100%;margin-top:4px;padding:12px;font:inherit;font-size:18px;border:2px solid var(--line);border-radius:6px;color:var(--ink)}
input:focus{outline:none;border-color:var(--ink)}
.row{display:flex;gap:10px;margin-top:6px}
.row button{flex:1;padding:14px;border-radius:6px;border:0;font:inherit;font-weight:800;font-size:16px}
.save{background:var(--ink);color:#fff}.del{background:#fff;color:var(--plate);border:2px solid var(--plate)!important}
.err{color:var(--plate);font-size:14px;min-height:18px;margin:0 0 8px}
</style>
</head>
<body>
<header><h1>Gym Log</h1><p id="sub"></p></header>
<main id="list"></main>
<button class="fab" id="addEx">+ Упражнение</button>
<dialog id="dlg"><h3 id="dt"></h3><div id="fields"></div><p class="err" id="err"></p>
<div class="row"><button class="del" id="bd">Удалить</button><button class="save" id="bs">Сохранить</button></div></dialog>
<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function api(path,opt={}){
  const r=await fetch(path,{headers:{'Content-Type':'application/json'},...opt});
  const body=await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(typeof body.detail==='string'?body.detail:'Ошибка '+r.status);
  return body;
}
let data=[];
async function load(){data=await api('/exercise');render()}
function fmtW(w){return w==null?'<small>без веса</small>':w+' <small>кг</small>'}
function render(){
  const total=data.reduce((a,e)=>a+e.sets.length,0);
  $('sub').textContent=data.length?`${data.length} упр. · ${total} подх.`:'Пока пусто';
  if(!data.length){$('list').innerHTML='<div class="empty">Нет упражнений.<br>Нажмите «+ Упражнение», чтобы начать.</div>';return}
  $('list').innerHTML=data.map(e=>`<section class="ex">
    <div class="ex-head"><h2>${esc(e.name)}</h2><button class="icon" data-act="rename" data-id="${e.id}">✎</button></div>
    ${e.sets.map((s,i)=>`<button class="set" data-act="set" data-id="${s.id}"><span class="n">${i+1}</span><span class="v">${s.reps} <small>повт. ×</small> ${fmtW(s.weight)}</span></button>`).join('')}
    <button class="add" data-act="addset" data-id="${e.id}">+ Подход</button></section>`).join('');
}
function ask({title,fields,onSave,onDelete}){
  $('dt').textContent=title;$('err').textContent='';
  $('fields').innerHTML=fields.map(f=>`<label>${f.label}<input id="f_${f.id}" type="${f.type||'text'}" ${f.type==='number'?'inputmode="decimal" step="any"':''} value="${esc(f.value??'')}"></label>`).join('');
  $('bd').style.display=onDelete?'':'none';
  const get=()=>Object.fromEntries(fields.map(f=>[f.id,$('f_'+f.id).value.trim()]));
  const run=fn=>async()=>{try{await fn(get());$('dlg').close();await load()}catch(e){$('err').textContent=e.message}};
  $('bs').onclick=run(onSave);$('bd').onclick=onDelete?run(onDelete):null;
  $('dlg').showModal();
}
const num=v=>v===''?null:Number(v.replace(',','.'));
function setFields(s={}){return[{id:'reps',label:'Повторения',type:'number',value:s.reps},{id:'weight',label:'Вес, кг (необязательно)',type:'number',value:s.weight}]}
$('addEx').onclick=()=>ask({title:'Новое упражнение',fields:[{id:'name',label:'Название'}],
  onSave:async v=>{if(!v.name)throw new Error('Введите название');await api('/exercise',{method:'POST',body:JSON.stringify({name:v.name})})}});
$('list').onclick=ev=>{
  const b=ev.target.closest('[data-act]');if(!b)return;const id=b.dataset.id;
  if(b.dataset.act==='rename'){const e=data.find(x=>x.id===id);
    ask({title:'Упражнение',fields:[{id:'name',label:'Название',value:e.name}],
      onSave:async v=>{if(!v.name)throw new Error('Введите название');await api('/exercise/'+id,{method:'PATCH',body:JSON.stringify({name:v.name})})},
      onDelete:async()=>{await api('/exercise/'+id,{method:'DELETE'})}})}
  if(b.dataset.act==='addset')ask({title:'Новый подход',fields:setFields(),
    onSave:async v=>{if(!v.reps)throw new Error('Укажите повторения');await api(`/exercise/${id}/sets`,{method:'POST',body:JSON.stringify({reps:parseInt(v.reps),weight:num(v.weight)})})}});
  if(b.dataset.act==='set'){const s=data.flatMap(e=>e.sets).find(x=>x.id===id);
    ask({title:'Подход',fields:setFields(s),
      onSave:async v=>{if(!v.reps)throw new Error('Укажите повторения');await api('/set/'+id,{method:'PATCH',body:JSON.stringify({reps:parseInt(v.reps),weight:num(v.weight)})})},
      onDelete:async()=>{await api('/set/'+id,{method:'DELETE'})}})}
};
load().catch(e=>{$('list').innerHTML='<div class="empty">'+esc(e.message)+'</div>'});
</script>
</body>
</html>
"""
