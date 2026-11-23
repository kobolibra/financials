#!/usr/bin/env python3
"""Company-agnostic extraction of the three consolidated statements of any A-share periodic report.

Why this exists: per-company fact specs (page / row / column typed by hand) do not generalize.
Chinese Accounting Standards fix the statement formats (财政部格式：一般企业 / 商业银行 / 保险公司 /
证券公司), so line items have standard names. This module

  1. finds the consolidated balance sheet, income statement and cash-flow statement pages
     (any prefix: "1、", "2026年6月30日", "截至…期间", "年初到报告期末", "（续）");
  2. rebuilds wrapped labels, strips enumerations and "（损失以“－”号填列）" notes;
  3. locates the current / prior amount columns per page by x geometry (note-reference columns and
     parenthesised negatives handled), reads the unit (元 / 千元 / 万元 / 百万元);
  4. detects the statement format from line items and maps every row to a canonical key with
     context rules (e.g. 利息收入 under 财务费用 vs. a bank's interest income);
  5. runs format-aware accounting identities. A residual is never absorbed: it is reported with
     the unmapped rows of that section, so a new or unusual line item surfaces instead of being
     silently dropped. New items are handled by adding a synonym to CANON (with a regression test),
     never by company-specific code.

Every extracted fact keeps the physical page, the printed cell text and its bbox, so the shared
publication validator re-reads it from the archived PDF.
"""
from __future__ import annotations

import re
from decimal import Decimal as D

# prefix: enumeration, a date / period phrase, "年半年度" (digits split away), "未经审计"; never a sentence (的/中/在/，)
TITLE = re.compile(r'^(?:[0-9一二三四五六七八九十]+[、.．]|[（(][0-9一二三四五六七八九十]+[)）]|[^的中在：:，,。]{0,24}?)?'
                   r'(合并及公司|合并及母公司|合并及银行|合并|母公司|公司)(?:年初到报告期末|本报告期)?(资产负债表|利润表|现金流量表|所有者权益变动表|股东权益变动表)(?:（续）|\(续\)|[-－—]续)?$')
PARENT_UNAUDITED_TITLE = re.compile(r'^未经审计(资产负债表|利润表|现金流量表)(?:[（(]续[）)])?$')
STATEMENTS = {'资产负债表': 'bs', '利润表': 'is', '现金流量表': 'cf', '所有者权益变动表': 'eq', '股东权益变动表': 'eq'}
UNITS = [('百万元', D(1000000)), ('千元', D(1000)), ('万元', D(10000)), ('元', D(1))]
PREFIX = re.compile(r'^(?:[一二三四五六七八九十]+[、.．]|[（(][一二三四五六七八九十0-9]+[)）]|[0-9]+[.、．]|其中[:：]|加[:：]|减[:：]|：)+')
NOTE = re.compile(r'[（(](?:[^（）()]*(?:号填列|以“|以"|损失以|亏损|净亏损|号$)[^（）()]*(?:[）)]|$)|(?:损失|亏损|净亏损|收益|亏损总额)以.*?填列[）)])')
NOTE_REF = re.compile(r'(?:附注)?(?:[一二三四五六七八九十]+[、.．])?[0-9]+(?:[（(][0-9一二三四五六七八九十]+[)）])?$')
AMOUNT = re.compile(r'^[(（]?-?[0-9][0-9,]*(?:\.[0-9]+)?[)）]?$')


def norm(label: str) -> str:
    s = re.sub(r'\s+', '', label)
    s = re.sub(r'[–—\-－]+$', '', s)
    if NOTE_REF.fullmatch(s):
        return ''
    if re.search(r'[一-龥]', s):
        # note column glued to the label: 营业收入七、48 / 营业收入四(46),十七(3) / 投资收益附注五、12
        ref = r'(?:附注)?(?:[一二三四五六七八九十]+(?:[、.．][0-9]+|[（(][0-9]+[)）])|[（(][一二三四五六七八九十]+[)）][0-9]+)(?:[（(][0-9a-z]+[)）])*'
        s = re.sub(r'(?<=[一-龥）)])' + ref + r'(?:[,，、]' + ref + r')*$', '', s)
        # loss hints on subtotals: 营业利润(亏损) / 利润总额(亏损总额) / 净利润(净亏损)
        s = re.sub(r'[（(](?:净)?亏损(?:总额)?[)）]', '', s)
        s = re.sub(r'[（(](?:转回|损失|收益)以负号列示[)）]', '', s)
        # sign hints: 财务(费用)/收入, 公允价值变动收益/(损失), 资产处置(损失)/收益
        s = re.sub(r'[（(](费用|损失|收益|亏损|收入)[)）]', r'\1', s)
        s = re.sub(r'/(费用|损失|收益|亏损|收入)$', '', s)
    s = NOTE.sub('', s)
    s = re.sub(r'[（(]续[)）]', '', s)
    prev = None
    while prev != s:
        prev, s = s, PREFIX.sub('', s)
    s = NOTE.sub('', s)
    s = re.sub(r'[（(][^（）()]*(以|填)[^（）()]*$', '', s)  # a fill-in note cut off by a line wrap: 固定资产报废损失（收益以
    return s.strip('：:')


