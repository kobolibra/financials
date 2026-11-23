"""Publish an authored source-fact dossier through shared financial grammars.

No issuer-name switches, inferred missing facts, or hardcoded reporting period.
The dossier supplies research questions and explicit exact source expressions.
"""
from pathlib import Path
from decimal import Decimal as D
from html import escape as H
import hashlib,json,re,sys
from editorial_bridge import render_product_economics,render_bridge,render_comparison,render_balance,render_components
from source_income_adapter import render_sector_income,compile_disclosed_income
from dossier_profit_chain import build as build_profit_chain
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text())
def fact_of(ledger,key):
    """A fact of this dossier, or of a declared external dossier written 'alias:key'."""
    if ':' in key:
        alias,name=key.split(':',1)
        return ledger['_external'][alias]['facts'][name]
    return ledger['facts'][key]
def amount(ledger,expr):
    if isinstance(expr,str):return D(fact_of(ledger,expr)['yuan'])
    if not isinstance(expr,list) or not expr:raise ValueError('EXPLICIT_FACT_EXPRESSION_REQUIRED')
    return sum((D(str(coef))*D(fact_of(ledger,key)['yuan']) for key,coef in expr),D(0))
def with_externals(ledger,story,root=None):
    """Attach declared sibling dossiers (read-only) for cross-period claims.

    The attached copy is only used to evaluate claims; it never enters the
    published ledger. Each external dossier is pinned by issuer, fiscal period and
    original PDF SHA, so a changed source cannot silently change a published number.
    """
    specs=story.get('external_ledgers',{})
    if not specs:return ledger
    root=root or ROOT;external={}
    if not isinstance(specs,dict):raise ValueError('DOSSIER_EXTERNAL_LEDGERS_INVALID')
    for alias,spec in specs.items():
        if not re.fullmatch('[a-z][a-z0-9]*',alias):raise ValueError('DOSSIER_EXTERNAL_ALIAS_INVALID')
        path=(root/spec['path']).resolve();path.relative_to(root.resolve())
        other=json.loads(path.read_text())
        if (other['issuer']['code']!=ledger['issuer']['code'] or other['issuer']['fiscal_period']!=spec['period']
            or other['source']['original_bytes_sha256']!=spec['pdf_sha256'] or other['issuer']['fiscal_period']==ledger['issuer']['fiscal_period']):
            raise ValueError('DOSSIER_EXTERNAL_LEDGER_IDENTITY '+alias)
        external[alias]=other
    return {**ledger,'_external':external}
CROSS_PERIOD='CUMULATIVE_FLOW_DIFFERENCE_SAME_FISCAL_YEAR'
SAME_DATE='SAME_DATE_STOCK_RECONCILIATION'
CITATION='SINGLE_EXTERNAL_REPORT_CITATION'
YOY='YOY_OF_SAME_FISCAL_YEAR_DIFFERENCES'
def check_cross_period_claims(ledger,story):
    """Claims that read another report period must declare the lawful mode and obey it.

    CUMULATIVE_FLOW_DIFFERENCE_SAME_FISCAL_YEAR: disclosed consolidated flows of ONE fiscal year
    (e.g. nine months minus first quarter). SAME_DATE_STOCK_RECONCILIATION: disclosed consolidated
    stocks that share one balance date, used to compare what two reports say about that date.
    SINGLE_EXTERNAL_REPORT_CITATION: a value or ratio computed entirely inside one other report.
    """
    lg=with_externals(ledger,story)
    def keys_of(spec):
        out=[]
        for part in (spec.get('expression'),spec.get('denominator'),(spec.get('times') or {}).get('expression'),(spec.get('times') or {}).get('denominator')):
            if part is None:continue
            out+=[part] if isinstance(part,str) else [k for k,c in part]
        return out
    specs=dict(story.get('quantified_claims',{}))
    for fig in story.get('figures',[]):
        for j,col in enumerate(fig.get('columns',[])):
            # every figure value that reads another report must also declare its lawful mode
            specs['figure:'+fig['id']+':'+str(j)]={'expression':col['value'],**({'cross_period':col['cross_period']} if col.get('cross_period') else {})}
    for name,spec in specs.items():
        keys=keys_of(spec);mode=spec.get('cross_period')
        if not any(':' in k for k in keys):
            if mode:raise ValueError('DOSSIER_CROSS_PERIOD_DECLARED_WITHOUT_EXTERNAL_FACT '+name)
            continue
        if mode not in (CROSS_PERIOD,SAME_DATE,CITATION,YOY):raise ValueError('DOSSIER_CROSS_PERIOD_CLAIM_NOT_DECLARED '+name)
        facts=[fact_of(lg,k) for k in keys]
        if any(f['scope']!='consolidated' or f['classification']!='DISCLOSED' for f in facts):raise ValueError('DOSSIER_CROSS_PERIOD_ONLY_DISCLOSED_CONSOLIDATED_FACTS '+name)
        if mode==CROSS_PERIOD:
            if any(f['type']!='flow' for f in facts) or len({f['period'][:4] for f in facts})!=1:raise ValueError('DOSSIER_CROSS_PERIOD_MIXED_FISCAL_YEARS_OR_NONFLOW '+name)
        elif mode==YOY:
            # (current-year quantity - prior-year quantity) / prior-year quantity, each built inside ONE fiscal year
            if any(f['type']!='flow' for f in facts):raise ValueError('DOSSIER_YOY_NONFLOW '+name)
            den=spec.get('denominator');expr=spec['expression']
            if not isinstance(den,list) or not isinstance(expr,list):raise ValueError('DOSSIER_YOY_REQUIRES_EXPLICIT_TERMS '+name)
            year=lambda k:fact_of(lg,k)['period'][:4]
            prior_years={year(k) for k,c in den}
            if len(prior_years)!=1:raise ValueError('DOSSIER_YOY_PRIOR_NOT_ONE_YEAR '+name)
            py=prior_years.pop();cur=[(k,c) for k,c in expr if year(k)!=py];old=[(k,c) for k,c in expr if year(k)==py]
            if sorted((k,-D(str(c))) for k,c in old)!=sorted((k,D(str(c))) for k,c in den):raise ValueError('DOSSIER_YOY_PRIOR_PART_MUST_EQUAL_DENOMINATOR '+name)
            if len({year(k) for k,c in cur})!=1 or int(year(cur[0][0]))!=int(py)+1:raise ValueError('DOSSIER_YOY_CURRENT_NOT_NEXT_YEAR '+name)
        elif mode==SAME_DATE:
            if any(f['type']!='stock' for f in facts) or len({f['period'] for f in facts})!=1:raise ValueError('DOSSIER_CROSS_PERIOD_STOCKS_MUST_SHARE_ONE_DATE '+name)
        else:
            # Citation: every operand comes from ONE external report, so the arithmetic is
            # exactly what that report's own validated ledger supports (flows of one year, or stocks of one date).
            if any(':' not in k for k in keys) or len({k.split(':',1)[0] for k in keys})!=1:raise ValueError('DOSSIER_CITATION_MUST_USE_ONE_EXTERNAL_REPORT '+name)
            other=lg['_external'][keys[0].split(':',1)[0]]['issuer']
            own={other['fiscal_period'],other['comparative_period']}|set(other.get('flow_columns',{}).values())
            if len({f['type'] for f in facts})!=1 or (facts[0]['type']=='flow' and not {f['period'] for f in facts}<=own):
                raise ValueError('DOSSIER_CITATION_MIXED_TYPES_OR_PERIODS '+name)
        for k in keys:
            if ':' in k and k.split(':',1)[0] not in story['external_ledgers']:raise ValueError('DOSSIER_CROSS_PERIOD_UNKNOWN_ALIAS '+name)
def reference(expr):return expr if isinstance(expr,str) else json.dumps(expr,separators=(',',':'),ensure_ascii=False)
def dependencies(expr):return [expr] if isinstance(expr,str) else [k for k,c in expr]
def signed_bridge_checkpoints(ledger, figure):
    """Verify disclosed subtotals against cumulative signed source rows."""
    checkpoints = figure.get('source_checkpoints', {})
    if not checkpoints:
        return set()
    rows = figure['rows']
    start = rows[0]
    if start[2] != 'start':
        raise ValueError('SIGNED_BRIDGE_CHECKPOINT_REQUIRES_START')
    total = amount(ledger, start[1])
    proven = set()
    for index, (_, expression, role) in enumerate(rows[1:-1], 1):
        if role != 'step':
            raise ValueError('SIGNED_BRIDGE_CHECKPOINT_REQUIRES_STEPS')
        total += amount(ledger, expression)
        key = checkpoints.get(str(index))
        if key is not None:
            fact = fact_of(ledger, key)
            if (fact['type'] != 'flow' or fact['scope'] != 'consolidated'
                    or fact['classification'] != 'DISCLOSED'
                    or fact['period'] != ledger['issuer']['fiscal_period']
                    or amount(ledger, key) != total or key in proven):
                raise ValueError('SIGNED_BRIDGE_CHECKPOINT_DRIFT ' + key)
            proven.add(key)
    if len(proven) != len(checkpoints):
        raise ValueError('SIGNED_BRIDGE_CHECKPOINT_NOT_IN_ROWS')
    return proven


