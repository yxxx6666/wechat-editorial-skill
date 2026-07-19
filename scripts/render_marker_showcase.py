#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import argparse, html, json, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from md_to_wechat import render_component
REG=json.loads((ROOT/'templates/editorial-marker-registry.json').read_text('utf-8'))
LABEL={'auto_safe':'自动安全','source_triggered':'原文触发','manual':'手动指定','wechat_fallback':'微信降级'}
COL={'auto_safe':'#2783DE','source_triggered':'#46A171','manual':'#D5803B','wechat_fallback':'#7D7A75'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('-o','--output',default=str(ROOT/'examples/v0.5.0-all-markers-showcase.html')); args=ap.parse_args()
 groups={}
 for m in REG['markers']: groups.setdefault(m['category'],[]).append(m)
 cards=[]
 for cat,items in groups.items():
  section=[f'<section class="catalog-section"><div class="section-head"><h2>{html.escape(cat.replace("_"," ").title())}</h2><span>{len(items)} markers</span></div><div class="grid">']
  for m in items:
   rendered=render_component({'type':m['id'],'role':'showcase','content':m['sample'],'style_token':'showcase','children':[]})
   section.append(f"""<article class="marker-card" data-marker-id="{m['id']}"><div class="card-meta"><span class="status" style="--status:{COL[m['activation']]}">{LABEL[m['activation']]}</span><code>{m['id']}</code></div><h3>{html.escape(m['name_zh'])}</h3><div class="wechat-preview">{rendered}</div><div class="card-foot"><span>{html.escape(m['source_policy'])}</span><span>{html.escape(m['wechat_support'])}</span></div></article>""")
  section.append('</div></section>'); cards.append(''.join(section))
 counts={a:sum(1 for m in REG['markers'] if m['activation']==a) for a in LABEL}
 stats=''.join(f'<div><strong>{counts[k]}</strong><span>{LABEL[k]}</span></div>' for k in LABEL)
 doc=f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v0.5.0 全量文章标识库</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#F4F5F7;color:#2C2C2B;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif}}.hero{{background:#191919;color:#fff;padding:56px 7vw 48px}}.hero-inner{{max-width:1120px;margin:auto}}.kicker{{color:#5E9FE8;font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase}}h1{{font-size:48px;line-height:1.12;margin:14px 0 16px;letter-spacing:-1.5px}}.lead{{max-width:720px;color:rgba(255,255,255,.68);font-size:17px;line-height:1.7}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:32px}}.stats div{{border-top:1px solid rgba(255,255,255,.2);padding-top:14px}}.stats strong{{font-size:26px;display:block}}.stats span{{font-size:12px;color:rgba(255,255,255,.6)}}main{{max-width:1180px;margin:0 auto;padding:46px 30px 80px}}.catalog-section{{margin:0 0 54px}}.section-head{{display:flex;justify-content:space-between;align-items:end;border-bottom:1px solid #DADDE1;padding-bottom:12px;margin-bottom:20px}}.section-head h2{{font-size:24px;margin:0;text-transform:capitalize}}.section-head span{{font-size:12px;color:#7D7A75}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.marker-card{{background:#fff;border:1px solid #E6E5E3;border-radius:12px;padding:18px;min-width:0}}.card-meta{{display:flex;justify-content:space-between;gap:12px;align-items:center}}.status{{font-size:11px;color:var(--status);font-weight:700;border:1px solid var(--status);border-radius:999px;padding:3px 8px}}code{{font-size:11px;color:#7D7A75;overflow-wrap:anywhere}}h3{{font-size:17px;margin:14px 0 12px}}.wechat-preview{{border:1px solid #ECEEF1;border-radius:8px;padding:16px;background:#fff;overflow:hidden}}.card-foot{{display:flex;justify-content:space-between;font-size:11px;color:#9A9792;margin-top:12px}}@media(max-width:760px){{h1{{font-size:34px}}.stats{{grid-template-columns:repeat(2,1fr)}}main{{padding:28px 16px 60px}}.grid{{grid-template-columns:1fr}}.hero{{padding:38px 20px}}}}
</style></head><body><header class="hero"><div class="hero-inner"><div class="kicker">xingchen / wechat-editorial-skill</div><h1>v0.5.0 全量文章标识库</h1><p class="lead">72 个可执行渲染器。全部进入 Skill 包，但按自动安全、原文触发和手动指定分层启用。所有正文组件坚持原文逐字保真，不生成标签或结论。</p><div class="stats">{stats}</div></div></header><main>{''.join(cards)}</main></body></html>"""
 Path(args.output).write_text(doc,'utf-8'); print(args.output)
if __name__=='__main__': main()