def value(printed: str) -> D:
    t = printed.strip().replace(',', '').replace('，', '')
    neg = t.startswith(('(', '（')) and t.endswith((')', '）'))
    t = t.strip('()（）')
    v = D(t)
    return -v if neg else v


# ---------------------------------------------------------------- canonical line items
# (key, statement, pattern on the normalised label, condition on the previous mapped key or None)
# Order matters inside a statement: the first matching unused rule wins.
FIN_COST = ('finance', 'interest_expense')
CANON = [
    # income statement — 一般企业
    ('total_rev', 'is', r'^营业总收入$', None),
    ('rev', 'is', r'^营业收入(合计)?$', None),
    ('total_cost', 'is', r'^营业总成本$', None),
    ('cogs', 'is', r'^营业成本$', None),
    ('tax_surcharge', 'is', r'^税金及附加$', None),
    ('selling', 'is', r'^销售费用$', None),
    ('admin', 'is', r'^管理费用$', None),
    ('rd_expense', 'is', r'^研发费用$', None),
    ('finance', 'is', r'^财务费用$', None),
    ('interest_expense', 'is', r'^利息费用$', ('finance',)),
    ('interest_income', 'is', r'^利息收入$', FIN_COST),
    ('other_income', 'is', r'^其他收益$', None),
    ('investment_income', 'is', r'^投资收益$', None),
    ('associate_income', 'is', r'^对联营企业和合营企业的投资收益$', None),
    ('fx_gain', 'is', r'^汇兑(净)?(收益|损益)$', None),
    ('hedge_gain', 'is', r'^净敞口套期(收益|损益)$', None),
    ('fair_value', 'is', r'^公允价值变动(收益|损益)$', None),
    ('credit_impairment', 'is', r'^信用减值损失$', None),
    ('asset_impairment', 'is', r'^(资产减值损失|其他资产减值损失)$', None),
    ('asset_disposal', 'is', r'^资产处置(收益|损益|损失)$', None),
    ('operating_profit', 'is', r'^营业利润$', None),
    ('nonop_income', 'is', r'^营业外收入$', None),
    ('nonop_expense', 'is', r'^营业外支出$', None),
    ('pretax', 'is', r'^利润总额$', None),
    ('income_tax', 'is', r'^所得税费用$', None),
    ('net_profit', 'is', r'^净利润$', None),
    ('continuing_profit', 'is', r'^持续经营净利润$', None),
    ('parent_net', 'is', r'^(归属于)?(母公司|本行|本公司)(股东|所有者)(的)?净利润$', None),
    ('nci', 'is', r'^(少数股东损益|少数股东的净利润)$', None),
    ('oci_net', 'is', r'^其他综合收益的税后净额$', None),
    ('comprehensive', 'is', r'^综合收益总额$', None),
    # 金融企业格式（银行 / 证券 / 保险）
    ('fin_interest_income', 'is', r'^利息收入$', None),
    ('fin_interest_expense', 'is', r'^利息支出$', None),
    ('nii', 'is', r'^(利息净收入|净利息收入)$', None),
    ('fee_income', 'is', r'^手续费及佣金收入$', None),
    ('fee_expense', 'is', r'^手续费及佣金支出$', None),
    ('fee_net', 'is', r'^(手续费及佣金净收入|净手续费及佣金收入)$', None),
    ('brokerage_fee', 'is', r'^经纪业务手续费净收入$', None),
    ('other_business_rev', 'is', r'^其他业务收入$', None),
    ('surrender', 'is', r'^退保金$', None),
    ('claims_net', 'is', r'^赔付支出净额$', None),
    ('reserve_net', 'is', r'^提取保险(责任)?(合同)?准备金净额$', None),
    ('policy_dividend', 'is', r'^保单红利支出$', None),
    ('reinsurance_cost', 'is', r'^分保费用$', None),
    ('other_business_cost', 'is', r'^其他业务成本$', None),
    ('opex_total', 'is', r'^营业支出(合计)?$', None),
    ('admin_fin', 'is', r'^业务及管理费$', None),
    ('earned_premium', 'is', r'^已赚保费$', None),
    ('insurance_revenue', 'is', r'^保险服务收入$', None),
    ('insurance_expense', 'is', r'^保险服务费用$', None),
    ('reinsurance_allocation', 'is', r'^分出保费的分摊$', None),
    ('reinsurance_recovery', 'is', r'^摊回保险服务费用$', None),
    ('insurance_finance', 'is', r'^承保财务损益$', None),
    ('reinsurance_finance', 'is', r'^分出再保险财务损益$', None),
    # balance sheet
    ('money_funds', 'bs', r'^(货币资金|现金及存放中央银行款项)$', None),
    ('trading_assets', 'bs', r'^交易性金融资产$', None),
    ('notes_receivable', 'bs', r'^应收票据$', None),
    ('ar', 'bs', r'^应收账款$', None),
    ('receivable_financing', 'bs', r'^应收款项融资$', None),
    ('prepayments', 'bs', r'^预付款项$', None),
    ('other_receivables', 'bs', r'^其他应收款$', None),
    ('inventory', 'bs', r'^存货$', None),
    ('contract_assets', 'bs', r'^合同资产$', None),
    ('current_assets', 'bs', r'^流动资产合计$', None),
    ('loans', 'bs', r'^(发放)?贷款(和|及)垫款$', None),
    ('reverse_repo', 'bs', r'^买入返售金融资产$', None),
    ('term_deposits', 'bs', r'^定期存款$', None),
    ('debt_investments', 'bs', r'^债权投资$', None),
    ('other_debt_investments', 'bs', r'^其他债权投资$', None),
    ('other_equity_investments', 'bs', r'^其他权益工具投资$', None),
    ('other_noncurrent_fin_assets', 'bs', r'^其他非流动金融资产$', None),
    ('long_equity_investment', 'bs', r'^长期股权投资$', None),
    ('investment_property', 'bs', r'^投资性房地产$', None),
    ('fixed_assets', 'bs', r'^固定资产$', None),
    ('construction', 'bs', r'^在建工程$', None),
    ('rou_assets', 'bs', r'^使用权资产$', None),
    ('intangible', 'bs', r'^无形资产$', None),
    ('development', 'bs', r'^开发支出$', None),
    ('goodwill', 'bs', r'^商誉$', None),
    ('dta', 'bs', r'^递延所得税资产$', None),
    ('noncurrent_assets', 'bs', r'^非流动资产合计$', None),
    ('assets', 'bs', r'^资产(总计|合计)$', None),
    ('short_debt', 'bs', r'^短期借款$', None),
    ('notes_payable', 'bs', r'^应付票据$', None),
    ('ap', 'bs', r'^应付账款$', None),
    ('advances', 'bs', r'^预收款项$', None),
    ('contract_liabilities', 'bs', r'^合同负债$', None),
    ('deposits', 'bs', r'^(吸收存款|客户存款)$', None),
    ('brokerage_payable', 'bs', r'^代理买卖证券款$', None),
    ('repo', 'bs', r'^卖出回购金融资产款$', None),
    ('trading_liabilities', 'bs', r'^交易性金融负债$', None),
    ('insurance_liabilities', 'bs', r'^保险合同负债$', None),
    ('payroll', 'bs', r'^应付职工薪酬$', None),
    ('taxes_payable', 'bs', r'^应交税费$', None),
    ('other_payables', 'bs', r'^其他应付款$', None),
    ('current_debt', 'bs', r'^一年内到期的非流动负债$', None),
    ('current_liabilities', 'bs', r'^流动负债合计$', None),
    ('long_debt', 'bs', r'^长期借款$', None),
    ('bonds', 'bs', r'^应付债券$', None),
    ('lease', 'bs', r'^租赁负债$', None),
    ('dtl', 'bs', r'^递延所得税负债$', None),
    ('deferred_income', 'bs', r'^递延收益$', None),
    ('provisions', 'bs', r'^预计负债$', None),
    ('noncurrent_liabilities', 'bs', r'^非流动负债合计$', None),
    ('liabilities', 'bs', r'^负债合计$', None),
    ('share_capital', 'bs', r'^(实收资本|股本)(（或股本）)?$', None),
    ('capital_reserve', 'bs', r'^资本公积$', None),
    ('treasury_stock', 'bs', r'^库存股$', None),
    ('oci_reserve', 'bs', r'^其他综合收益$', None),
    ('surplus_reserve', 'bs', r'^盈余公积$', None),
    ('general_risk_reserve', 'bs', r'^一般风险准备$', None),
    ('retained', 'bs', r'^未分配利润$', None),
    ('parent_equity', 'bs', r'^归属于母公司(所有者|股东)(的)?(权益|股东权益|所有者权益)(（或股东权益）)?合计$', None),
    ('nci_equity', 'bs', r'^少数股东权益$', None),
    ('equity', 'bs', r'^(所有者权益|股东权益)(（或股东权益）)?合计$', None),
    ('liabilities_equity', 'bs', r'^负债(和|及)(所有者权益|股东权益)(（或股东权益）)?(总计|合计)$', None),
    # cash flow
    ('sales_cash', 'cf', r'^销售商品、?提供劳务收到的现金$', None),
    ('tax_refund', 'cf', r'^收到的税费返还$', None),
    ('other_op_in', 'cf', r'^收到其他与经营活动有关的现金$', None),
    ('op_inflow', 'cf', r'^经营活动现金流入小计$', None),
    ('purchase_cash', 'cf', r'^购买商品、?接受劳务支付的现金$', None),
    ('employee_cash', 'cf', r'^支付给职工(以及|及)为职工支付的现金$', None),
    ('tax_paid', 'cf', r'^支付的各项税费$', None),
    ('other_op_out', 'cf', r'^支付其他与经营活动有关的现金$', None),
    ('op_outflow', 'cf', r'^经营活动现金流出小计$', None),
    ('cfo', 'cf', r'^经营活动(产生|使用)的现金流量净额$', None),
    ('invest_recover', 'cf', r'^收回投资(收到|所收到)的现金$', None),
    ('invest_income_cash', 'cf', r'^取得投资收益(收到|所收到)的现金$', None),
    ('invest_inflow', 'cf', r'^投资活动现金流入小计$', None),
    ('cash_capex', 'cf', r'^购建固定资产、?无形资产和其他长期资产(支付|所支付)的现金$', None),
    ('invest_pay', 'cf', r'^投资(支付|所支付)的现金$', None),
    ('invest_outflow', 'cf', r'^投资活动现金流出小计$', None),
    ('cfi', 'cf', r'^投资活动(产生|使用)的现金流量净额$', None),
    ('equity_raise_cash', 'cf', r'^吸收投资收到的现金$', None),
    ('borrow_cash', 'cf', r'^取得借款收到的现金$', None),
    ('other_fin_pay', 'cf', r'^支付其他与筹资活动有关的现金$', None),
    ('disposal_cash', 'cf', r'^处置固定资产、?无形资产和其他长期资产收回的现金净额$', None),
    ('subsidiary_disposal_cash', 'cf', r'^处置子公司及其他营业单位收到的现金净额$', None),
    ('subsidiary_acquire_cash', 'cf', r'^取得子公司及其他营业单位支付的现金净额$', None),
    ('premium_cash', 'cf', r'^收到(签发保险合同保费取得|原保险合同保费取得)的现金$', None),
    ('claims_cash', 'cf', r'^支付(签发保险合同赔款|原保险合同赔付款项)的现金$', None),
    ('fee_paid_cash', 'cf', r'^支付手续费及佣金的现金$', None),
    ('fin_inflow', 'cf', r'^筹资活动现金流入小计$', None),
    ('debt_repay', 'cf', r'^偿还债务支付的现金$', None),
    ('dividend_interest', 'cf', r'^分配股利、?利润或偿付利息支付的现金$', None),
    ('fin_outflow', 'cf', r'^筹资活动现金流出小计$', None),
    ('cff', 'cf', r'^筹资活动(产生|使用)的现金流量净额$', None),
    ('cash_fx', 'cf', r'^汇率变动对现金及现金等价物的影响(额)?$', None),
    ('net_cash_change', 'cf', r'^现金及现金等价物净(增加|减少|变动)(/（减少）|/\(减少\))?(额)?$', None),
    ('cash_open', 'cf', r'^(加：)?期初现金及现金等价物余额$', None),
    ('cash_close', 'cf', r'^期末现金及现金等价物余额$', None),
]
CANON_RE = [(k, s, re.compile(p), c) for k, s, p, c in CANON]
FORMAT_MARKERS = {  # checked in this order; a 营业成本 line overrides all (general format with a finance subsidiary)
    'insurance': ('insurance_revenue', 'earned_premium', 'insurance_expense'),
    'securities': ('brokerage_payable', 'brokerage_fee'),
    'bank': ('deposits', 'loans', 'nii'),
}


