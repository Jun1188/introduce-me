#!/usr/bin/env python3
"""Render the audited local calendar snapshot into index.html, without runtime fetch."""
from pathlib import Path
from datetime import date
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/github-activity.json').read_text());p=ROOT/'index.html';s=p.read_text()
highlights=re.search(r'<div class="contribution-highlights">.*?</div>',s).group()
months={m['month']:m for y in d['years'] for m in y['months']}
parts=['<section id="activity" class="activity-chapter section wrap"><div class="section-head"><p class="eyebrow">06 / CODE ACTIVITY</p><h2>집중해서 쌓은<br>개발의 기록</h2><p class="activity-intro">기여가 많은 기간을 먼저 살펴보고, 다른 기록은 연도별로 간단히 확인할 수 있습니다.</p></div><div class="active-months">']
for row in d['active_months_ranked'][:3]:
 m=months[row['month']];year,month=map(int,m['month'].split('-'));incomplete='' if m['complete_month'] else f' · {d["as_of"]}까지'
 parts.append(f'<article class="activity-month"><h3>{year}년 {month}월</h3><p class="month-total">{m["count"]:,}회 기여 · 활동 {m["active_days"]}일{incomplete}</p><div class="calendar-weekdays" aria-hidden="true">'+''.join('<span>'+x+'</span>' for x in '일월화수목금토')+'</div><div class="month-calendar">')
 first=date.fromisoformat(m['days'][0]['date']);padding=(first.weekday()+1)%7
 parts.extend(['<span class="pad" aria-hidden="true"></span>']*padding)
 for day in m['days']:
  label=f'{day["date"]}: 기여 {day["count"]}회'
  parts.append(f'<span data-date="{day["date"]}" data-count="{day["count"]}" data-level="{day["level"]}" role="img" aria-label="{label}" title="{label}"></span>')
 parts.append('</div></article>')
parts.append('</div><p class="activity-legend">옅은색 → 진한색: GitHub 기여 단계. 색만으로 기여 수를 추정하지 않으며, 날짜별 수치는 각 칸의 설명으로 제공합니다.</p><p class="activity-source">'+html.escape(d['display_note_ko'])+' 활동 월 안의 빈 날짜는 달력의 흐름을 보존하기 위해 남겼습니다.</p><div class="activity-years">')
for y in reversed(d['years']):
 parts.append(f'<details><summary>{y["year"]}년 · {y["count"]:,}회 기여 · 활동 {y["active_days"]}일</summary><p class="note">집계 범위 {y["observed_from"]} ~ {y["observed_through"]}</p><ul class="year-months">')
 for m in y['months']:
  if m['count']:
   parts.append(f'<li>{int(m["month"].split("-")[1])}월 <strong>{m["count"]:,}회</strong> · {m["active_days"]}일</li>')
 parts.append('</ul></details>')
parts.append('</div><h3>커리어로 이어진 대표 작업</h3>'+highlights+'<p class="activity-source">위 작업은 공개 프로젝트에서 선별했습니다. 잔디의 특정 날짜나 기여 수를 특정 프로젝트의 작업량으로 연결하지 않습니다.</p><p class="activity-source">'+html.escape(d['scope_note_ko'])+f' 집계 기준: {d["as_of"]}. 이 페이지에 저장한 스냅샷이므로 외부 서비스 연결 없이도 표시됩니다. 최신 기록은 아래 원본에서 확인할 수 있습니다.</p><a class="text-link" href="https://github.com/Jun1188">GitHub 공개 프로필 · 활동 대시보드 보기 ↗</a></section>')
block=''.join(parts)
if '<section id="activity"' in s:s=re.sub(r'<section id="activity".*?</section>',block,s,count=1)
else:
 s=re.sub(r'<section class="contribution-card".*?</section>','',s,count=1)
 s=s.replace('<section id="contact"',block+'\n<section id="contact"')
s=s.replace('06 / NEXT CONNECTION','07 / NEXT CONNECTION');p.write_text(s)
