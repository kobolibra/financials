"""Industrial source-ledger adapter for shared nonhero art, not issuer templates."""
from decimal import Decimal as D
from editorial_bridge import render_bridge,render_balance,render_comparison,render_components,render_metric_cards,combine_panels


def figures(d, *, mobile):
    facts=d['facts'];identity=d['issuer'];source=d['source']
    def v(k):return D(facts[k]['yuan'])
    def ref(*keys):return '; '.join(k+' p.'+str(facts[k]['page']) for k in keys)
    def row(label,terms,kind='step'):
        return (label,sum((v(k)*D(sign) for k,sign in terms),D(0)),kind,ref(*(k for k,_ in terms)))
    common=dict(issuer=identity['code'],period=identity['fiscal_period'],pdf_sha256=source['original_bytes_sha256'],mobile=mobile)
    pnl=[row('营业毛利润',[('rev',1),('cogs',-1)],'start')]
    for name,terms in [('税金及附加',[('tax_surcharge',-1)]),('销售与管理费用',[('selling',-1),('admin',-1)]),('研发费用',[('rd_expense',-1)]),('财务费用',[('finance',-1)]),('其他与投资收益',[('other_income',1),('investment_income',1)]),('公允价值变动',[('fair_value',1)]),('减值与处置',[('credit_impairment',1),('asset_impairment',1),('asset_disposal',1)]),('营业外收支',[('nonop_income',1),('nonop_expense',-1)]),('所得税',[('income_tax',-1)]),('少数股东损益',[('nci',-1)])]:
        pnl.append(row(name,terms))
    pnl.append(row('归母净利润',[('parent_net',1)],'total'))
    cfo=[row('合并净利润',[('net_profit',1)],'start')]
    cfo.extend(row(facts[k]['label'],[(k,1)]) for k in d['cfo_adjustments'])
    cfo.append(row('经营现金净额',[('cfo',1)],'total'))
    cash=[row('期初现金等价物',[('cash_start',1)],'start')]
    cash.extend(row(label,[(k,1)]) for label,k in [('经营现金','cfo'),('投资现金','cfi'),('筹资现金','cff'),('汇率影响','fx_cash')])
    cash.append(row('期末现金等价物',[('cash_end',1)],'total'))
    out={k:render_bridge(rows,title,**common) for k,rows,title in [('pnl',pnl,'完整CAS毛利润至归母利润'),('cfo',cfo,'净利润与完整间接附注到经营现金'),('cash',cash,'现金等价物四活动闭合')]}
    dates=[]
    for suffix in ('_prior',''):
        keys=['assets'+suffix,'liabilities'+suffix,'equity_prior' if suffix else 'total_equity']
        if all(k in facts for k in keys):dates.append((facts[keys[0]]['period'],*(v(k) for k in keys),ref(*keys)))
    if dates:out['balance']=render_balance(dates,'两个时点资产与资金结构',**{k:v for k,v in common.items() if k!='period'})
    pairs=[('营业收入',v('rev_prior'),v('rev'),ref('rev_prior','rev')),
           ('营业毛利润，计算值',v('rev_prior')-v('cogs_prior'),v('rev')-v('cogs'),ref('rev_prior','cogs_prior','rev','cogs')),
           ('经营现金',v('cfo_prior'),v('cfo'),ref('cfo_prior','cfo'))]
    out['trend']=render_comparison(pairs,'收入毛利与现金两期比较',issuer=identity['code'],periods=(facts['rev_prior']['period'],facts['rev']['period']),pdf_sha256=source['original_bytes_sha256'],mobile=mobile)
    capex=v('cash_capex')
    free=[row('经营现金净额',[('cfo',1)],'start'),row('购建长期资产所付现金',[('cash_capex',-1)]),('简易现金FCF',v('cfo')-capex,'total',ref('cfo','cash_capex'))]
    card_entries=[('股利、利润及利息合并支付',v('dividend_interest_cash'),'CNY_yuan',ref('dividend_interest_cash'))]
    if 'bill_endorse_capex' in facts:card_entries.append(('非现金票据购建资产',v('bill_endorse_capex'),'CNY_yuan',ref('bill_endorse_capex')))
    out['capital']=combine_panels([render_bridge(free,'经营现金扣减现金资本开支',**common),render_metric_cards(card_entries,'独立支付及非现金事项，不计入上方FCF',**common)],'现金投资、非现金结算及分配严格分开')
    if 'power_gen_100m_kwh' in facts:
        f=facts['power_gen_100m_kwh']
        if f['type']!='operating_metric' or f['unit']!='亿千瓦时' or f['period']!=identity['fiscal_period']:raise ValueError('OPERATING_METRIC_BASIS_DRIFT')
        out['sector']=render_metric_cards([('物理发电量，不是净售电量',v('power_gen_100m_kwh'),'亿千瓦时',ref('power_gen_100m_kwh')),('法定营业收入，不能由发电量推算',v('rev'),'CNY_yuan',ref('rev')),('经营现金净额，收付口径',v('cfo'),'CNY_yuan',ref('cfo'))],'发电、会计确认与现金是不同事实',**common)
    elif 'innovative_drug_sales_100m' in facts:
        f=facts['innovative_drug_sales_100m']
        if f['type']!='operating_metric' or f['unit']!='亿元' or f['period']!=identity['fiscal_period']:raise ValueError('OPERATING_METRIC_BASIS_DRIFT')
        innovation=v('innovative_drug_sales_100m')*D(100000000)
        goods=v('drug_sales_rev')
        if not D(0)<=innovation<=goods:raise ValueError('OPERATING_SUBSET_EXCEEDS_PARENT')
        primary=[('药品等商品销售',goods,ref('drug_sales_rev')),('知识产权许可',v('licence_rev'),ref('licence_rev')),('其他合同收入',v('other_rev'),ref('other_rev'))]
        nested=[('商品销售中的创新药，管理层口径',innovation,ref('innovative_drug_sales_100m')),('其余商品，计算差额',goods-innovation,ref('drug_sales_rev','innovative_drug_sales_100m'))]
        # Both composition bands use total revenue as their reference domain.
        first=render_components(primary,v('rev'),'第一层，互斥法定收入',**common)
        second=render_components(nested,goods,'第二层，商品中的创新药子集',reference_total=v('rev'),**common)
        stock=render_metric_cards([('尚未履约义务，期末存量，非本期收入',v('rpo'),'CNY_yuan',ref('rpo'))],'独立时点存量',**common)
        out['sector']=combine_panels([first,second,stock],'合同收入、商品子集及履约存量分层')
    return out