def segments(doc, rows_on_page, squash):
    """Rows of every consolidated statement, in reading order, split by page.

    A statement can start mid-page under the end of the previous one (e.g. the parent-company
    balance sheet), so the context switches at the title ROW, not at the page."""
    titles = []
    cache = {}
    for i, page in enumerate(doc):
        if not re.search(r'(资产负债表|利润表|现金流量表|权益变动表)', squash(page.get_text())):
            continue  # cheap text filter: row geometry only for pages that can hold a statement title
        rows = rows_on_page(page)
        for r in rows:
            m = TITLE.match(squash(r['label']))
            if m:
                titles.append((i + 1, r['y'], m.group(1), STATEMENTS[m.group(2)]))
                cache[i + 1] = rows
    titles = [(p, y, '合并' if sc.startswith('合并') else sc, st) for p, y, sc, st in titles]  # 合并及公司: consolidated columns come first
    first = [t for t in titles if t[2] == '合并' and t[3] != 'eq']
    if not first:
        return {}
    start = first[0][0]
    stop = max(t[0] for t in titles if t[0] >= start and t[3] != 'eq')
    out, ctx, done, units = {}, None, set(), {}
    for p in range(start, min(len(doc), stop + 3) + 1):
        rows = cache.get(p) or rows_on_page(doc[p - 1])
        for r in rows:
            m = TITLE.match(squash(r['label']))
            parent = PARENT_UNAUDITED_TITLE.fullmatch(squash(r['label']))
            if parent and ctx and ctx[0] == '合并' and STATEMENTS[parent.group(1)] == ctx[1]:
                done.add(ctx)
                ctx = ('公司', ctx[1])
                continue
            if m:
                scope, st = ('合并' if m.group(1).startswith('合并') else m.group(1)), STATEMENTS[m.group(2)]
                # a title only closes a statement that actually collected numeric rows: an audit opinion
                # listing "合并及母公司资产负债表、利润表…" in prose is not a statement
                if ctx and ctx != (scope, st) and ctx[0] == '合并' and any(x['numbers'] for rows_ in out.get(ctx[1], {}).values() for x in rows_):
                    done.add(ctx)
                ctx = (scope, st)
                units.setdefault(st, None)
                continue
            if ctx and ctx[0] == '合并' and ctx[1] != 'eq' and ctx not in done:
                out.setdefault(ctx[1], {}).setdefault(p, []).append(r)
                if units.get(ctx[1]) is None and not r['numbers']:
                    units[ctx[1]] = unit_of(squash(r['label']), strict=False)
    out['_units'] = {k: v for k, v in units.items() if v is not None}
    return out


