import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
OUT=Path('test-results');OUT.mkdir(exist_ok=True)
URL=os.environ.get('BASE_URL','http://127.0.0.1:8000')
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in [1440,768,390,320]:
  context=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,has_touch=width<500)
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(URL);expect(page.locator('h1')).to_be_visible()
  assert page.locator('.hero-identity').inner_text().startswith('게임 개발자 · 콘텐츠 크리에이터')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  for section in ['knowledge','creating','community','record','contact']:
   page.locator('#'+section).scroll_into_view_if_needed();expect(page.locator('#'+section+' h2')).to_be_visible()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  for category,count in [('game',2),('tool',4),('all',6)]:
   page.locator(f'[data-filter="{category}"]').click()
   expect(page.locator('[data-kind]:visible')).to_have_count(count)
   expect(page.locator(f'[data-filter="{category}"]')).to_have_attribute('aria-pressed','true')
   expect(page.locator('#knowledge')).to_be_visible()
  page.goto(URL+'/?category=tool#work');expect(page.locator('[data-kind]:visible')).to_have_count(4)
  page.locator('[data-filter="all"]').click()
  # Disclosure repetition must stay stable, and keyboard operation must work.
  detail=page.locator('.project-main details');summary=detail.locator('summary')
  summary.focus();page.keyboard.press('Enter');expect(detail).to_have_attribute('open','')
  page.keyboard.press('Enter');expect(detail).not_to_have_attribute('open','')
  page.locator('#motion').click();expect(page.locator('body')).to_have_class('motion-off')
  assert page.locator('html').evaluate('(e)=>getComputedStyle(e).scrollBehavior')=='auto'
  page.locator('#motion').click();expect(page.locator('body')).not_to_have_class('motion-off')
  page.evaluate('document.querySelectorAll(".reveal").forEach(el=>el.classList.add("seen"))')
  page.screenshot(path=str(OUT/f'full-{width}.png'),full_page=True)
  page.locator('#home').scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'hero-{width}.png'))
  page.locator('#knowledge').scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'knowledge-{width}.png'))
  assert not errors,errors
  results.append({'width':width,'status':'passed'});context.close()
 # The external chart is optional; a failed service must not block the portfolio.
 context=browser.new_context(viewport={'width':390,'height':844})
 context.route('https://ghchart.rshah.org/**',lambda route:route.abort())
 page=context.new_page();page.goto(URL);page.locator('#contact').scroll_into_view_if_needed()
 expect(page.locator('#contribution-status')).to_contain_text('불러오지 못했습니다')
 expect(page.locator('.contribution-card a')).to_be_visible()
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 context.close()
 context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
 page=context.new_page();page.goto(URL)
 expect(page.locator('[data-kind]:visible')).to_have_count(6)
 expect(page.locator('#knowledge h2')).to_be_visible()
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 context.close()
 context=browser.new_context(reduced_motion='reduce');page=context.new_page();page.goto(URL)
 expect(page.locator('body')).to_have_class('motion-off')
 assert page.locator('html').evaluate('(e)=>getComputedStyle(e).scrollBehavior')=='auto'
 page.keyboard.press('Tab');expect(page.locator('.skip')).to_be_focused()
 context.close();browser.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print('All viewport, navigation, filter, disclosure, motion and no-JavaScript checks passed.')