def presentation_rows(figure):
    rows=figure['rows'];groups=figure.get('editorial_groups')
    if groups is None:return rows
    if rows[0][2]!='start' or rows[-1][2]!='total' or any(r[2]!='step' for r in rows[1:-1]):raise ValueError('EDITORIAL_GROUPING_REQUIRES_SINGLE_CHANGE_BRIDGE')
    indices=[i for g in groups for i in g['indices']]
    if sorted(indices)!=list(range(1,len(rows)-1)) or any(type(i) is not int for i in indices):raise ValueError('EDITORIAL_GROUPING_DROPPED_OR_DUPLICATED_SOURCE_ROW')
    result=[rows[0]]
    for g in groups:
        terms=[]
        for i in g['indices']:
            expr=rows[i][1];terms.extend([[expr,1]] if isinstance(expr,str) else expr)
        result.append((g['label'],terms,'step'))
    return result+[rows[-1]]
def expand_claims(story,ledger):
    """Render authored numeric placeholders directly from explicit source math.

    A claim is `expression` (signed fact terms) optionally divided by
    `denominator`, multiplied by a second ratio `times` ({expression,denominator})
    and reduced by another named claim's raw value (`less`). Raw values are
    exact Decimals before unit scaling, so a scale/margin split such as
    (rev - rev_prior) * prior_margin is computed, never retyped.
    """
    claims=story.get('quantified_claims',{});ledger=with_externals(ledger,story)
    def ratio(expr,den):
        value=amount(ledger,expr)
        if den is not None:
            d=amount(ledger,den)
            if not d:raise ValueError('DOSSIER_UNDEFINED_CLAIM_RATIO')
            value/=d
        return value
    def raw(name,trail=()):
        spec=claims.get(name)
        if not isinstance(spec,dict) or name in trail:raise ValueError('DOSSIER_UNSOURCED_QUANTIFIED_CLAIM')
        value=ratio(spec['expression'],spec.get('denominator'))
        if 'times' in spec:
            t=spec['times']
            if not isinstance(t,dict) or 'expression' not in t:raise ValueError('DOSSIER_INVALID_CLAIM_TIMES')
            value*=ratio(t['expression'],t.get('denominator'))
        if 'less' in spec:value-=raw(spec['less'],trail+(name,))
        return value
    def substitute(match):
        spec=claims.get(match.group(1))
        if not isinstance(spec,dict):raise ValueError('DOSSIER_UNSOURCED_QUANTIFIED_CLAIM')
        value=raw(match.group(1))
        scale=D(str(spec.get('scale','1')));multiplier=D(str(spec.get('multiplier','1')))
        if not scale.is_finite() or scale<=0 or not multiplier.is_finite():raise ValueError('DOSSIER_INVALID_CLAIM_UNIT_SCALE')
        value=value/scale*multiplier
        if spec.get('absolute'):value=abs(value)
        if not value.is_finite():raise ValueError('DOSSIER_NONFINITE_QUANTIFIED_CLAIM')
        places=spec.get('decimals',2)
        if type(places) is not int or not 0<=places<=6:raise ValueError('DOSSIER_INVALID_CLAIM_PRECISION')
        if 'signed' in spec and type(spec['signed']) is not bool:raise ValueError('DOSSIER_INVALID_CLAIM_SIGN')
        return format(value,('+' if spec.get('signed') else '')+(',' if spec.get('grouping') else '')+'.'+str(places)+'f')
    def walk(value):
        if isinstance(value,str):return re.sub(r'\{\{([a-z0-9_]+)\}\}',substitute,value)
        if isinstance(value,list):return [walk(x) for x in value]
        if isinstance(value,dict):return {k:walk(v) for k,v in value.items()}
        return value
    return walk(story)
def product_rows(ledger, figure):
    rows = []
    seen = set()
    for label, revenue, cost in figure['products']:
        if revenue == cost or {revenue, cost} & seen:
            raise ValueError('PRODUCT_DUPLICATE_SOURCE')
        seen.update((revenue, cost))
        for key, measure in ((revenue, 'revenue'), (cost, 'cost')):
            fact = ledger['facts'][key]
            if fact.get('product') != label or fact.get('measure') != measure:
                raise ValueError('PRODUCT_ROW_OR_MEASURE_MISMATCH ' + key)
            if (fact['period'] != ledger['issuer']['fiscal_period'] or fact['type'] != 'flow'
                    or fact['scope'] != 'consolidated' or fact['unit'] != '元'
                    or fact['classification'] != 'DISCLOSED' or not fact.get('source_cells')):
                raise ValueError('PRODUCT_CURRENT_DISCLOSED_FLOW_REQUIRED')
        # The revenue and gross-profit marks are DIFFERENT economic values.
        # Give each mark its own reproducible expression, never the same pair
        # of fact names (which cannot be independently checked by a reader).
        refs={'收入':revenue,'毛利':reference([[revenue,1],[cost,-1]])}
        rows.append((label, amount(ledger, revenue), amount(ledger, cost), refs))
    return rows


def volume_rate_rows(ledger, figure):
    """Decompose a monetary flow using disclosed, comparable average balances."""
    from comparison_basis import require_pair
    flow, base = figure['flow'], figure['average_balance']
    facts = ledger['facts']
    if flow == base:
        raise ValueError('VOLUME_RATE_DISTINCT_MEASURES_REQUIRED')
    for key in (flow, base):
        require_pair(ledger, key, key + '_prior')
        if facts[key]['type'] != 'flow' or facts[key]['scope'] != 'consolidated':
            raise ValueError('VOLUME_RATE_PERIOD_FLOW_REQUIRED')
        if (facts[key]['period'] != ledger['issuer']['fiscal_period']
                or facts[key + '_prior']['period'] != ledger['issuer']['comparative_period']):
            raise ValueError('VOLUME_RATE_REPORT_PERIOD_REQUIRED')
    if '平均' not in facts[base].get('denominator_definition', ''):
        raise ValueError('VOLUME_RATE_DISCLOSED_AVERAGE_REQUIRED')
    old, now = (amount(ledger, k) for k in (flow + '_prior', flow))
    previous, current = (amount(ledger, k) for k in (base + '_prior', base))
    if min(previous, current) <= 0:
        raise ValueError('VOLUME_RATE_POSITIVE_BALANCE_REQUIRED')
    volume = ((current - previous) * old / previous).quantize(D('0.01'))
    source = reference([flow, flow + '_prior', base, base + '_prior'])
    return [('上期' + facts[flow]['label'], old, 'start', flow + '_prior'),
            ('平均规模变化', volume, 'step', source),
            ('比率、结构及交互变化', now - old - volume, 'step', source),
            ('本期' + facts[flow]['label'], now, 'total', flow)]