def unit_of(text: str, strict=True):
    """Unit of a statement: 单位：千元 / 金额单位为人民币百万元 / a bare 人民币元 header line."""
    m = re.search(r'(?:单位|金额单位|货币单位)[^。]{0,8}?(?:人民币)?(百万元|千元|万元|元)', text)
    if not m and not strict:
        m = re.fullmatch(r'[（(]?(?:人民币)?(百万元|千元|万元|元)[)）]?', text.strip())
    if not m:
        return D(1) if strict else None
    return dict(UNITS)[m.group(1)]


def amount_columns(rows, column_indices=(0, 1)):
    """Two value columns of a statement page: current (left) and prior (right).

    Right edges of clear amounts (comma, decimals or parentheses) are clustered; parenthesised
    negatives sit a few points right of positives, so clusters within 8pt merge."""
    edges = []
    for r in rows:
        for n in r['numbers']:
            t = n['printed'].strip()
            if AMOUNT.match(t) and (',' in t or '.' in t or t.startswith(('(', '（'))):
                edges.append(n['bbox'][2])
    edges.sort()
    clusters = []
    for x in edges:
        if clusters and x - clusters[-1][-1] <= 8:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    if not clusters:
        return None
    top = max(len(c) for c in clusters)
    big = sorted((c for c in clusters if len(c) >= max(3, top * 0.25)), key=min)
    if len(big) <= max(column_indices):
        return None
    return [(min(big[index]) - 4, max(big[index]) + 4) for index in column_indices]


