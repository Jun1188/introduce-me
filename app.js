'use strict';
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
let motionOff = reduced.matches;
const motion = document.querySelector('#motion');
function applyMotion(){document.documentElement.classList.toggle('motion-off',motionOff);document.body.classList.toggle('motion-off',motionOff);motion.setAttribute('aria-pressed',String(motionOff));motion.textContent=motionOff?'모션 켜기':'모션 끄기';}
applyMotion();motion.addEventListener('click',()=>{motionOff=!motionOff;applyMotion()});
reduced.addEventListener('change',e=>{motionOff=e.matches;applyMotion()});
for(let i=0;i<80;i++){document.querySelector('.dot-field').append(document.createElement('i'))}
const projects=[...document.querySelectorAll('[data-kind]')];
function selectFilter(button){document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let visible=0;projects.forEach(p=>{p.hidden=button.dataset.filter!=='all'&&p.dataset.kind!==button.dataset.filter;if(!p.hidden)visible++});document.querySelector('#filter-status').textContent=`프로젝트 ${visible}개 표시`; const url=new URL(location.href);if(button.dataset.filter==='all')url.searchParams.delete('category');else url.searchParams.set('category',button.dataset.filter);history.replaceState(null,'',url); }
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>selectFilter(button)));
const initialCategory=new URLSearchParams(location.search).get('category');const initialButton=[...document.querySelectorAll('[data-filter]')].find(b=>b.dataset.filter===initialCategory);if(initialButton)selectFilter(initialButton);
if('IntersectionObserver' in window){const reveals=document.querySelectorAll('.project,.impact article,.timeline article,.tool-list article,.contribution-highlights article,.activity-month');reveals.forEach(x=>x.classList.add('reveal'));document.documentElement.classList.add('js');const ob=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('seen');ob.unobserve(e.target)}}),{threshold:.08});reveals.forEach(x=>ob.observe(x));const scenes=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)document.body.dataset.scene=e.target.id}),{rootMargin:'-25% 0px -45% 0px',threshold:0});document.querySelectorAll('main>section').forEach(x=>scenes.observe(x));}
let ticking=false;function updateProgress(){const max=document.documentElement.scrollHeight-innerHeight;document.querySelector('.scroll-progress').style.width=`${max>0?scrollY/max*100:0}%`;ticking=false;}
addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(updateProgress);ticking=true}},{passive:true});addEventListener('resize',updateProgress);updateProgress();
document.querySelector('#print').addEventListener('click',()=>window.print());




// Direct chapter links reveal their content; ordinary page entry stays collapsed.
function revealLinkedChapter(){
 let hash=location.hash.slice(1);try{hash=decodeURIComponent(hash)}catch{}
 let target=hash?document.getElementById(hash):null;
 if(!target&&new URLSearchParams(location.search).has('category'))target=document.getElementById('work');
 const disclosure=target?.matches('details.chapter-details')?target:target?.querySelector('details.chapter-details');
 if(disclosure)disclosure.open=true;
}
revealLinkedChapter();addEventListener('hashchange',revealLinkedChapter);
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{
 const target=document.getElementById(a.getAttribute('href').slice(1));
 const detail=target?.querySelector('details.chapter-details');if(detail)detail.open=true;
}));
document.querySelectorAll('.chapter-details').forEach(d=>d.addEventListener('toggle',()=>{
 d.querySelector(':scope > summary').textContent=d.open?'세부사항 접기':'세부사항 보기';updateProgress();
}));
let printDisclosureState=[];
addEventListener('beforeprint',()=>{printDisclosureState=[...document.querySelectorAll('.chapter-details')].map(d=>[d,d.open]);printDisclosureState.forEach(([d])=>{d.open=true});});
addEventListener('afterprint',()=>{printDisclosureState.forEach(([d,open])=>{d.open=open});});