def validate_offline_comparisons(ledger, story):
    """Enforce the same comparison contract for the figures, prose and evidence rows."""
    tools = ROOT / 'skills' / 'ashare-financial-storytelling' / 'tools'
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    from comparison_basis import require_growth_base, require_pair
    from coverage_review import check_dependencies
    facts = ledger['facts']

    def expression(keys, *, archival=False):
        check_dependencies(ledger, keys)
        periods = {facts[key]['period'] for key in keys}
        if len(periods) > 1:
            for key in keys:
                current = key.removesuffix('_prior')
                require_pair(ledger, current, current + '_prior')
                if current not in keys or current + '_prior' not in keys:
                    raise ValueError('OFFLINE_UNPAIRED_CROSS_PERIOD_EXPRESSION ' + key)
        archived = [key for key in keys if facts[key].get('disclosure_version') == 'original_before_restatement']
        if archived and (not archival or len(archived) != len(keys)):
            raise ValueError('OFFLINE_ARCHIVE_FACT_IN_COMPARATIVE_EXPRESSION')

    for name, claim in story.get('quantified_claims', {}).items():
        keys = dependencies(claim['expression'])
        archival = claim.get('basis') == 'original_before_restatement'
        expression(keys, archival=archival)
        den = claim.get('denominator')
        if den is not None:
            den_keys = dependencies(den)
            expression(den_keys, archival=archival)
            if archival and any(facts[k].get('disclosure_version') != 'original_before_restatement'
                                for k in keys + den_keys):
                raise ValueError('OFFLINE_ARCHIVE_MIXED_VERSION_DENOMINATOR ' + name)
            if amount(ledger, den) <= 0:
                raise ValueError('OFFLINE_NONPOSITIVE_DENOMINATOR ' + name)
            pnum = {facts[k]['period'] for k in keys}
            pden = {facts[k]['period'] for k in den_keys}
            if pnum != pden:
                if len(pnum) != 2 or not set(den_keys) <= set(keys) or any(not k.endswith('_prior') for k in den_keys):
                    raise ValueError('OFFLINE_DENOMINATOR_PERIOD_MISMATCH ' + name)
                require_growth_base(amount(ledger, den), name)
        if claim.get('times'):
            factor = claim['times']
            factor_num = dependencies(factor['expression'])
            factor_den = dependencies(factor['denominator'])
            expression(factor_num)
            expression(factor_den)
            if (len({facts[k]['period'] for k in factor_num + factor_den}) != 1
                    or amount(ledger, factor['denominator']) <= 0):
                raise ValueError('OFFLINE_FACTOR_DENOMINATOR_MISMATCH ' + name)
        if name.startswith('v2p_'):
            for key in keys + dependencies(den):
                require_pair(ledger, key, key + '_prior')

    for figure in story['figures']:
        family = figure['family']
        check_dependencies(ledger, cited(figure))
        if family == 'comparison':
            for _, prior, current in figure['pairs']:
                current_terms = [[current, 1]] if isinstance(current, str) else current
                prior_terms = [[prior, 1]] if isinstance(prior, str) else prior
                if prior_terms != [[key + '_prior', coefficient] for key, coefficient in current_terms]:
                    raise ValueError('COMPARISON_DIFFERENT_METRIC ' + figure['id'])
                bases = {require_pair(ledger, key, key + '_prior') for key, _ in current_terms}
                current_periods = {facts[key]['period'] for key, _ in current_terms}
                prior_periods = {facts[key]['period'] for key, _ in prior_terms}
                if len(current_periods) != 1 or len(prior_periods) != 1:
                    raise ValueError('OFFLINE_COMPARISON_EXPRESSION_MIXED_PERIODS ' + figure['id'])
                periods = [prior_periods.pop() + ('（重述后）' if 'restated' in bases else ''),
                           current_periods.pop()]
                if figure['periods'] != periods:
                    raise ValueError('OFFLINE_COMPARISON_LEGEND_MISMATCH ' + figure['id'])
        elif family == 'product_economics':
            product_rows(ledger, figure)
        elif family == 'volume_rate':
            volume_rate_rows(ledger, figure)
        elif family == 'signed_bridge':
            for _, expr, _ in figure['rows']:
                expression(dependencies(expr))
        elif family == 'income_flow_v3':
            bundle = build_profit_chain(ledger)
            if not set(bundle['facts']) <= set(cited(figure)):
                raise ValueError('DOSSIER_PROFIT_CHAIN_MISSING_SOURCE_TABLE_ROWS')
            signed_bridge_checkpoints(ledger, figure)
        elif family == 'income':
            # A source-declared mutually exclusive revenue/cost partition is mandatory.
            # The shared compiler independently checks source, cost and gross-profit ties.
            compile_disclosed_income(ledger)
        elif family in {'kpi_board', 'growth_bars', 'ratio_dumbbell', 'stock_delta', 'balance'}:
            # Newer common renderers already exist. Validate their source periods
            # instead of treating them as an unsupported company-specific adapter.
            # This check must fail closed before any SVG is rendered.
            def terms(expr):
                if isinstance(expr, str):
                    return [[expr, 1]]
                if not isinstance(expr, list) or not expr:
                    raise ValueError('OFFLINE_EXHIBIT_EXPRESSION_REQUIRED ' + figure['id'])
                return expr

            def same_metric(current, previous, *, expected_type=None):
                c, p = terms(current), terms(previous)
                if p != [[key + '_prior', coef] for key, coef in c]:
                    raise ValueError('OFFLINE_EXHIBIT_COMPARISON_DIFFERENT_METRIC ' + figure['id'])
                for key, _ in c:
                    require_pair(ledger, key, key + '_prior')
                    if expected_type and facts[key]['type'] != expected_type:
                        raise ValueError('OFFLINE_EXHIBIT_FACT_TYPE_MISMATCH ' + figure['id'])
                curr_periods = {facts[key]['period'] for key, _ in c}
                prev_periods = {facts[key]['period'] for key, _ in p}
                if len(curr_periods) != 1 or len(prev_periods) != 1:
                    raise ValueError('OFFLINE_EXHIBIT_MIXED_PERIODS ' + figure['id'])
                return next(iter(prev_periods)), next(iter(curr_periods))

            def ensure_legend(prev, curr):
                declared = figure.get('periods')
                if declared != [prev, curr]:
                    raise ValueError('OFFLINE_EXHIBIT_LEGEND_PERIOD_MISMATCH ' + figure['id'])

            if family == 'kpi_board':
                if not figure.get('tiles'):
                    raise ValueError('OFFLINE_KPI_TILES_REQUIRED ' + figure['id'])
                for tile in figure['tiles']:
                    if tile.get('kind') == 'money':
                        prev, curr = same_metric(tile['value'], tile['prior'])
                        if facts[dependencies(tile['value'])[0]]['type'] == 'stock':
                            if (tile.get('period') != curr or
                                    tile.get('prior_period') != prev or
                                    tile.get('delta_label') != '较年初'):
                                raise ValueError('OFFLINE_KPI_STOCK_DATE_REQUIRED ' + figure['id'])
                        else:
                            ensure_legend(prev, curr)
                    elif tile.get('kind') == 'ratio':
                        prev_n, curr_n = same_metric(tile['num'], tile['prior_num'])
                        prev_d, curr_d = same_metric(tile['den'], tile['prior_den'])
                        if (prev_n, curr_n) != (prev_d, curr_d):
                            raise ValueError('OFFLINE_KPI_RATIO_MIXED_PERIODS ' + figure['id'])
                        if ({facts[k]['type'] for k in
                             dependencies(tile['num']) + dependencies(tile['den'])} != {'flow'} or
                                amount(ledger, tile['den']) <= 0 or
                                amount(ledger, tile['prior_den']) <= 0):
                            raise ValueError('OFFLINE_KPI_RATIO_INVALID_BASIS ' + figure['id'])
                        ensure_legend(prev_n, curr_n)
                    else:
                        raise ValueError('OFFLINE_KPI_KIND_UNSUPPORTED ' + figure['id'])
            elif family == 'growth_bars':
                if not figure.get('pairs'):
                    raise ValueError('OFFLINE_GROWTH_PAIRS_REQUIRED ' + figure['id'])
                for row in figure['pairs']:
                    prev, curr = same_metric(row[2], row[1], expected_type='flow')
                    ensure_legend(prev, curr)
                    require_growth_base(amount(ledger, row[1]), figure['id'])
            elif family == 'ratio_dumbbell':
                if not figure.get('rows'):
                    raise ValueError('OFFLINE_RATIO_ROWS_REQUIRED ' + figure['id'])
                for row in figure['rows']:
                    pn, cn = same_metric(row['num'], row['prior_num'], expected_type='flow')
                    pd, cd = same_metric(row['den'], row['prior_den'], expected_type='flow')
                    if (pn, cn) != (pd, cd):
                        raise ValueError('OFFLINE_RATIO_MIXED_PERIODS ' + figure['id'])
                    ensure_legend(pn, cn)
                    if (amount(ledger, row['den']) <= 0 or
                            amount(ledger, row['prior_den']) <= 0 or
                            amount(ledger, row['num']) < 0 or
                            amount(ledger, row['prior_num']) < 0):
                        raise ValueError('OFFLINE_RATIO_INVALID_POSITIVE_GRAMMAR ' + figure['id'])
            elif family == 'stock_delta':
                if not figure.get('items'):
                    raise ValueError('OFFLINE_STOCK_ITEMS_REQUIRED ' + figure['id'])
                for label, side, prior, current in figure['items']:
                    if side not in {'asset', 'liability'}:
                        raise ValueError('OFFLINE_STOCK_SIDE_INVALID ' + figure['id'])
                    prev, curr = same_metric(current, prior, expected_type='stock')
                    if figure.get('dates') != [prev, curr]:
                        raise ValueError('OFFLINE_STOCK_DATE_MISMATCH ' + figure['id'])
            elif family == 'balance':
                if len(figure.get('dates', [])) != 2:
                    raise ValueError('OFFLINE_BALANCE_TWO_DATES_REQUIRED ' + figure['id'])
                for date, assets, liabilities, equity in figure['dates']:
                    if (any(facts[k]['type'] != 'stock' or facts[k]['period'] != date
                            for k in (assets, liabilities, equity)) or
                            amount(ledger, assets) != amount(ledger, liabilities) + amount(ledger, equity)):
                        raise ValueError('OFFLINE_BALANCE_IDENTITY_OR_DATE_INVALID ' + figure['id'])
        else:
            raise ValueError('OFFLINE_EXHIBIT_ADAPTER_UNVERIFIED ' + family)