def labelled_rows(rows, statement=None):
    """For ambiguous amount rows, recover nearby wrapped canonical labels."""
    patterns = [rx for _, st, rx, _ in CANON_RE if statement in (None, st)]

    def canonical(label):
        return any(rx.fullmatch(label) for rx in patterns)

    out = []
    for i, row in enumerate(rows):
        if not row['numbers']:
            continue
        label = row['label']
        normalized = norm(label)
        short = len(normalized) < 2
        if short or not canonical(normalized):
            own = '' if NOTE_REF.fullmatch(re.sub(r'\s+', '', label)) else label
            above = []
            y = row['y']
            for preceding in reversed(rows[max(0, i - 3):i]):
                if preceding['numbers'] or y - preceding['y'] > 22:
                    break
                above.insert(0, preceding['label'])
                y = preceding['y']
            following = rows[i + 1] if i + 1 < len(rows) else None
            below = (following['label'] if following and not following['numbers']
                     and following['y'] - row['y'] <= 10 else '')
            reconstructed = next(
                (candidate for n in range(len(above) + 1)
                 for tail in ((own + below, own) if short else (own, own + below))
                 if (candidate := ''.join(above[len(above) - n:]) + tail)
                 and canonical(norm(candidate))), None)
            if reconstructed is not None:
                label = reconstructed
            elif short:
                near = above[-1] if above and row['y'] - rows[i - 1]['y'] <= 10 else ''
                label = near + own + below
        out.append(dict(row, label=label))
    return out


