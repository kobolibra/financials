#!/usr/bin/env python3
"""Independently audit a real-ledger adaptive KPI tile in Chromium and WebKit.

This is a machine layout gate, NOT an independent human art-editor signoff.
Uses original source values; only the test's long editorial labels are synthetic.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from editorial_geometry import check_editorial_svg  # noqa: E402
from source_publication_audit import check_vector_source  # noqa: E402
from source_publication import render_exhibit  # noqa: E402

ISSUER, PERIOD = '300394', '20269M'
BASE = ROOT / 'research' / 'issuers' / ISSUER / PERIOD
DEST = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'native-kpi-tile'

INSPECT = r"""
() => {
  const svg = document.querySelector('svg');
  const tiles = [...svg.querySelectorAll('rect[fill="#F6F7F8"]')];
  const textElems = [...svg.querySelectorAll('text[data-kpi-label-line],text[data-exact-value],text[data-delta-label]')];
  const micro = [...svg.querySelectorAll('rect[data-micro-value]')];
  const failures = [];
  const details = [];
  const close = (a,b) => Math.abs(a-b) < 0.2;
  for (const tile of tiles) {
    const x = Number(tile.getAttribute('x'));
    const y = Number(tile.getAttribute('y'));
    const rb = tile.getBoundingClientRect();
    const sameX = el => close(Number(el.getAttribute('x')), x + 14);
    const insideY = el => {
      const py = Number(el.getAttribute('y'));
      return py > y && py < y + Number(tile.getAttribute('height'));
    };
    const ts = textElems.filter(el => sameX(el) && insideY(el));
    const labels = ts.filter(el => el.hasAttribute('data-kpi-label-line'));
    const values = ts.filter(el => el.hasAttribute('data-exact-value'));
    const deltas = ts.filter(el => el.hasAttribute('data-delta-label'));
    const bars = micro.filter(el => close(Number(el.getAttribute('x')), x+14)
       && Number(el.getAttribute('y')) > y
       && Number(el.getAttribute('y')) < y + Number(tile.getAttribute('height')));
    if (!labels.length || values.length !== 1 || deltas.length !== 1 || bars.length !== 2)
      failures.push('MISSING_TILE_COMPONENTS tile-x=' + x);
    for (const el of ts) {
      const b = el.getBoundingClientRect();
      if (b.left < rb.left + 7 || b.right > rb.right - 7) {
        failures.push('TEXT_OVERLAPS_NEIGHBOR tile-x=' + x + ' text=' + el.textContent
          + ' left=' + b.left + ' right=' + b.right + ' tile-right=' + rb.right);
      }
    }
    const bottom = elems => elems.length ? Math.max(...elems.map(el => el.getBoundingClientRect().bottom)) : NaN;
    const top = elems => elems.length ? Math.min(...elems.map(el => el.getBoundingClientRect().top)) : NaN;
    if (labels.length && values.length && bottom(labels) >= top(values) - 3)
      failures.push('LABEL_OVERLAPS_VALUE tile-x=' + x);
    if (values.length && deltas.length && bottom(values) >= top(deltas) - 3)
      failures.push('VALUE_OVERLAPS_DELTA tile-x=' + x);
    if (deltas.length && bars.length && bottom(deltas) >= top(bars) - 3)
      failures.push('DELTA_OVERLAPS_MICROBARS tile-x=' + x);
    details.push({tile_x:x, labels:labels.map(el => el.textContent),
      value:values.map(el => el.textContent), delta:deltas.map(el => el.textContent)});
  }
  if (document.documentElement.scrollWidth > window.innerWidth + 1)
    failures.push('DOCUMENT_HORIZONTAL_OVERFLOW');
  return {viewport:innerWidth, tile_count:tiles.length,
    font_ready:document.fonts.status, details, failures};
}
"""


def main():
    from urllib.parse import quote
    ledger = json.loads((BASE / 'source-ledger.json').read_text())
    pub = json.loads((BASE / 'publication.json').read_text())
    figure = copy.deepcopy(next(f for f in pub['figures'] if f['family'] == 'kpi_board'))
    figure['adaptive_layout'] = 'KPI_TILE_WRAP_V2'
    figure['tiles'][0]['label'] = '本期销售商品和提供劳务收到的全部现金'
    figure['tiles'][1]['label'] = '归属于上市公司普通股股东的净利润'
    figure['tiles'][2]['label'] = 'Accounts Receivable Balance'
    original = ledger['source']['original_bytes_sha256']
    svg = render_exhibit(ledger, figure, True,
                         {'issuer': ISSUER, 'pdf_sha256': original},
                         figure['question'], PERIOD)
    check_editorial_svg(svg, issuer=ISSUER, pdf_sha256=original)
    check_vector_source(svg, ledger)
    DEST.mkdir(parents=True, exist_ok=True)
    style = ('<style>html,body{margin:0;padding:0;overflow-x:hidden;background:#fff}'
             'svg{width:100%;height:auto;display:block}</style>')
    html = '<!doctype html><html lang="zh"><meta charset="utf-8">' + style + '<body>' + svg + '</body></html>'
    report = {'schema': 'financials.kpi_tile_browser_check.v1',
              'issuer': ISSUER, 'period': PERIOD, 'original_pdf_sha256': original,
              'machine_source_and_geometry': 'PASS',
              'independent_human_aesthetic_editor': 'NOT_CHECKED', 'results': []}
    with sync_playwright() as pw:
        for engine in ('chromium', 'webkit'):
            browser = getattr(pw, engine).launch(headless=True)
            try:
                for width in (330, 390):
                    page = browser.new_page(viewport={'width': width, 'height': 900},
                                            device_scale_factor=1)
                    page.set_content(html)
                    page.evaluate('document.fonts.ready')
                    inspected = page.evaluate(INSPECT)
                    result = {'browser': engine, 'width': width, **inspected}
                    screenshot = DEST / f'{engine}-{width}.png'
                    page.screenshot(path=str(screenshot), full_page=True)
                    result['screenshot'] = str(screenshot)
                    report['results'].append(result)
                    print('NATIVE_KPI_TILE_BROWSER', engine, width, inspected['failures'],
                          'tiles', inspected['tile_count'], 'font', inspected['font_ready'])
                    page.close()
            finally:
                browser.close()
    (DEST / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert {(r['browser'], r['width']) for r in report['results']} == {
        ('chromium', 330), ('chromium', 390), ('webkit', 330), ('webkit', 390)}
    for item in report['results']:
        if item['tile_count'] != len(figure['tiles']) or item['font_ready'] != 'loaded' or item['failures']:
            raise SystemExit('NATIVE_KPI_TILE_BROWSER_FAILED: ' + json.dumps(
                item, ensure_ascii=False)[:2000])
    print('NATIVE_KPI_TILE_ALL_BROWSER_AND_SOURCE_GATES_PASS; HUMAN_AESTHETIC_EDITOR_NOT_CHECKED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
