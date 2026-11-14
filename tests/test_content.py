from pathlib import Path
from html.parser import HTMLParser
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids=[];self.links=[];self.images=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if tag=='a':self.links.append(a.get('href',''))
  if tag=='img':self.images.append(a)
  if tag=='h1':self.h1+=1
class Content(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.text=(ROOT/'index.html').read_text();cls.doc=Document();cls.doc.feed(cls.text)
 def test_identity(self):
  hero=self.text.split('<section class="work')[0]
  self.assertIn('게임 개발자 · 컨텐츠 크리에이터',hero);self.assertNotIn('한국공학대학교',hero)
 def test_structure(self):
  self.assertEqual(1,self.doc.h1);self.assertEqual(len(self.doc.ids),len(set(self.doc.ids)))
  for href in self.doc.links:
   if href.startswith('#'):self.assertIn(href[1:],self.doc.ids)
 def test_topics(self):
  for t in ['CS와 메모리','자료구조와 알고리즘','렌더링 파이프라인','게임 개발 지식과 경험','한국공학대학교 게임공학과']:
   self.assertIn(t,self.text)
 def test_preserved(self):
  for t in ['data-filter="all"','data-filter="game"','data-filter="tool"','CoreDawn','모두의 카페','shared-context-public','ai-hub-public']:
   self.assertIn(t,self.text)
 def test_privacy(self):
  for t in ['drive.google.com','135by135by','Interactive_SceneEditer','C:\\Users\\','api_key','ghp_']:
   self.assertNotIn(t,self.text)
 def test_heading_whitespace(self):
  import re
  for heading in re.findall(r'<h[1-6]\b[^>]*>.*?</h[1-6]>',self.text):
   self.assertNotRegex(heading,r'<br>[^\s]')
 def test_chapter_disclosures(self):
  import re
  self.assertEqual(len(re.findall(r'<details class="chapter-details"',self.text)),7)
  self.assertNotRegex(self.text,r'<details class="chapter-details"[^>]*\\bopen')
  activity=self.text.split('<section id="activity"')[1].split('</section>')[0]
  self.assertNotIn('2024',activity)
  for target in ['work','knowledge','creating','community','record','activity','contact']:
   self.assertIn('href="#'+target+'"',self.text.split('<section class="work')[0])
 def test_images(self):
  for i in self.doc.images:self.assertTrue(i.get('alt'));self.assertTrue(i.get('width'));self.assertTrue(i.get('height'))
if __name__=='__main__':unittest.main()