# Lines that are expenses by nature. Canonical ledger convention: an expense is POSITIVE (CAS general format).
# Reports that print expenses negative (IFRS style, 美的 / 招行 / 中国人寿) are normalised at intake; the cell
# keeps the printed text and a `sign_flipped` flag, and the validator re-reads it with the flip.
COST_PARTS = ('cogs', 'tax_surcharge', 'selling', 'admin', 'rd_expense', 'finance', 'fin_interest_expense', 'fee_expense',
              'surrender', 'claims_net', 'reserve_net', 'policy_dividend', 'reinsurance_cost')
EXPENSE_KEYS = ('cogs', 'tax_surcharge', 'selling', 'admin', 'rd_expense', 'finance', 'interest_expense', 'nonop_expense', 'income_tax',
                'opex_total', 'total_cost', 'fin_interest_expense', 'fee_expense', 'admin_fin', 'other_business_cost', 'surrender', 'claims_net',
                'reserve_net', 'policy_dividend', 'reinsurance_cost', 'insurance_expense', 'reinsurance_allocation', 'insurance_finance')


def extract(doc, rows_on_page, squash):
    segs = segments(doc, rows_on_page, squash)
    units = segs.pop('_units', {})
    doc_unit = next(iter(units.values()), None)
    facts, unmapped, notes = {}, [], []
    pages = {st: sorted(ps) for st, ps in segs.items()}
    for st in ('is', 'bs', 'cf'):
        if st not in segs:
            notes.append('STATEMENT_NOT_FOUND ' + st)
            continue
        used, last = set(), None
        column_indices = (0, 1)
        for p in sorted(segs[st]):
            rows = segs[st][p]
            # the unit is read once per statement (header line under the title) and carried to its
            # continuation pages; a page-level text search would pick up a neighbouring note's unit
            scale = units.get(st) or doc_unit or unit_of(squash(doc[p - 1].get_text()))
            # Combined statements can be ordered by entity (group 2 periods,
            # company 2 periods) or by period (group and company within each).
            for row in rows:
                header = squash(row['label'])
                if re.search(r'(本集团|合并)(本行|公司|母公司)(本集团|合并)(本行|公司|母公司)', header):
                    column_indices = (0, 2)
                    break
            cols = amount_columns(rows, column_indices) or amount_columns(rows_on_page(doc[p - 1]), column_indices)
            if cols is None:
                continue
            for r in labelled_rows(rows, st):
                cells = [None, None]
                for n in r['numbers']:
                    t = n['printed'].strip()
                    if not AMOUNT.match(t):
                        continue
                    for j, (lo, hi) in enumerate(cols):
                        if lo <= n['bbox'][2] <= hi and cells[j] is None:
                            cells[j] = n
                if cells == [None, None]:
                    continue
                lab = norm(r['label'])
                if re.search(r'(年度|季度)报告', lab):  # running footer with the page number
                    continue
                key = None
                for k, s_, rx, cond in CANON_RE:
                    if s_ == st and k not in used and rx.match(lab) and (cond is None or last in cond):
                        key = k
                        break
                if key is None:
                    unmapped.append({'statement': st, 'page': p, 'label': lab, 'y': r['y'], 'after': last,
                                     'current': cells[0]['printed'] if cells[0] else None,
                                     'prior': cells[1]['printed'] if cells[1] else None})
                    continue
                used.add(key)
                last = key
                facts[key] = {'statement': st, 'page': p, 'label': lab, 'raw_label': r['label'], 'scale': scale,
                              'current': cells[0], 'prior': cells[1]}
    # A 营业成本 line means the general format, even when a finance subsidiary adds 利息收入 / 吸收存款 lines.
    fmt = 'general'
    if 'cogs' not in facts:
        for f, markers in FORMAT_MARKERS.items():
            if any(m in facts for m in markers):
                fmt = f
                break
    # Sign convention: CAS general format prints expenses as positive numbers; some (IFRS-style)
    # financial statements print them negative. Decided from the large cost lines, never per item.
    probe = [value(facts[k]['current']['printed']) for k in ('cogs', 'opex_total', 'total_cost', 'admin_fin', 'income_tax') if k in facts and facts[k]['current']]
    convention = 'expenses_negative' if probe and all(v < 0 for v in probe) else 'expenses_positive'
    return {'format': fmt, 'convention': convention, 'pages': pages, 'facts': facts, 'unmapped': unmapped, 'notes': notes}