def has_source_amount(region, printed):
    """Match a signed money token when PDF text separates accounting brackets."""
    region = re.sub(r'(?<=[(（])[^\S\r\n]+(?=\d)|(?<=\d)[^\S\r\n]+(?=[)）])', '', region)
    token = re.escape(printed.replace(',', ''))
    return re.search(r'(?<![0-9.+−(（-])' + token + r'(?![0-9.])', region) is not None


def validate(ledger,story,root=ROOT):
    expand_claims(story,ledger);check_cross_period_claims(ledger,story)
    source=ledger['source'];issuer=ledger['issuer'];path=(root/source['source_path']).resolve();path.relative_to(root.resolve())
    if not re.fullmatch(r'[0-9]{6}',issuer['code']):raise ValueError('DOSSIER_INVALID_ISSUER_CODE')
    from urllib.parse import urlsplit
    offline = story.get('composition') == 'OFFLINE_RESEARCH_CANDIDATE_V1'
    if offline:
        if not issuer.get('offline_candidate') or story.get('design') != 'EDITORIAL_V2':
            raise ValueError('OFFLINE_CANDIDATE_INTAKE_AND_DESIGN_REQUIRED')
        validate_offline_comparisons(ledger, story)
    url=urlsplit(source['official_announcement'] or '')
    if (not offline or source['official_announcement']) and (url.scheme!='https' or not url.hostname or url.username or url.password):raise ValueError('DOSSIER_SOURCE_REQUIRES_HTTPS_URL')
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=source['original_bytes_sha256'] or not data.startswith(b'%PDF'):raise ValueError('DOSSIER_ORIGINAL_PDF_BYTES_DRIFT')
    import pymupdf
    doc=pymupdf.open(path)
    identity_page=source.get('issuer_identity_page',1)
    if type(identity_page) is not int or not 1<=identity_page<=len(doc):raise ValueError('DOSSIER_ORIGINAL_PDF_IDENTITY')
    if (len(doc)!=source['physical_pages_observed']
        or issuer['code'] not in doc[identity_page-1].get_text()
        or re.sub(r'\s+','',issuer['name']) not in re.sub(r'\s+','',doc[0].get_text())):raise ValueError('DOSSIER_ORIGINAL_PDF_IDENTITY')
    cover=re.sub(r'\s+','',doc[0].get_text())
    report=re.search(r'(20[0-9]{2})年(半年度|第一季度|第三季度|年度)报告',cover)
    expected_kind={'H1':'半年度','FY':'年度','Q1':'第一季度','9M':'第三季度'}
    period=issuer['fiscal_period']
    if not report or report.group(1)!=period[:4] or expected_kind.get(period[4:])!=report.group(2):raise ValueError('DOSSIER_ORIGINAL_REPORT_PERIOD')
    # Quarterly reports print extra flow columns (e.g. Q3 single quarter next to
    # nine-month YTD). Each extra column must be declared once, explicitly.
    extra_columns=issuer.get('flow_columns',{})
    if not isinstance(extra_columns,dict) or any(c in {'本期/期末','上期/期初'} or not isinstance(p,str) or not re.fullmatch(r'20[0-9]{2}(Q[1-4]|H1|H2|9M|FY)',p) for c,p in extra_columns.items()):raise ValueError('DOSSIER_INVALID_EXTRA_FLOW_COLUMNS')
    archive_docs = {}
    if offline:
        import fin_intake as fi
        import statement_extract as se
        replay = se.to_ledger_facts(se.extract(doc, fi.rows_on_page, fi.squash), issuer)
        for key, fact in replay.items():
            observed = ledger['facts'].get(key)
            if observed is None or any(fact[field] != observed.get(field)
                                       for field in ('page', 'yuan', 'source_cells', 'source_column', 'period')):
                raise ValueError('OFFLINE_CANONICAL_SOURCE_COLUMN_DRIFT ' + key)
    for k,f in ledger['facts'].items():
        fact_doc = doc
        archive = f.get('archival_source')
        if offline and archive:
            archive_path = (root / archive['path']).resolve()
            archive_path.relative_to(root.resolve())
            if archive_path not in archive_docs:
                if hashlib.sha256(archive_path.read_bytes()).hexdigest() != archive['sha256']:
                    raise ValueError('OFFLINE_ARCHIVE_HASH_DRIFT ' + k)
                archive_docs[archive_path] = pymupdf.open(archive_path)
            fact_doc = archive_docs[archive_path]
            if (len(fact_doc) != archive['physical_pages']
                    or fi.detect_identity(fact_doc, issuer['code'])['fiscal_period'] != archive['period']
                    or f['period'] != archive['period']):
                raise ValueError('OFFLINE_ARCHIVE_IDENTITY ' + k)
        if f['type']=='flow' and f['classification']=='DISCLOSED':
            column=f.get('source_column')
            wanted=extra_columns[column] if column in extra_columns else issuer['comparative_period'] if column=='上期/期初' else issuer['fiscal_period']
            if f['period']!=wanted:raise ValueError('DOSSIER_FLOW_PERIOD_COLUMN_MISMATCH '+k)
        if f['scope']!='consolidated' or f['currency']!='CNY' or f['unit']!='元' or not D(f['yuan']).is_finite():raise ValueError('DOSSIER_FACT_BASIS '+k)
        if type(f['page']) is not int or not 1<=f['page']<=len(fact_doc):raise ValueError('DOSSIER_PHYSICAL_PAGE '+k)
        if f['classification']=='DERIVED':
            d=f['derivation'];terms=d['terms']
            if d['operation']!='subtract' or len(terms)!=2 or any(ledger['facts'][t]['classification']!='DISCLOSED' or ledger['facts'][t]['period']!=f['period'] for t in terms):raise ValueError('DOSSIER_DERIVATION_REQUIRES_ORIGINAL_OPERANDS')
            if amount(ledger,terms[0])-amount(ledger,terms[1])!=D(f['yuan']):raise ValueError('DOSSIER_DERIVED_VALUE_FALSE '+k)
        elif f['classification']=='DISCLOSED':
            cells=f.get('source_cells',[])
            if not cells:raise ValueError('DOSSIER_PHYSICAL_SOURCE_CELLS_REQUIRED '+k)
            for cell in cells:
                region=fact_doc[f['page']-1].get_textbox(pymupdf.Rect(cell['bbox'])+(-.5,-.5,.5,.5)).replace(',','')
                if cell.get('wrapped_number') is True:region=re.sub(r'\s+','',region)
                if offline:
                    from fin_intake import to_decimal
                    printed = cell['printed'].strip()
                    if not has_source_amount(region, printed):
                        raise ValueError('DOSSIER_SOURCE_CELL_FALSE ' + k)
                    signed = to_decimal(printed) * D(cell.get('unit_scale', '1'))
                    if cell.get('sign_flipped'):
                        signed = -signed
                    if signed != D(f['yuan']):
                        raise ValueError('DOSSIER_SOURCE_CELL_FALSE ' + k)
                elif cell.get('unit_scale'):
                    # report printed in 千元/万元/百万元: the cell must hold the printed figure and printed x scale = yuan
                    p=cell['printed'].strip().replace(',','');neg=p.startswith(('(','（'))
                    shown=D(p.strip('()（）'))*(-1 if neg else 1)
                    if cell.get('sign_flipped') is True:shown=-shown  # expense printed negative; canonical ledger stores it positive
                    if p.strip('()（）') not in region or shown*D(cell['unit_scale'])!=D(f['yuan']):raise ValueError('DOSSIER_SOURCE_CELL_FALSE '+k)
                elif not re.search(r'(?<![0-9.+-])'+re.escape(f['yuan'])+r'(?![0-9.])',region):raise ValueError('DOSSIER_SOURCE_CELL_FALSE '+k)
        else:raise ValueError('DOSSIER_CLASSIFICATION_UNKNOWN '+k)
    for test in story['accounting_identities']:
        if amount(ledger,test['left'])!=amount(ledger,test['right']):raise ValueError('DOSSIER_ACCOUNTING_IDENTITY '+test['name'])
    # Quarterly reports usually omit product revenue/cost notes; the income
    # Sankey is compiled (and fail-closed) only when the dossier asks for it.
    if any(f['family']=='income' for f in story['figures']):compile_disclosed_income(ledger)
    ids=[f['id'] for f in story['figures']]
    for f in story['figures']:
        if f['family']=='signed_bridge':
            presentation_rows(f)
            signed_bridge_checkpoints(ledger, f)
    if len(ids)!=len(set(ids)) or any(not re.fullmatch('[a-z][a-z0-9-]*',i) for i in ids):raise ValueError('DOSSIER_DUPLICATE_OR_UNSAFE_FIGURE')
    return {'status':'PASS','facts':len(ledger['facts']),'accounting_identities':len(story['accounting_identities']),'pdf_sha256':source['original_bytes_sha256'],'source_cells':'EXACT_ARCHIVED_PDF_COORDINATES_NOT_HUMAN_AUDIT'}
