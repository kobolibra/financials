#!/usr/bin/env python3
"""Exercise standalone source dossiers in a real offline browser and retain each exhibit."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree
import json
import shutil
from time import sleep
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright


# Match the explicit production-lock HTTP request contract: Python's default
# urllib User-Agent can receive a different CDN/edge response from a real browser.
# Keep exact original-byte comparison: alternate HTML is NEVER accepted as PASS.
RELEASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; OriginalFinancePreviewReleaseQA/1.0)',
    'Cache-Control': 'no-cache',
    'Accept': 'text/html,*/*',
}


def verify_remote_bytes(url, expected, *, retries=30, interval_seconds=5, observations=None):
    """Fail closed on exact bytes, recording what the edge returned each try."""
    observations = [] if observations is None else observations
    wanted = sha256(expected).hexdigest()
    for number in range(1, retries + 1):
        row = {'attempt': number}
        try:
            request = Request(url, headers=RELEASE_HEADERS)
            with urlopen(request, timeout=15) as response:
                data = response.read()
                status = response.status
                row.update(http_status=status, actual_sha256=sha256(data).hexdigest(),
                           actual_bytes=len(data), content_type=response.headers.get('Content-Type'),
                           cache_status=response.headers.get('CF-Cache-Status'))
                if status == 200 and data == expected:
                    row['result'] = 'PASS_EXACT_BYTES'
                    observations.append(row)
                    return row
                row['result'] = 'MISMATCH'
        except Exception as exc:
            row['error'] = f'{type(exc).__name__}: {exc}'
            row['result'] = 'FETCH_FAILED'
        observations.append(row)
        print('RELEASE_EXACT_BYTE_PREFLIGHT_PENDING',
              url, number, 'expected_sha256=' + wanted, row, flush=True)
        if number < retries:
            sleep(interval_seconds)
    raise ValueError(f'RELEASE_HTML_BYTES_MISMATCH {url} expected_sha256={wanted} '
                     f'expected_bytes={len(expected)} last_observation={observations[-1]}')


def audit(html, out, engine, widths, executable=None, origin=None):
    out.mkdir(parents=True, exist_ok=True)
    if origin:
        homepage = html.parent / 'index.html'
        route = '/' + html.name
        preflight = {'schema': 'financials.catalog_exact_live_bytes.v1',
                     'origin': origin, 'checks': []}
        for remote, local in (('/', homepage), (route, html)):
            events = []
            target = origin + remote
            expected = local.read_bytes()
            row = {'route': remote, 'expected_sha256': sha256(expected).hexdigest(),
                   'expected_bytes': len(expected), 'observations': events}
            preflight['checks'].append(row)
            try:
                verify_remote_bytes(target, expected, observations=events)
                row['result'] = 'PASS_EXACT_BYTES'
            except Exception:
                row['result'] = 'FAIL_CLOSED'
                raise
            finally:
                # Keep a machine-readable receipt even when CDN bytes mismatch.
                (out / 'release-byte-preflight.json').write_text(
                    json.dumps(preflight, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf8')
    with sync_playwright() as playwright:
        executable = executable or (shutil.which('chromium') if engine == 'chromium' else None)
        browser = getattr(playwright, engine).launch(executable_path=executable)
        receipt = {'browser': engine, 'version': browser.version, 'sha256': sha256(html.read_bytes()).hexdigest(), 'viewports': []}
        for width in widths:
            context = browser.new_context(viewport={'width': width, 'height': 950}, offline=origin is None and engine != 'webkit', accept_downloads=True)
            if origin is None and engine == 'webkit':
                # WebKit blocks file: navigations in offline mode on macOS.
                # Permit the local document while denying every HTTP(S) request.
                context.route('http**/*', lambda route: route.abort())
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            if origin:
                page.goto(origin + '/', wait_until='load')
                page.locator(f'a[href="{route}"]').first.click()
                assert page.url in (origin + route, origin + route.removesuffix('.html')), page.url
            else:
                page.goto(html.resolve().as_uri(), wait_until='load')
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width} document overflow'
            assert page.locator('h1').inner_text()
            visible_copy = page.locator('main').inner_text()
            for marker in ('核对意见类型', 'TODO', '待填写'):
                if marker in visible_copy:
                    raise ValueError('READER_VISIBLE_AUTHOR_NOTE ' + marker)
            for figure in page.locator('figure').all():
                question = figure.locator('.figure-head h2').inner_text()
                svg = figure.locator('svg:visible')
                if (svg.get_attribute('data-scale-policy') == 'INDEPENDENT_PER_PAIR'
                        and '多少' in question and '转成' in question):
                    raise ValueError('UNSUPPORTED_CONVERSION_QUESTION ' + question)
            assert page.locator('figure[data-editorial-role=primary]').count() == 1
            page.screenshot(path=out / f'{width}-full.png', full_page=True, animations='disabled')
            figures = []
            for figure in page.locator('figure').all():
                name = figure.get_attribute('id')
                svg = figure.locator('svg:visible')
                assert svg.count() == 1, (width, name, 'visible SVG')
                findings = svg.evaluate("""s => {
                  const rect = s.getBoundingClientRect(), texts = Array.from(s.querySelectorAll('text'));
                  const points = [...s.querySelectorAll('circle[data-ratio-role]')];
                  const pointLabelOverlap = points.flatMap(point => {
                    const p = point.getBoundingClientRect();
                    return texts.filter(t => {
                      const r = t.getBoundingClientRect();
                      const x = (p.left + p.right) / 2, y = (p.top + p.bottom) / 2;
                      const dx = x - Math.max(r.left, Math.min(x, r.right));
                      const dy = y - Math.max(r.top, Math.min(y, r.bottom));
                      return Math.hypot(dx, dy) < p.width / 2;
                    }).map(t => [point.dataset.ratioRole, t.textContent]);
                  });
                  return {pointLabelOverlap, issues: texts.filter(t => {
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
                  }), values: Array.from(s.querySelectorAll('[data-exact-value],[data-signed-yuan],[data-exact-percent-value],[data-node-yuan],[data-exact-yuan],[data-chain-node-yuan],[data-chain-leaf-yuan]')).map(n=>({
                    period:n.dataset.period, value:n.dataset.exactValue ?? n.dataset.signedYuan ?? n.dataset.exactPercentValue ?? n.dataset.nodeYuan ?? n.dataset.exactYuan ?? n.dataset.chainNodeYuan ?? n.dataset.chainLeafYuan,
                    min:n.dataset.domainMin, max:n.dataset.domainMax, source:n.dataset.sourceReference ?? n.dataset.valueReference ?? n.dataset.ratioReference ?? n.dataset.nodeId ?? n.dataset.chainTerms ?? n.dataset.chainLeaf,
                    width:Number(n.getAttribute('width')), scale:n.dataset.scaleYuanPerUnit,
                    before:n.dataset.beforeYuan, after:n.dataset.afterYuan,
                    stock_role:n.dataset.stockRole
                  }))};
                }""")
                assert not findings['pointLabelOverlap'], ('RATIO_POINT_OVER_LABEL', width, name, findings['pointLabelOverlap'])
                assert not findings['issues'] and not findings['overlap'], (width, name, findings)
                assert findings['values'], (width, name, 'source values')
                for value in findings['values']:
                    assert value['source'], (name, value)
                    if value.get('min') is not None:
                        span = float(value['max']) - float(value['min'])
                        expected = abs(float(value['value'])) * (298 if width <= 850 else 480) / span if span else 0
                        assert abs(expected - value['width']) < 1e-5, (name, value, expected)
                    elif value.get('scale') and value['scale'] != 'ZERO_ONLY':
                        # A money bridge scales a before/after delta. A balance
                        # stock scales its exact yuan amount, not an invented
                        # before/after flow. Both are fail-closed and audited
                        # again independently in editorial_geometry.py.
                        scale = float(value['scale'])
                        assert scale > 0, (name, value, 'nonpositive yuan/px')
                        if value.get('before') is not None and value.get('after') is not None:
                            expected = abs(float(value['after']) - float(value['before'])) / scale
                        elif value.get('stock_role') in ('assets', 'liabilities', 'equity'):
                            expected = float(value['value']) / scale
                            assert expected >= 0, (name, value, 'negative stock')
                        else:
                            raise ValueError('UNPROVEN_FINANCIAL_SCALE_SOURCE ' + str((name, value)))
                        assert abs(expected - value['width']) < 1e-5, (name, value, expected)
                figure.screenshot(path=out / f'{width}-{name}.png', animations='disabled')
                with page.expect_download() as event:
                    figure.locator('button[data-export]').click()
                path = out / f'{width}-{name}.svg'
                event.value.save_as(path)
                doc = ElementTree.parse(path).getroot()
                assert doc.get('data-original-pdf-sha256') == svg.get_attribute('data-original-pdf-sha256')
                assert path.read_text() == svg.evaluate('s => new XMLSerializer().serializeToString(s)')
                if doc.get('data-dossier-profit-chain') == 'true':
                    import sys
                    shared = str(Path(__file__).resolve().parents[1] / 'research/shared')
                    if shared not in sys.path:
                        sys.path.insert(0, shared)
                    from source_publication_audit import check_vector_source
                    ledger = json.loads(page.locator('#ledger-data').text_content())
                    check_vector_source(path.read_text(), ledger)
                figures.append({'id': name, 'role': figure.get_attribute('data-editorial-role'), **findings})
            view = {'width': width, 'figures': figures}
            if origin:
                view['article_url'] = page.url
                page.locator('header a[href="/#companies"]').click()
                assert page.url == origin + '/#companies', page.url
                view['directory_url'] = page.url
                page.screenshot(path=out / f'{width}-directory.png', animations='disabled')
            assert not errors, errors
            receipt['viewports'].append(view)
            context.close()
        browser.close()
    (out / 'browser.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--engine', default='chromium', choices=('chromium', 'webkit'))
    parser.add_argument('--executable')
    parser.add_argument('--origin', help='HTTP site whose homepage and report must match checked-in bytes')
    args = parser.parse_args()
    audit(args.html, args.out, args.engine, (1440, 768, 390) if args.engine == 'chromium' else (375,), args.executable, args.origin.rstrip('/') if args.origin else None)