def flipped(result, key):
    return result.get('convention') == 'expenses_negative' and key in EXPENSE_KEYS


def amounts(result, side):
    """Canonical amounts in yuan: expenses positive whatever the report's printing convention."""
    out = {}
    for k, f in result['facts'].items():
        c = f[side]
        if c is not None:
            out[k] = value(c['printed']) * f['scale'] * (-1 if flipped(result, k) else 1)
    return out


def identities(result):
    """Format-aware closure checks on both columns. Returns (passed, failed) lists of messages."""
    ok, bad = [], []
    result['source_anomalies'] = []
    for side in ('current', 'prior'):
        subtotals = []
        v = amounts(result, side)
        ded = lambda k: v[k]  # canonical: expenses already positive
        g = lambda *ks: all(k in v for k in ks)
        tests = []
        if g('assets', 'liabilities', 'equity'):
            tests.append(('资产=负债+权益', v['assets'], v['liabilities'] + v['equity']))
        if g('equity', 'parent_equity', 'nci_equity'):
            tests.append(('权益=归母+少数', v['equity'], v['parent_equity'] + v['nci_equity']))
        if g('pretax', 'operating_profit', 'nonop_income', 'nonop_expense'):
            tests.append(('利润总额=营业利润+营业外收支', v['pretax'], v['operating_profit'] + v['nonop_income'] - ded('nonop_expense')))
        if g('net_profit', 'pretax', 'income_tax'):
            tests.append(('净利润=利润总额-所得税', v['net_profit'], v['pretax'] - ded('income_tax')))
        if g('net_profit', 'parent_net', 'nci'):
            tests.append(('净利润=归母+少数', v['net_profit'], v['parent_net'] + v['nci']))
        if g('net_cash_change', 'cfo', 'cfi', 'cff'):
            tests.append(('现金净增加=经营+投资+筹资+汇率', v['net_cash_change'], v['cfo'] + v['cfi'] + v['cff'] + v.get('cash_fx', D(0))))
        if g('cash_close', 'cash_open', 'net_cash_change'):
            tests.append(('期末现金=期初+净增加', v['cash_close'], v['cash_open'] + v['net_cash_change']))
        if g('cfo', 'op_inflow', 'op_outflow'):
            tests.append(('经营现金=流入-流出', v['cfo'], v['op_inflow'] - (-v['op_outflow'] if v['op_outflow'] < 0 else v['op_outflow'])))
        if result['format'] == 'general' and g('operating_profit', 'rev'):
            # line items are the evidence; printed subtotals (营业总收入 / 营业总成本) are checked separately
            top = v['rev'] + sum((v[k] for k in ('fin_interest_income', 'fee_income', 'earned_premium') if k in v), D(0))
            cost = sum((v[k] for k in COST_PARTS if k in v), D(0))
            adds = sum((v[k] for k in ('other_income', 'investment_income', 'fx_gain', 'hedge_gain', 'fair_value',
                                         'credit_impairment', 'asset_impairment', 'asset_disposal') if k in v), D(0))
            tests.append(('营业利润=收入类明细-成本费用明细+其他损益项', v['operating_profit'], top - cost + adds))
            if g('total_rev'):
                subtotals.append(('营业总收入=营业收入+金融类收入', v['total_rev'], top))
            if g('total_cost'):
                subtotals.append(('营业总成本=各成本费用项', v['total_cost'], cost))
        if result['format'] != 'general' and g('operating_profit', 'rev', 'opex_total'):
            tests.append(('营业利润=营业收入-营业支出', v['operating_profit'], v['rev'] - ded('opex_total')))
        scale = max((f['scale'] for f in result['facts'].values()), default=D(1))
        for name, left, right in subtotals:
            if abs(left - right) > 2 * scale:
                # the report's own printed subtotal disagrees with its line items: a SOURCE finding to disclose,
                # not an extraction error to patch (e.g. 万科 2026H1 prints 营业总成本 equal to 营业成本)
                result['source_anomalies'].append(f'{side}:{name} 原件小计与明细差额 {left - right}')
            else:
                ok.append(f'{side}:{name}')
        for name, left, right in tests:
            if left == right:
                ok.append(f'{side}:{name}')
            elif scale > 1 and abs(left - right) <= 2 * scale:
                # statements printed in 千元/百万元 round each line; a tail within two printed units is the
                # report's own rounding, recorded as such (never absorbed into a line item)
                ok.append(f'{side}:{name} 尾差 {left - right}（四舍五入）')
            else:
                bad.append(f'{side}:{name} 差额 {left - right}')
    return ok, bad