def chart(ledger,figure,mobile):
    issuer=ledger['issuer'];kw=dict(issuer=issuer['code'],pdf_sha256=ledger['source']['original_bytes_sha256'],mobile=mobile);period=issuer['fiscal_period'];title=figure['question'];v=lambda e:amount(ledger,e);family=figure['family']
    if family=='product_economics':return render_product_economics(product_rows(ledger,figure),title,period=period,**kw)
    if family=='volume_rate':return render_bridge(volume_rate_rows(ledger,figure),title,period=period,**kw)
    if family=='income':
        return render_sector_income(ledger,mobile=mobile,
                                    show_income_shares=figure.get('show_income_shares') is True)
    if family=='income_flow_v3':
        from income_flow_v3 import render
        return render(build_profit_chain(ledger), mobile=mobile).replace(
            '<svg ', '<svg data-dossier-profit-chain="true" ', 1)
    if family=='signed_bridge':return render_bridge([(l,v(e),role,reference(e)) for l,e,role in presentation_rows(figure)],title,period=figure.get('period',period),**kw)
    if family=='comparison':return render_comparison([(l,v(p),v(n),json.dumps({'periods':figure['periods'],'prior':p,'current':n},ensure_ascii=False,separators=(',',':'))) for l,p,n in figure['pairs']],title,periods=figure['periods'],**kw)
    if family=='balance':return render_balance([(date,v(a),v(l),v(e),json.dumps({'assets':a,'liabilities':l,'equity':e},separators=(',',':'))) for date,a,l,e in figure['dates']],title,**kw)
    if family in EXHIBIT_FAMILIES:return render_exhibit(ledger,figure,mobile,kw,title,period)
    if family=='components':return render_components([(l,v(e),reference(e)) for l,e in figure['parts']],v(figure['total']),title,period=figure.get('period',period),**kw)
    raise ValueError('DOSSIER_UNKNOWN_FINANCIAL_GRAMMAR '+family)
EXHIBIT_FAMILIES=('kpi_board','ratio_dumbbell','growth_bars','period_columns','stock_delta')
def ratio_of(ledger,num,den):
    d=amount(ledger,den)
    if not d:raise ValueError('DOSSIER_RATIO_ZERO_DENOMINATOR')
    return amount(ledger,num)/d*100
def render_exhibit(ledger,figure,mobile,kw,title,period):
    import exhibits as X
    family=figure['family'];periods=figure.get('periods',[ledger['issuer']['comparative_period'],period])
    ident=dict(issuer=kw['issuer'],period=period,pdf_sha256=kw['pdf_sha256'])
    if family=='kpi_board':
        tiles=[]
        for t in figure['tiles']:
            if t['kind']=='money':
                tiles.append(dict(label=t['label'],kind='money',value=amount(ledger,t['value']),prior=amount(ledger,t['prior']),value_ref=t['value'],prior_ref=t['prior'],period=t.get('period',periods[1]),prior_period=t.get('prior_period',periods[0]),lower_is_better=t.get('lower_is_better',False),delta_label=t.get('delta_label','同比')))
            elif t['kind']=='ratio':
                tiles.append(dict(label=t['label'],kind='ratio',value=ratio_of(ledger,t['num'],t['den']),prior=ratio_of(ledger,t['prior_num'],t['prior_den']),value_ref={'num':t['num'],'den':t['den']},prior_ref={'num':t['prior_num'],'den':t['prior_den']},period=periods[1],prior_period=periods[0],lower_is_better=t.get('lower_is_better',False)))
            else:raise ValueError('DOSSIER_KPI_KIND '+str(t.get('kind')))
        return X.render_kpi_board(tiles,title,mobile=mobile,
                                  adaptive_layout=figure.get('adaptive_layout'),**ident)
    if family=='ratio_dumbbell':
        rows=[dict(label=r['label'],value=ratio_of(ledger,r['num'],r['den']),prior=ratio_of(ledger,r['prior_num'],r['prior_den']),value_ref={'num':r['num'],'den':r['den']},prior_ref={'num':r['prior_num'],'den':r['prior_den']},lower_is_better=r.get('lower_is_better',False)) for r in figure['rows']]
        return X.render_ratio_dumbbell(rows,title,periods=periods,mobile=mobile,**ident)
    if family=='growth_bars':
        rows=[dict(label=r[0],prior=amount(ledger,r[1]),value=amount(ledger,r[2]),prior_ref=r[1],value_ref=r[2],lower_is_better=(r[3] if len(r)>3 else {}).get('lower_is_better',False)) for r in figure['pairs']]
        return X.render_growth_bars(rows,title,periods=periods,mobile=mobile,**ident)
    if family=='period_columns':
        ext={a:{'path':s['path'],'period':s['period'],'pdf_sha256':s['pdf_sha256']} for a,s in (figure.get('_external_specs') or {}).items()}
        series=[dict(label=c['label'],value=amount(ledger,c['value']),value_ref=c['value'],compare=c.get('compare'),highlight=c.get('highlight',False)) for c in figure['columns']]
        return X.render_period_columns(series,title,unit_label=figure['unit_label'],mobile=mobile,external=ext or None,**ident)
    if family=='stock_delta':
        rows=[dict(label=l,side=s,prior=amount(ledger,p),value=amount(ledger,c),prior_ref=p,value_ref=c) for l,s,p,c in figure['items']]
        return X.render_stock_delta(rows,title,dates=figure['dates'],mobile=mobile,**ident)
    raise ValueError('DOSSIER_UNKNOWN_FINANCIAL_GRAMMAR '+family)
def cited(figure):
    if figure.get('family') == 'product_economics':
        return [key for _, revenue, cost in figure['products'] for key in (revenue, cost)]
    if figure.get('family') == 'volume_rate':
        return [key for k in (figure['flow'], figure['average_balance']) for key in (k, k + '_prior')]
    if 'facts' in figure:return figure['facts']
    expr=[]
    for l,e,role in (figure.get('rows',[]) if figure.get('family')=='signed_bridge' else []):expr+=dependencies(e)
    for l,p,n in (figure.get('pairs',[]) if figure.get('family')=='comparison' else []):expr+=dependencies(p)+dependencies(n)
    for date,a,l,e in (figure.get('dates',[]) if figure.get('family')=='balance' else []):expr += [a,l,e]
    for l,e in figure.get('parts',[]):expr+=dependencies(e)
    def deps(x):
        if x is None:return []
        if isinstance(x,dict):return deps(x.get('num'))+deps(x.get('den'))
        return dependencies(x)
    for t in figure.get('tiles',[]):expr+=sum((deps(t.get(k)) for k in ('value','prior','num','den','prior_num','prior_den')),[])
    for r in (figure.get('rows',[]) if figure.get('family')=='ratio_dumbbell' else []):expr+=sum((deps(r.get(k)) for k in ('num','den','prior_num','prior_den')),[])
    for r in (figure.get('pairs',[]) if figure.get('family')=='growth_bars' else []):expr+=deps(r[1])+deps(r[2])
    for c in figure.get('columns',[]):expr+=deps(c['value'])
    for it in figure.get('items',[]):expr+=deps(it[2])+deps(it[3])
    if 'total' in figure:expr+=dependencies(figure['total'])
    return list(dict.fromkeys(expr))
def title_markup(story):
    """Optional editorial line breaks. `title_lines` are display lines whose phrase units are
    separated by '|'; a unit never wraps internally, so Chinese breaks only at phrase edges.
    Without `title_lines` the original markup is unchanged."""
    lines=story.get('title_lines')
    if lines is None:return H(story['title'])
    if not isinstance(lines,list) or not 2<=len(lines)<=3 or ''.join(lines).replace('|','')!=story['title']:raise ValueError('DOSSIER_TITLE_LINES_MUST_SPLIT_TITLE')
    return ''.join('<span style="display:block">'+''.join('<span style="display:inline-block">'+H(u)+'</span>' for u in line.split('|') if u)+'</span>' for line in lines)
