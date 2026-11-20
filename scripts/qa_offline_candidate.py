#!/usr/bin/env python3
"""Exercise standalone source dossiers in a real offline browser and retain each exhibit."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree
import json
import shutil

from playwright.sync_api import sync_playwright


def audit(html, out, engine, widths, executable=None):
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        executable = executable or (shutil.which('chromium') if engine == 'chromium' else None)
        browser = getattr(playwright, engine).launch(executable_path=executable)
        receipt = {'browser': engine, 'version': browser.version, 'sha256': sha256(html.read_bytes()).hexdigest(), 'viewports': []}
        for width in widths:
            context = browser.new_context(viewport={'width': width, 'height': 950}, offline=True, accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(html.resolve().as_uri(), wait_until='load')
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width} document overflow'
            assert page.locator('h1').inner_text()
            assert page.locator('figure[data-editorial-role=primary]').count() == 1
            page.screenshot(path=out / f'{width}-full.png', full_page=True, animations='disabled')
            figures = []
            for figure in page.locator('figure').all():
                name = figure.get_attribute('id')
                svg = figure.locator('svg:visible')
                assert svg.count() == 1, (width, name, 'visible SVG')
                findings = svg.evaluate("""s => {
                  const rect = s.getBoundingClientRect(), texts = Array.from(s.querySelectorAll('text'));
                  return {issues: texts.filter(t => {
                    const p=t.getBoundingClientRect();
                    return (p.left<rect.left-1 || p.right>rect.right+1 ||
                      p.top<rect.top-1 || p.bottom>rect.bottom+1 ||
                      Number(getComputedStyle(t).fontSize.replace('px','')) * rect.width / s.viewBox.baseVal.width < 10);
                  }).map(t=>t.textContent), overlap: texts.flatMap((a,i) => {
                    const u=a.getBoundingClientRect();
                    return texts.slice(i+1).filter(b => {
                      const v=b.getBoundingClientRect();
                      return Math.min(u.right,v.right)-Math.max(u.left,v.left)>2 &&
                        Math.min(u.bottom,v.bottom)-Math.max(u.top,v.top)>3;
                    }).map(b=>[a.textContent,b.textContent]);
                  }), values: Array.from(s.querySelectorAll('[data-exact-value],[data-signed-yuan]')).map(n=>({
                    period:n.dataset.period, value:n.dataset.exactValue ?? n.dataset.signedYuan,
                    min:n.dataset.domainMin, max:n.dataset.domainMax, source:n.dataset.sourceReference,
                    width:Number(n.getAttribute('width')), scale:n.dataset.scaleYuanPerUnit,
                    before:n.dataset.beforeYuan, after:n.dataset.afterYuan
                  }))};
                }""")
                assert not findings['issues'] and not findings['overlap'], (width, name, findings)
                assert findings['values'], (width, name, 'source values')
                for value in findings['values']:
                    assert value['source'], (name, value)
                    if value.get('min') is not None:
                        span = float(value['max']) - float(value['min'])
                        expected = abs(float(value['value'])) * (298 if width <= 850 else 480) / span if span else 0
                        assert abs(expected - value['width']) < 1e-5, (name, value, expected)
                    elif value.get('scale') and value['scale'] != 'ZERO_ONLY':
                        expected = abs(float(value['after']) - float(value['before'])) / float(value['scale'])
                        assert abs(expected - value['width']) < 1e-5, (name, value, expected)
                figure.screenshot(path=out / f'{width}-{name}.png', animations='disabled')
                with page.expect_download() as event:
                    figure.locator('button[data-export]').click()
                path = out / f'{width}-{name}.svg'
                event.value.save_as(path)
                doc = ElementTree.parse(path).getroot()
                assert doc.get('data-original-pdf-sha256') == svg.get_attribute('data-original-pdf-sha256')
                figures.append({'id': name, 'role': figure.get_attribute('data-editorial-role'), **findings})
            assert not errors, errors
            receipt['viewports'].append({'width': width, 'figures': figures})
            context.close()
        browser.close()
    (out / 'browser.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--engine', default='chromium', choices=('chromium', 'webkit'))
    parser.add_argument('--executable')
    args = parser.parse_args()
    audit(args.html, args.out, args.engine, (1440, 768, 390) if args.engine == 'chromium' else (375,), args.executable)