def to_ledger_facts(result, issuer):
    """Ledger facts (fin_intake / source_publication schema) for every mapped key, both columns."""
    out = {}
    fy, cp = issuer['fiscal_period'], issuer['comparative_period']
    end = stock_dates(fy)
    for k, f in result['facts'].items():
        for side, suffix in (('current', ''), ('prior', '_prior')):
            c = f[side]
            if c is None:
                continue
            flow = f['statement'] != 'bs'
            fact = {'yuan': str(value(c['printed']) * f['scale'] * (-1 if flipped(result, k) else 1)), 'label': f['label'] + ('（比较期）' if suffix else ''), 'page': f['page'],
                    'type': 'flow' if flow else 'stock', 'period': (fy if side == 'current' else cp) if flow else end[side],
                    'scope': 'consolidated', 'classification': 'DISCLOSED', 'unit': '元', 'currency': 'CNY',
                    'source_cells': [{'bbox': c['bbox'], 'printed': c['printed'], 'wrapped_number': bool(c.get('wrapped'))}],
                    'source_row_label': f['raw_label'], 'source_column': '本期/期末' if side == 'current' else '上期/期初',
                    'extraction': 'STATEMENT_EXTRACT_CANON_V1'}
            if f['scale'] != 1 or flipped(result, k):
                fact['source_cells'][0]['unit_scale'] = str(f['scale'])
            if flipped(result, k):
                fact['source_cells'][0]['sign_flipped'] = True  # printed as a negative expense; canonical expense is positive
            out[k + suffix] = fact
    return out


def stock_dates(fiscal_period: str):
    y = int(fiscal_period[:4])
    tail = fiscal_period[4:]
    day = {'Q1': '03-31', '3M': '03-31', 'H1': '06-30', '9M': '09-30', 'Q3': '09-30', 'FY': '12-31', 'A': '12-31'}.get(tail, '12-31')
    return {'current': f'{y}-{day}', 'prior': f'{y - 1}-12-31'}