def ids_of(story):return [f['id'] for f in story['figures']]
CSS_OPENING = """
main{padding-top:0}.opening{--paper:#f2ede2;--ink:#322e28;--accent:#84502d;background:var(--paper);color:var(--ink);
padding:clamp(32px,5vw,80px) clamp(22px,5vw,76px);margin:0 -28px 22px;display:grid;grid-template-columns:minmax(0,1.4fr) minmax(200px,.65fr);gap:6%;align-items:center}
.opening.bank{--paper:#102f36;--ink:#f6f5eb;--accent:#a7ddce}
.opening .eyebrow,.opening .metrics strong{color:var(--accent)}.opening h1{font-size:clamp(34px,4.3vw,62px);line-height:1.22;text-wrap:balance;margin:20px 0}
.opening .deck{color:var(--ink);font-size:clamp(16px,1.5vw,20px);line-height:1.7;margin:0}
.opening .metrics{display:grid;gap:24px;border-left:1px solid currentColor;padding-left:24px}
.opening .metrics span,.opening .metrics small{display:block;font-size:13px}.opening .metrics strong{display:block;font:600 clamp(30px,3vw,44px)/1.17 Georgia,serif;font-variant-numeric:tabular-nums}
.opening .metrics small{margin-top:3px}.opening~nav a{border:0;border-radius:0;border-bottom:1px solid #bdccc7;padding:3px 2px}.opening~nav{gap:10px 18px}
@media(max-width:850px){.opening{margin:0 -18px 14px;grid-template-columns:1fr;gap:24px;padding:32px 18px}.opening h1{margin:18px 0 14px}.opening .metrics{grid-template-columns:repeat(auto-fit,minmax(140px,1fr));border-left:0;border-top:1px solid currentColor;padding:16px 0 0;gap:12px}}
"""


