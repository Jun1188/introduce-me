"""Offline regression checks for the public-calendar snapshot."""
import json
from pathlib import Path
import unittest
from datetime import date,timedelta

DATA=json.loads((Path(__file__).resolve().parents[1]/'data/github-activity.json').read_text())
class ActivitySnapshotTests(unittest.TestCase):
 def test_source_and_scope(self):
  self.assertEqual(DATA['username'],'Jun1188')
  self.assertEqual(DATA['metric'],'profile_contributions')
  self.assertIn('비공개 기여',DATA['scope_note_ko'])
  for y in DATA['years']:self.assertTrue(y['source_url'].startswith('https://github.com/users/Jun1188/contributions?'))
 def test_daily_completeness(self):
  for y in DATA['years']:
   rows=[d for m in y['months'] for d in m['days']]
   start=date.fromisoformat(y['observed_from']);end=date.fromisoformat(y['observed_through'])
   self.assertEqual([d['date'] for d in rows],[(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)])
   self.assertEqual(len(rows),y['observed_days'])
   self.assertEqual(sum(d['count'] for d in rows),y['github_reported_total'])
   self.assertEqual(y['count'],y['github_reported_total'])
   self.assertTrue(all(isinstance(d['count'],int) and d['count']>=0 and 0<=d['level']<=4 for d in rows))
 def test_months_and_ranking(self):
  active=[];omitted=[]
  for y in DATA['years']:
   for m in y['months']:
    self.assertEqual(m['count'],sum(d['count'] for d in m['days']))
    self.assertEqual(m['active_days'],sum(d['count']>0 for d in m['days']))
    self.assertTrue(all(d['date'].startswith(m['month']) for d in m['days']))
    if m['count']:active.append({'month':m['month'],'count':m['count'],'active_days':m['active_days']})
    else:omitted.append(m['month'])
  active.sort(key=lambda x:(-x['count'],x['month']))
  self.assertEqual(DATA['active_months_ranked'],active)
  self.assertEqual(DATA['omitted_zero_months'],omitted)
if __name__=='__main__':unittest.main()
