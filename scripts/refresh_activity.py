#!/usr/bin/env python3
"""Snapshot GitHub's unauthenticated contribution calendar; no token required.

Counts come from linked text tooltips, NEVER from colour levels. Fail closed on
missing/duplicate days, unknown tooltip syntax, or a mismatched annual total.
The GitHub public profile may show anonymized private contribution counts; this
is not a count of public commits and cannot prove particular repository work.
Run: python scripts/refresh_activity.py [--as-of YYYY-MM-DD] [--html-dir DIR]
--html-dir reads independently downloaded contributions-YYYY.html for audits.
"""
import argparse
import calendar
from collections import defaultdict
from datetime import date, datetime, timezone, timedelta
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

USER='Jun1188'
START_YEAR=2024

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.cells={}; self.tips={}; self.annual=''; self.target=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and 'data-date' in a:
            if a['id'] in self.cells: raise ValueError('Duplicate cell ID')
            self.cells[a['id']]={'date':a['data-date'],'level':int(a['data-level'])}
        if tag=='tool-tip' and 'for' in a:
            self.target=('tip',a['for']); self.tips[a['for']]=''
        if tag=='h2' and a.get('id')=='js-contribution-activity-description':self.target=('annual',None)
    def handle_data(self,data):
        if self.target:
            kind,key=self.target
            if kind=='tip':self.tips[key]+=data
            else:self.annual+=data
    def handle_endtag(self,tag):
        if self.target and ((tag=='tool-tip' and self.target[0]=='tip') or (tag=='h2' and self.target[0]=='annual')):self.target=None

def parse_year(html,year,as_of):
    p=CalendarParser();p.feed(html)
    annual=re.search(r'([\d,]+)\s+contributions?\s+in\s+'+str(year),p.annual)
    if not annual:raise ValueError(f'{year}: missing annual total')
    rows=[]
    for key,cell in p.cells.items():
        d=date.fromisoformat(cell['date'])
        if d.year!=year:continue
        tip=' '.join(p.tips.get(key,'').split())
        m=re.match(r'^(No|[\d,]+) contributions? on ',tip)
        if not m:raise ValueError(f'{year}: missing/unknown exact count for {cell["date"]}: {tip}')
        count=0 if m[1]=='No' else int(m[1].replace(',',''))
        if not 0<=cell['level']<=4:raise ValueError('Invalid level')
        if count==0 and cell['level']!=0:raise ValueError('Count/level inconsistent')
        rows.append({**cell,'count':count})
    rows.sort(key=lambda x:x['date'])
    end=min(as_of,date(year,12,31)); expected=(end-date(year,1,1)).days+1
    filtered=[r for r in rows if r['date']<=end.isoformat()]
    dates={r['date'] for r in filtered}
    if len(dates)!=expected or len(filtered)!=expected:raise ValueError(f'{year}: incomplete daily data: {len(dates)}/{expected}')
    if any(r['count'] for r in rows if r['date']>as_of.isoformat()):raise ValueError('Unexpected future contributions')
    total=sum(r['count'] for r in filtered)
    if total!=int(annual[1].replace(',','')):raise ValueError(f'{year}: daily sum {total} does not match GitHub annual total {annual[1]}')
    months=[]
    grouped=defaultdict(list)
    for r in filtered:grouped[r['date'][:7]].append(r)
    for month,days in sorted(grouped.items()):
        months.append({'month':month,'count':sum(r['count'] for r in days),'active_days':sum(r['count']>0 for r in days),'days':days,'complete_month':len(days)==calendar.monthrange(year,int(month[-2:]))[1]})
    return {'year':year,'count':total,'active_days':sum(r['count']>0 for r in filtered),'observed_from':f'{year}-01-01','observed_through':end.isoformat(),'daily_data_complete':True,'observed_days':expected,'github_reported_total':int(annual[1].replace(',','')),'months':months}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--as-of',default=date.today().isoformat());ap.add_argument('--html-dir',type=Path);ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'data/github-activity.json');args=ap.parse_args();as_of=date.fromisoformat(args.as_of)
    if as_of>date.today():raise ValueError('Future snapshot not allowed')
    years=[]
    for year in range(START_YEAR,as_of.year+1):
        url=f'https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31'
        if args.html_dir:html=(args.html_dir/f'contributions-{year}.html').read_text()
        else:
            req=urllib.request.Request(url,headers={'User-Agent':'introduce-me-public-calendar-snapshot/1.0','Accept-Language':'en-US'})
            with urllib.request.urlopen(req,timeout=30) as response:html=response.read().decode('utf-8')
        result=parse_year(html,year,as_of);result['source_url']=url;years.append(result)
    active=[{'month':m['month'],'count':m['count'],'active_days':m['active_days']} for y in years for m in y['months'] if m['count']>0]
    active.sort(key=lambda x:(-x['count'],x['month']))
    obj={'schema_version':1,'username':USER,'source':'GitHub public profile contribution calendar (unauthenticated)','profile_url':f'https://github.com/{USER}','as_of':as_of.isoformat(),'retrieved_at':datetime.now(timezone.utc).isoformat(),'metric':'profile_contributions','scope_note_ko':'GitHub 공개 프로필에 표시된 기여 수입니다. 커밋만의 수치가 아니며, 프로필 설정에 따라 익명화된 비공개 기여가 포함될 수 있습니다. 비공개 저장소명이나 내용은 수집하지 않습니다.','display_note_ko':'기여가 0인 월은 생략하고 활동이 많은 월을 먼저 보여줍니다. 월별 비교이며 시간 연속 그래프가 아닙니다.','years':years,'active_months_ranked':active,'omitted_zero_months':[m['month'] for y in years for m in y['months'] if m['count']==0]}
    args.output.parent.mkdir(parents=True,exist_ok=True);tmp=args.output.with_suffix('.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');tmp.replace(args.output)
    print(json.dumps({'as_of':obj['as_of'],'years':[{'year':y['year'],'count':y['count'],'days':y['observed_days']} for y in years],'top_months':active[:6]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
