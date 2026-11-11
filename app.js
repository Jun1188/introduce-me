'use strict';
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
let motionOff = reduced.matches;
const motion = document.querySelector('#motion');
function applyMotion(){document.body.classList.toggle('motion-off',motionOff);motion.setAttribute('aria-pressed',String(motionOff));motion.textContent=motionOff?'모션 켜기':'모션 끄기';}
applyMotion();motion.addEventListener('click',()=>{motionOff=!motionOff;applyMotion()});
reduced.addEventListener('change',e=>{motionOff=e.matches;applyMotion()});
for(let i=0;i<80;i++){document.querySelector('.dot-field').append(document.createElement('i'))}
const projects=[...document.querySelectorAll('[data-kind]')];
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let visible=0;projects.forEach(p=>{p.hidden=button.dataset.filter!=='all'&&p.dataset.kind!==button.dataset.filter;if(!p.hidden)visible++});document.querySelector('#filter-status').textContent=`프로젝트 ${visible}개 표시`; }));
if('IntersectionObserver' in window){const reveals=document.querySelectorAll('.project,.impact article,.timeline article,.tool-list article');reveals.forEach(x=>x.classList.add('reveal'));document.documentElement.classList.add('js');const ob=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('seen');ob.unobserve(e.target)}}),{threshold:.08});reveals.forEach(x=>ob.observe(x));const scenes=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)document.body.dataset.scene=e.target.id}),{rootMargin:'-25% 0px -45% 0px',threshold:0});document.querySelectorAll('main>section').forEach(x=>scenes.observe(x));}
let ticking=false;function updateProgress(){const max=document.documentElement.scrollHeight-innerHeight;document.querySelector('.scroll-progress').style.width=`${max>0?scrollY/max*100:0}%`;ticking=false;}
addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(updateProgress);ticking=true}},{passive:true});addEventListener('resize',updateProgress);updateProgress();
document.querySelector('#print').addEventListener('click',()=>window.print());