def publish(folder,out=None,*,catalog_report=False):
    folder=Path(folder);ledger=read(folder/'source-ledger.json');story=read(folder/'publication.json');qa=validate(ledger,story);story=expand_claims(story,ledger);issuer=ledger['issuer'];code=issuer['code'];source=ledger['source'];parts=[];briefs=[]
    offline = story.get('composition') == 'OFFLINE_RESEARCH_CANDIDATE_V1'
    if catalog_report and not offline:
        raise ValueError('CATALOG_REPORT_REQUIRES_OFFLINE_COMPOSITION')
    if offline:
        if out is None or (not catalog_report and (ROOT / 'public').resolve() in Path(out).resolve().parents):
            raise ValueError('OFFLINE_CANDIDATE_REQUIRES_EXPLICIT_NON_PUBLIC_OUTPUT')
        manifest = read(folder / 'editorial-manifest.json')
        decisions = manifest['editorial']['figures']
        if (manifest['issuer'] != code or manifest['period'] != issuer['fiscal_period']
                or manifest['source_sha256'] != source['original_bytes_sha256']):
            raise ValueError('OFFLINE_EDITORIAL_MANIFEST_DRIFT: issuer, period or original PDF')
        planned = [(f['id'], f['question']) for f in story['figures']]
        approved = [(f['id'], f['title']) for f in decisions]
        if planned != approved:
            raise ValueError(
                f'OFFLINE_EDITORIAL_MANIFEST_DRIFT: current figures {planned!r}; '
                f'editorial manifest {approved!r}')
        roles = [f['role'] for f in decisions]
        if not roles or roles[0] != 'primary' or roles.count('primary') != 1:
            raise ValueError('OFFLINE_EDITORIAL_MANIFEST_DRIFT: expected one primary first figure')
        if any(f['family'] == 'income_flow_v3' for f in story['figures']) and story['figures'][0]['family'] != 'income_flow_v3':
            raise ValueError('DOSSIER_COMPLETE_PROFIT_SANKEY_MUST_BE_PRIMARY')
        if not source['official_announcement']:
            source = {**source, 'official_announcement': '#original-source'}
    lx=with_externals(ledger,story)
    def source_row(k):
        if ':' not in k:return None
        alias,name=k.split(':',1);other=lx['_external'][alias];fx=other['facts'][name]
        return '<tr><th>'+H(fx['label'])+'</th><td>'+H(fx['period'])+'</td><td class="number">'+H(fx['yuan'])+'</td><td>另一期原件披露</td><td><a href="'+other['source']['official_announcement']+'#page='+str(fx['page'])+'">'+H(other['issuer']['fiscal_period'])+' 原件 p.'+str(fx['page'])+'</a></td></tr>'
    for i,f in enumerate(story['figures']):
        if f['family']=='period_columns':f=dict(f,_external_specs=story.get('external_ledgers',{}))
        allkeys=cited(f);keys=[k for k in allkeys if ':' not in k];external_rows=''.join(source_row(k) for k in dict.fromkeys(allkeys) if ':' in k)
        pages=sorted({ledger['facts'][k]['page'] for k in keys})
        table=external_rows+''.join('<tr><th>'+H(ledger['facts'][k]['label'])+'</th><td>'+H(ledger['facts'][k]['period'])+'</td><td class="number">'+H(ledger['facts'][k]['yuan'])+'</td><td>'+('原文披露' if ledger['facts'][k]['classification']=='DISCLOSED' else '原值计算')+'</td><td><a href="'+source['official_announcement']+'#page='+str(ledger['facts'][k]['page'])+'">原件 p.'+str(ledger['facts'][k]['page'])+'</a></td></tr>' for k in keys)
        v2=story.get('design')=='EDITORIAL_V2'
        if v2:
            chap=f.get('chapter')
            lead=('<header class="chapter" id="ch-'+f['id']+'"><span>'+H(chap['kicker'])+'</span><h2>'+H(chap['title'])+'</h2><p>'+H(chap['summary'])+'</p></header>') if chap else ''
            trend=('<p><b>趋势</b>'+H(f['trend'])+'</p>') if f.get('trend') else ''
            parts.append(lead+f'<figure id="{f["id"]}" class="v2"><div class="figure-head"><span>图 {i+1:02d}</span><h2>{H(f["question"])}</h2><p>{H(f["takeaway"])}</p></div><div class="desktop-art">{chart(lx,f,False)}</div><div class="native-art">{chart(lx,f,True)}</div><figcaption>{trend}<p><b>重点</b>{H(f["analysis"])}</p><p><b>反证</b>{H(f["counter"])}</p><span>来源：原始披露报告 · 物理页 '+', '.join(map(str,pages))+' · 人民币原始元；图中金额适度舍入。<button type="button" data-export="{f["id"]}">导出当前图 SVG ↗</button></span></figcaption><details><summary>核对原始数据与计算口径</summary><div class="table-scroll"><table><thead><tr><th>原始项目</th><th>期间/时点</th><th>人民币元</th><th>性质</th><th>来源</th></tr></thead><tbody>'+table+'</tbody></table></div></details></figure>')
        else:parts.append(f'<figure id="{f["id"]}"><div class="figure-head"><span>FIGURE / {i+1:02d} · {H(f["eyebrow"])}</span><h2>{H(f["question"])}</h2><p>{H(f["takeaway"])}</p><button type="button" data-export="{f["id"]}">导出当前图 SVG ↗</button></div><div class="desktop-art">{chart(lx,f,False)}</div><div class="native-art">{chart(lx,f,True)}</div><figcaption><b>读图结论</b> / {H(f["analysis"])}<br><b>反证与边界</b> / {H(f["counter"])}<br><span>来源：原始披露报告 · 物理页 '+', '.join(map(str,pages))+' · 人民币原始元；图中金额适度舍入。</span></figcaption><details><summary>核对原始数据与计算口径</summary><div class="table-scroll"><table><thead><tr><th>原始项目</th><th>期间/时点</th><th>人民币元</th><th>性质</th><th>来源</th></tr></thead><tbody>'+table+'</tbody></table></div></details></figure>')
        if offline:
            parts[-1] = parts[-1].replace('<figure ', '<figure data-editorial-role="' + decisions[i]['role'] + '" ', 1)
            parts[-1] = parts[-1].replace('</figcaption>', '<p>' + H(f['identity']) + '</p></figcaption>', 1)
        if f.get('editorial_groups'):
            full_rows=''.join('<tr><td>'+H(label)+'</td><td>'+H(str(amount(ledger,expr)))+'</td><td>'+H(role)+'</td></tr>' for label,expr,role in f['rows'])
            parts[-1]=parts[-1].replace('</figure>','<details><summary>展开完整原始变动逐项对账（人民币元）</summary><div class="table-scroll"><table><tr><th>原始变动项目</th><th>精确金额</th><th>会计角色</th></tr>'+full_rows+'</table></div></details></figure>')
        briefs.append({'id':f['id'],'family':f['family'],'question':f['question'],'takeaway':f['takeaway'],'identity':f['identity'],'counter':f['counter'],'mobile':'桌面1040/1100与手机330独立绘制；全部金额与来源可见并可下载当前版本。','source_pages':pages,'facts':keys})
        if offline:
            briefs[-1]['source_expressions'] = {k: f[k] for k in ('periods', 'pairs', 'rows', 'flow', 'average_balance', 'products') if k in f}
    def essay(s):return '<section id="'+s['id']+'" class="essay"><div class="eyebrow">'+H(s['eyebrow'])+'</div><h2>'+H(s['title'])+'</h2>'+''.join('<p>'+H(p)+'</p>' for p in s['paragraphs'])+'</section>'
    # Essays without `after` keep the original position (after the second figure).
    # `after: <figure id>` or `after: end` interleaves prose with figures for reading rhythm.
    figure_ids=ids_of(story)
    for s in story['essays']:
        if s.get('after') and s['after']!='end' and s['after'] not in figure_ids:raise ValueError('DOSSIER_ESSAY_AFTER_UNKNOWN_FIGURE')
    sections=''.join(essay(s) for s in story['essays'] if not s.get('after'))
    placed={}
    for s in story['essays']:
        if s.get('after'):placed.setdefault(s['after'],[]).append(essay(s))
    body=''.join(parts[:2])+sections if not placed else None
    notes=''.join('<tr><th>'+H(n['theme'])+'</th><td>'+H(n['finding'])+'</td><td>'+H(n['boundary'])+'</td><td>'+''.join('<a href="'+source['official_announcement']+'#page='+str(p)+'">p.'+str(p)+'</a> ' for p in n['pages'])+'</td></tr>' for n in story['notes'])
    nav=''.join('<a href="#'+f['id']+'">'+H(f['nav'])+'</a>' for f in story['figures'])
    metrics=''.join('<div><span>'+H(m['label'])+'</span><strong>'+H(m['value'])+'</strong><small>'+H(m['context'])+'</small></div>' for m in story['metrics'])
    glance=''.join('<li>'+H(g)+'</li>' for g in story.get('glance',[]))
    style_v2='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#FFFFFF;color:#1D2B33;font:17px/1.8 "Noto Sans CJK SC","PingFang SC",sans-serif;-webkit-font-smoothing:antialiased}a{color:inherit}header{border-bottom:1px solid #E3E6E8;padding:16px 5vw;display:flex;justify-content:space-between;font-size:12px;letter-spacing:.06em;color:#5E6B73}main{max-width:1120px;margin:auto;padding:56px 28px}h1,h2{font-family:"Noto Serif CJK SC","Songti SC",serif;font-weight:700;line-height:1.35;letter-spacing:-.01em}h1{font-size:clamp(34px,4.6vw,56px);margin:14px 0 18px}.eyebrow{font-size:12px;letter-spacing:.14em;font-weight:700;color:#16824A}.deck{font-size:21px;line-height:1.75;max-width:900px;color:#33434C}.status{font-size:13px;color:#5E6B73}.glance{margin:34px 0;padding:22px 26px;background:#F6F7F8;border-radius:12px}.glance h2{font-size:20px;margin:0 0 8px}.glance ul{margin:0;padding-left:20px;columns:2;column-gap:40px}.glance li{break-inside:avoid;margin:4px 0;font-size:15px}.metrics{display:none}nav{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 26px}nav a{font-size:13px;text-decoration:none;padding:6px 12px;border:1px solid #E3E6E8;border-radius:999px;color:#33434C}nav a:hover{border-color:#16824A;color:#16824A}.thesis{border-left:4px solid #16824A;padding:6px 0 6px 22px;margin:36px 0}.thesis h2{font-size:24px;margin:0 0 8px}.chapter{margin:84px 0 6px;padding-top:26px;border-top:2px solid #1D2B33}.chapter span{font-size:12px;letter-spacing:.14em;font-weight:700;color:#16824A}.chapter h2{font-size:34px;margin:8px 0}.chapter p{font-size:18px;color:#33434C;max-width:860px;margin:0}figure.v2{margin:40px 0 56px}figure.v2 .figure-head span{font-size:12px;font-weight:700;letter-spacing:.12em;color:#5E6B73}figure.v2 .figure-head h2{font-size:26px;margin:6px 0 6px}figure.v2 .figure-head p{font-size:17px;color:#33434C;margin:0 0 14px;max-width:920px}svg{display:block;width:100%;height:auto}.desktop-art{padding:8px 0}.native-art{display:none}figure.v2 figcaption{font-size:15px;line-height:1.85;color:#33434C;padding:12px 0 0;border-top:1px solid #E3E6E8}figure.v2 figcaption p{margin:6px 0}figure.v2 figcaption b{display:inline-block;min-width:44px;color:#1D2B33;margin-right:6px}figure.v2 figcaption span{display:flex;justify-content:space-between;gap:12px;align-items:center;color:#5E6B73;font-size:12px;margin-top:10px}button{background:transparent;border:1px solid #CFD5D9;color:#33434C;padding:7px 12px;font:inherit;font-size:12px;border-radius:999px;cursor:pointer;white-space:nowrap}details{border-top:1px solid #E3E6E8;padding:12px 0;font-size:13px}summary{cursor:pointer;color:#16824A}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;margin-top:14px;font-size:12px}th,td{border-bottom:1px solid #E3E6E8;padding:10px 8px;text-align:left;vertical-align:top}td.number{font-variant-numeric:tabular-nums;white-space:nowrap}.essay{max-width:860px;margin:48px 0;padding:24px 28px;background:#F6F7F8;border-radius:12px}.essay h2{font-size:24px;margin:6px 0 6px}.essay p{margin:12px 0;font-size:16px}#notes{margin-top:80px}#notes table{min-width:650px}footer{overflow-wrap:anywhere;border-top:1px solid #E3E6E8;margin-top:60px;padding:28px 0;color:#5E6B73;font-size:12px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #16824A;outline-offset:3px}@media(max-width:850px){main{padding:30px 18px}.desktop-art{display:none}.native-art{display:block}h1{font-size:34px}.deck{font-size:18px}.glance{padding:16px 18px}.glance ul{columns:1}.chapter{margin-top:56px}.chapter h2{font-size:27px}.chapter p{font-size:16px}figure.v2 .figure-head h2{font-size:22px}figure.v2 .figure-head p{font-size:15px}figure.v2 figcaption span{flex-direction:column;align-items:flex-start}.essay{padding:18px}}'''
    style='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f7f6f1;color:#17393d;font:16px/1.85 "Noto Sans CJK SC","PingFang SC",sans-serif}a{color:inherit}header{border-bottom:1px solid #ced8cf;padding:18px 5vw;display:flex;justify-content:space-between;font-size:12px;letter-spacing:.06em}main{max-width:1180px;margin:auto;padding:50px 28px}h1,h2{font-family:"Noto Serif CJK SC","Songti SC",serif;font-weight:550;line-height:1.4}h1{font-size:clamp(34px,4.5vw,62px);max-width:1000px;margin:22px 0}h2{font-size:30px}.eyebrow,.figure-head>span{font-size:11px;letter-spacing:.15em;font-weight:700;color:#087f68}.deck{font-size:21px;max-width:900px}.status{font-size:13px;color:#617875;max-width:950px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;border-top:1px solid #cbd8ce;border-bottom:1px solid #cbd8ce;padding:28px 0;margin:38px 0}.metrics span,.metrics small{display:block;font-size:13px;color:#617875}.metrics strong{font-size:36px;font-weight:500}nav{display:flex;flex-wrap:wrap;gap:12px 22px;padding:0 0 35px;font-size:13px}.essay{max-width:860px;margin:55px 0}.essay p{margin:18px 0}.thesis{border-left:3px solid #087f68;padding:20px 28px;background:#eeeee6;margin:40px 0}.thesis h2{font-size:25px;margin-top:0}figure{margin:65px 0 90px;background:#fffefb;border-top:1px solid #b7cac0}.figure-head{padding:28px 30px 12px}.figure-head h2{font-size:29px;margin:12px 0}.figure-head p{max-width:930px;color:#536e6b}button{background:transparent;border:1px solid #b9cec2;color:#087f68;padding:10px 15px;font:inherit;font-size:12px;cursor:pointer}svg{display:block;width:100%;height:auto}.desktop-art{padding:12px 20px}.native-art{display:none}figcaption{padding:24px 30px;font-size:14px;border-top:1px solid #e2e7df}figcaption span{display:block;color:#647c73;font-size:12px;margin-top:12px}details{border-top:1px solid #d5dfd5;padding:16px 30px;font-size:13px}summary{cursor:pointer;color:#087f68}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;margin-top:20px;font-size:12px}th,td{border-bottom:1px solid #d8e0d5;padding:12px 10px;text-align:left;vertical-align:top}td.number{font-variant-numeric:tabular-nums;white-space:nowrap}footer{overflow-wrap:anywhere;border-top:1px solid #becfc3;margin-top:65px;padding:30px 0;color:#617875;font-size:12px}#notes table{min-width:650px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #087f68;outline-offset:3px}@media(max-width:850px){main{padding:35px 18px}.desktop-art{display:none}.native-art{display:block;padding:20px 0}h1{font-size:36px}.deck{font-size:18px}.metrics{gap:12px}.metrics strong{font-size:25px}.metrics span,.metrics small{font-size:11px}.figure-head,figcaption,details{padding-left:16px;padding-right:16px}.figure-head h2{font-size:25px}.thesis{padding:18px}h2{font-size:27px}}'''
    scripts='''document.querySelectorAll('[data-export]').forEach(b=>b.addEventListener('click',()=>{const f=b.closest('figure'),s=[...f.querySelectorAll('svg')].find(s=>s.getBoundingClientRect().width>0);const text=new XMLSerializer().serializeToString(s),u=URL.createObjectURL(new Blob([text],{type:'image/svg+xml'})),a=document.createElement('a');a.href=u;a.download=document.body.dataset.issuer+'-'+document.body.dataset.period+'-'+b.dataset.export+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}));'''
    embedded_ledger = ledger
    if offline and not catalog_report:
        # The offline reader has the source identity and cells; its bytes must not
        # depend on where the local checkout staged archived PDFs.
        embedded_ledger = {**ledger, 'source': {**source, 'source_path': Path(source['source_path']).name},
                           'facts': {key: ({**fact, 'archival_source': {**fact['archival_source'],
                                       'path': Path(fact['archival_source']['path']).name}}
                                       if fact.get('archival_source') else fact)
                                     for key, fact in ledger['facts'].items()}}
    html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+H(issuer['short']+'｜'+story['title'])+'</title><style>'+(style_v2 if story.get('design')=='EDITORIAL_V2' else style)+'</style><body data-issuer="'+code+'" data-period="'+issuer['fiscal_period']+'"><header><a href="/#companies">← 返回公司研究目录</a><span>FINANCIALS IN VISUALS</span></header><main><div class="eyebrow">'+H(issuer['short']+' / '+code+' / '+issuer.get('period_label',issuer['fiscal_period']))+'</div><h1>'+title_markup(story)+'</h1><p class="deck">'+H(story['deck'])+'</p><p class="status">来源限定研究 · '+H(issuer['audit'])+' · 原始披露、管理层解释和研究计算分列 · 独立人类二审尚未完成。</p><div class="metrics">'+metrics+'</div>'+(('<section class="glance" aria-label="本期一览"><h2>本期一览</h2><ul>'+glance+'</ul></section>') if glance else '')+'<nav aria-label="报告章节">'+nav+'<a href="#research">研究判断</a><a href="#notes">重大附注</a></nav><aside class="thesis"><h2>'+H(story['thesis']['title'])+'</h2><p>'+H(story['thesis']['body'])+'</p></aside>'+(body+''.join(parts[2:]) if body is not None else ''.join(p+''.join(placed.get(fid,[])) for p,fid in zip(parts,figure_ids))+''.join(placed.get('end',[])))+'<section id="notes"><div class="eyebrow">SOURCE NOTES / COUNTEREVIDENCE</div><h2>重大附注：哪些事实会改变判断？</h2><p>逐项阅读范围及计算边界如下。源金额校验不等于审计意见或独立人类二审。</p><div class="table-scroll"><table><tr><th>主题</th><th>核查发现</th><th>影响与边界</th><th>原件</th></tr>'+notes+'</table></div></section><footer><a href="'+source['official_announcement']+'">完整原始报告 ↗</a><p>归档原件 SHA256：'+source['original_bytes_sha256']+'</p><p>本报告不提供未经来源支持的估值目标、价格预测、销量归因或行业认证，不构成投资建议。</p><a href="/#companies">返回同一公司研究目录</a></footer></main><script type="application/json" id="ledger-data">'+json.dumps(embedded_ledger,ensure_ascii=False).replace('</','<\\/')+'</script><script>'+scripts+'</script></body></html>'
    route=issuer.get('route',f'/{code}.html')
    if not re.fullmatch(r'/[0-9]{6}(-[a-z0-9]+)?\.html',route):raise ValueError('DOSSIER_INVALID_ROUTE')
    target=Path(out) if out else ROOT/'public'/route.lstrip('/');target.parent.mkdir(exist_ok=True,parents=True)
    from publication_editorial import finalize_publication
    if offline:
        if story['metrics']:
            # Compose an opening spread from the article's own evidence.
            # Keep the verification and navigation in the reading column.
            hero_start = html.index('<main>') + len('<main>')
            status_start = html.index('<p class="status">', hero_start)
            metrics_start = html.index('<div class="metrics">', status_start)
            metrics_end = html.index('</div></div>', metrics_start) + len('</div></div>')
            hero = ('<section class="opening"><div class="opening-copy">' + html[hero_start:status_start]
                    + '</div>' + html[metrics_start:metrics_end] + '</section>')
            html = html[:hero_start] + hero + html[status_start:metrics_start] + html[metrics_end:]
            tone = 'bank' if story.get('capability_plan', {}).get('sector_route') == 'bank' else 'enterprise'
            html = html.replace('<section class="opening">', f'<section class="opening {tone}">', 1)
            html = html.replace('</style>', CSS_OPENING + '</style>', 1)
        comparison = []
        for key, basis in ledger.get('comparison_basis', {}).items():
            if basis['status'] != 'restated':
                continue
            before = ledger['facts'][basis['original_fact']]
            after = ledger['facts'][key + '_prior']
            archive = before.get('archival_source') or {}
            before_url = archive.get('url') or source['official_announcement']
            comparison.append('<tr><th>' + H(ledger['facts'][key]['label']) + '</th><td>' + H(after['period']) +
                              '</td><td class="number">' + H(before['yuan']) + '</td><td class="number">' +
                              H(after['yuan']) + '</td><td>' + H(basis['reason']) + ' · <a href="' +
                              H(before_url, quote=True) + '#page=' + str(before['page']) + '">调整前 p.' +
                              str(before['page']) + '</a> · <a href="' + H(source['official_announcement'], quote=True) +
                              '#page=' + str(after['page']) + '">调整后 p.' + str(after['page']) + '</a></td></tr>')
        if comparison:
            table = ('<section><h2>比较基础的变动</h2><div class="table-scroll"><table><thead><tr>'
                     '<th>原始项目</th><th>期间</th><th>调整前（元）</th><th>调整后（元）</th>'
                     '<th>原因和源格</th></tr></thead><tbody>' + ''.join(comparison) + '</tbody></table></div></section>')
            html = html.replace('<footer>', table + '<footer>', 1)
        html = html.replace('</style>', '@media(max-width:850px){.deck{margin:12px 0}.status{margin:10px 0}'
            'nav{margin:12px 0}.thesis{margin:20px 0}.thesis h2{font-size:20px}'
            'figure.v2{margin-top:26px}}</style>', 1)
        if not catalog_report:
            html = html.replace('<a href="/#companies">← 返回公司研究目录</a>', '<a href="#notes">核对原始披露</a>')
            html = html.replace('<a href="/#companies">返回同一公司研究目录</a>', '')
        html = html.replace('<footer>', '<footer id="original-source">', 1)
        html = html.replace('<header class="chapter"', '<div class="chapter"').replace('</p></header>', '</p></div>')
    else:
        html = finalize_publication(code, html, period=issuer['fiscal_period'])
    target.write_text(html)
    (folder/'figure-briefs.json').write_text(json.dumps({'issuer':code,'report':issuer['fiscal_period'],'source_sha256':source['original_bytes_sha256'],'figure_briefs':briefs},ensure_ascii=False,indent=2)+'\n')
    qa.update(html_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),figures=len(briefs) + (0 if offline else 1));(folder/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print('SOURCE_DOSSIER_PUBLISHED',code,len(briefs),qa['html_sha256']);return target
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('out', nargs='?')
    parser.add_argument('--catalog-report', action='store_true')
    args = parser.parse_args()
    publish(ROOT / args.folder, args.out, catalog_report=args.catalog_report)
