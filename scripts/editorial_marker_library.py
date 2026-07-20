#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static WeChat-safe renderers for the v0.6.2 integrity-audited editorial marker registry."""
from __future__ import annotations
import html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REGISTRY_PATH=ROOT/'templates/editorial-marker-registry.json'
FF="-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif"
TEXT='#2A2E34'; MUTED='#7B8792'; BLUE='#1746A2'; BLUE_BG='#EAF0FA'; GREEN='#2F855A'; GREEN_BG='#EAF6EF'; ORANGE='#B7791F'; ORANGE_BG='#FFF4D6'; RED='#C53030'; RED_BG='#FDECEC'; PURPLE='#6B46C1'; PURPLE_BG='#F2ECFB'; GREY='#7B8792'; GREY_BG='#F1F2F4'; LINE='#E5EAEE'; PALE='#F7F8FA'
def esc(v): return html.escape(str(v or ''),quote=True)
def load_marker_registry(): return json.loads(REGISTRY_PATH.read_text('utf-8'))
def library_marker_ids(): return {m['id'] for m in load_marker_registry()['markers']}
def library_marker_category(marker_id):
    for m in load_marker_registry()['markers']:
        if m['id']==marker_id: return m['category']
    return ''
def source_triggered_component(text):
    pairs=[('定义：','definition_box'),('定义:','definition_box'),('事实：','fact_box'),('事实:','fact_box'),('案例：','example_box'),('案例:','example_box'),('提示：','callout_note'),('提示:','callout_note'),('技巧：','callout_tip'),('技巧:','callout_tip'),('注意：','callout_warning'),('注意:','callout_warning'),('警告：','callout_caution'),('警告:','callout_caution'),('重要：','callout_important'),('重要:','callout_important'),('作者：','author_byline'),('作者:','author_byline'),('发布日期：','publish_date'),('发布时间：','publish_date'),('阅读时间：','reading_time'),('来源：','source_note'),('来源:','source_note'),('引文：','citation_block'),('引文:','citation_block')]
    stripped=str(text or '').strip()
    for prefix,marker in pairs:
        if stripped.startswith(prefix): return marker
    return ''

def content_aware_component(text, semantic_role='neutral', section_index=0, group_index=0):
    """Select a block marker from source semantics without generating copy."""
    raw=str(text or '').strip()
    explicit=source_triggered_component(raw)
    if explicit:
        return explicit
    if not (16 <= len(raw) <= 150):
        return ''
    if re.search(r'^(?:所谓|定义为)|(?:是指|指的是)', raw):
        return 'definition_box'
    if re.search(r'^(?:例如|比如|举例来说|以.+为例)', raw):
        return 'example_box'
    if semantic_role=='risk' and re.search(r'(记住|必须|务必|不要|不能|警惕|风险|禁止)', raw):
        return 'callout_caution'
    if semantic_role=='attention' and re.search(r'(注意|提醒|尤其|需要留意|值得重视)', raw):
        return 'callout_warning'
    if semantic_role=='insight' and re.search(r'(真正|本质|关键|核心|最重要|值得记住|结构正确|不是.+而是)', raw):
        return ('callout_important' if (section_index+group_index)%2==0 else 'top_bar_box')
    if semantic_role in {'knowledge','data'} and re.search(r'(研究|数据|证据|表明|发现|原因|作用|意味着|取决于|参与|提供)', raw):
        return ('fact_box' if (section_index+group_index)%2==0 else 'minimal_gray_box')
    return ''
def source_payloads_for_library_component(marker_id,content):
    if marker_id not in library_marker_ids(): return []
    if marker_id in {'simple_compare_table','data_table'}: return []
    if marker_id=='big_number' and isinstance(content,dict) and content.get('source'): return [str(content['source'])]
    if isinstance(content,str): return [content] if content else []
    if isinstance(content,list): return [str(x) for row in content for x in (row if isinstance(row,list) else [row]) if x]
    if not isinstance(content,dict): return []
    out=[]
    for key in ('text','source','value','left','right'):
        if content.get(key): out.append(str(content[key]))
    for key in ('items','rows'):
        value=content.get(key,[])
        if isinstance(value,list):
            for row in value:
                if isinstance(row,list): out.extend(str(x) for x in row if x)
                elif row: out.append(str(row))
    return out
def tone(t):
    return {'risk':(RED_BG,RED),'action':(GREEN_BG,GREEN),'attention':(ORANGE_BG,ORANGE),'insight':(PURPLE_BG,PURPLE),'old_belief':(GREY_BG,GREY)}.get(t,(BLUE_BG,BLUE))
def p(text,extra=''):
    return f'<p style="font-size:16px;line-height:1.75;color:{TEXT};margin:0;font-family:{FF};{extra}">{esc(text)}</p>'
def heading_p(text,size=21,extra=''):
    return f'<p style="font-size:{size}px;line-height:1.45;color:{TEXT};font-weight:700;margin:0;font-family:{FF};{extra}">{esc(text)}</p>'
def list_rows(items,symbol=None,number=None):
    out=[]
    for idx,item in enumerate(items or []):
        mark=(number(idx) if number else symbol or '•')
        out.append(f'<p style="font-size:16px;line-height:1.7;color:{TEXT};margin:0 0 10px 0;font-family:{FF};"><span style="display:inline-block;min-width:24px;color:{BLUE};font-weight:700;margin-right:6px;">{esc(mark)}</span>{esc(item)}</p>')
    return ''.join(out)
def render_library_component(marker_id,content):
    bg,color=tone(content.get('tone','data') if isinstance(content,dict) else 'data')
    text=content.get('text','') if isinstance(content,dict) else str(content or '')
    inline_styles={'strong_emphasis':f'font-weight:700;color:{TEXT}','solid_underline':f'font-weight:700;color:{BLUE};border-bottom:2px solid {BLUE};padding-bottom:1px','dotted_underline':f'font-weight:700;color:{BLUE};border-bottom:2px dotted {BLUE};padding-bottom:1px','double_underline':f'font-weight:700;color:{BLUE};border-bottom:3px double {BLUE};padding-bottom:1px','strikethrough':f'color:{GREY};text-decoration:line-through;text-decoration-color:#A0A6AF;text-decoration-thickness:2px','inline_highlight':f'font-weight:700;color:{BLUE};background:{BLUE_BG};padding:1px 4px;border-radius:3px','text_color':f'font-weight:700;color:{PURPLE}','inline_pill':f'display:inline-block;color:{BLUE};background:{BLUE_BG};border-radius:999px;padding:2px 8px;font-weight:700','inline_outline':f'display:inline-block;color:{BLUE};border:1px solid {BLUE};border-radius:4px;padding:1px 6px;font-weight:700','data_badge':f'display:inline-block;color:#FFFFFF;background:{BLUE};border-radius:4px;padding:2px 6px;font-weight:700','inline_code':f'display:inline-block;color:#333333;background:{GREY_BG};border-radius:4px;padding:1px 5px;font-family:Menlo,Consolas,monospace','footnote_mark':f'display:inline-block;color:{BLUE};font-size:12px;vertical-align:4px;font-weight:700','soft_marker_underline':f'font-weight:700;color:{BLUE};box-shadow:inset 0 -0.42em 0 {BLUE_BG};padding:0 2px','keyword_corner_outline':f'font-weight:700;color:{PURPLE};border-left:2px solid {PURPLE};border-bottom:2px solid {PURPLE};padding:0 3px 1px 4px','dual_tone_phrase':f'font-weight:700;color:{PURPLE};background:{PURPLE_BG};padding:1px 4px;border-radius:3px'}
    if marker_id in inline_styles:
        return f'<p style="font-size:16px;line-height:1.75;color:{TEXT};margin:12px 0;font-family:{FF};">示例文字 <span style="{inline_styles[marker_id]}">{esc(text)}</span> 保持原句。</p>'
    idx=int(content.get('index',1) if isinstance(content,dict) else 1); num=f'{idx:02d}'
    if marker_id=='chapter_dot_rail': return f'<section style="margin:30px 0 18px;padding-left:18px;border-left:2px dotted {BLUE};"><p style="font-size:34px;line-height:1;color:{BLUE};font-weight:700;margin:0 0 8px;font-family:{FF};">{num}</p>{heading_p(text)}<p style="width:52px;height:2px;background:{BLUE};margin:11px 0 0;"></p></section>'
    if marker_id=='chapter_corner_frame': return f'<section style="margin:30px 0 18px;border-left:3px solid {BLUE};border-top:1px solid {LINE};padding:13px 0 4px 16px;"><p style="font-size:32px;line-height:1;color:{BLUE};font-weight:700;margin:0 0 8px;font-family:{FF};">{num}</p>{heading_p(text)}</section>'
    if marker_id=='chapter_double_rule': return f'<section style="margin:30px 0 18px;"><p style="font-size:34px;line-height:1;color:{BLUE};font-weight:700;margin:0 0 8px;font-family:{FF};">{num}</p>{heading_p(text)}<section style="margin:11px 0 0;"><span style="display:inline-block;width:56px;height:3px;background:{BLUE};vertical-align:middle;"></span><span style="display:inline-block;width:16px;height:3px;background:{PURPLE};margin-left:6px;vertical-align:middle;"></span></section></section>'
    if marker_id=='chapter_diamond_mark': return f'<section style="margin:30px 0 18px;"><p style="font-size:34px;line-height:1;color:{BLUE};font-weight:700;margin:0 0 8px;font-family:{FF};">{num}</p>{heading_p(text)}<p style="margin:11px 0 0;color:{BLUE};font-size:13px;line-height:1;letter-spacing:4px;">◆ ─────</p></section>'
    if marker_id=='chapter_end_signature': return f'<section style="margin:26px 0;text-align:center;"><span style="display:inline-block;width:5px;height:5px;background:{BLUE};transform:rotate(45deg);vertical-align:middle;"></span><span style="display:inline-block;width:42px;height:1px;background:{LINE};margin-left:8px;vertical-align:middle;"></span></section>'
    if marker_id=='short_double_divider': return f'<section style="margin:27px 0;text-align:center;"><span style="display:inline-block;width:48px;height:2px;background:{BLUE};vertical-align:middle;"></span><span style="display:inline-block;width:14px;height:2px;background:{PURPLE};margin-left:6px;vertical-align:middle;"></span></section>'
    if marker_id=='diamond_line_divider': return f'<section style="margin:27px 0;text-align:center;color:{BLUE};font-size:11px;line-height:1;letter-spacing:5px;">──── ◆ ────</section>'
    if marker_id=='dot_chain_divider': return f'<section style="margin:27px 0;text-align:center;"><span style="display:inline-block;width:4px;height:4px;background:{BLUE};border-radius:50%;margin:0 5px;"></span><span style="display:inline-block;width:7px;height:7px;border:1px solid {PURPLE};border-radius:50%;margin:0 5px;"></span><span style="display:inline-block;width:4px;height:4px;background:{BLUE};border-radius:50%;margin:0 5px;"></span></section>'
    if marker_id=='dual_tone_divider': return f'<section style="margin:27px 0;text-align:center;"><span style="display:inline-block;width:34px;height:2px;background:{BLUE};vertical-align:middle;"></span><span style="display:inline-block;width:34px;height:2px;background:{PURPLE};vertical-align:middle;"></span></section>'
    if marker_id=='center_node_divider': return f'<section style="margin:27px 0;text-align:center;"><span style="display:inline-block;width:42px;height:1px;background:{LINE};vertical-align:middle;"></span><span style="display:inline-block;width:8px;height:8px;border:2px solid {BLUE};border-radius:50%;margin:0 8px;vertical-align:middle;"></span><span style="display:inline-block;width:42px;height:1px;background:{LINE};vertical-align:middle;"></span></section>'
    if marker_id=='chapter_transition_divider': return f'<section style="margin:28px 0;text-align:center;"><span style="display:inline-block;width:5px;height:5px;background:{PURPLE};transform:rotate(45deg);vertical-align:middle;"></span><span style="display:inline-block;width:54px;border-top:1px dotted {BLUE};margin-left:9px;vertical-align:middle;"></span><span style="display:inline-block;width:5px;height:5px;background:{BLUE};border-radius:50%;margin-left:7px;vertical-align:middle;"></span></section>'
    if marker_id=='large_number_heading': return f'<section style="margin:24px 0 16px 0;"><p style="font-size:34px;line-height:1;color:{BLUE};font-weight:700;margin:0 0 8px 0;font-family:{FF};">{num}</p>{heading_p(text)}</section>'
    if marker_id in {'chinese_number_heading','roman_number_heading','letter_heading'}:
        seq={'chinese_number_heading':['一','二','三'],'roman_number_heading':['I','II','III'],'letter_heading':['A','B','C']}[marker_id][min(idx-1,2)]
        return f'<section style="margin:22px 0 15px 0;"><p style="font-size:13px;line-height:1.4;color:{BLUE};font-weight:700;letter-spacing:1px;margin:0 0 6px 0;font-family:{FF};">{seq}</p>{p(text,"font-size:20px;font-weight:700")}</section>'
    if marker_id=='part_heading': return f'<section style="margin:24px 0 16px 0;border-bottom:1px solid {LINE};padding-bottom:10px;"><p style="font-size:12px;line-height:1.4;color:{BLUE};font-weight:700;letter-spacing:2px;margin:0 0 5px 0;font-family:{FF};">PART {num}</p>{p(text,"font-size:20px;font-weight:700")}</section>'
    if marker_id=='centered_heading': return f'<section style="margin:24px 0 16px;text-align:center;">{p(text,"font-size:20px;font-weight:700;text-align:center")}</section>'
    if marker_id=='boxed_heading': return f'<section style="margin:24px 0 16px;border:1px solid {BLUE};border-radius:5px;padding:10px 14px;">{p(text,"font-size:19px;font-weight:700")}</section>'
    if marker_id=='bottom_line_heading': return f'<section style="margin:24px 0 16px;border-bottom:3px solid {BLUE};padding-bottom:8px;">{p(text,"font-size:20px;font-weight:700")}</section>'
    if marker_id=='eyebrow': return f'<p style="font-size:12px;line-height:1.4;color:{BLUE};font-weight:700;letter-spacing:2px;margin:18px 0 8px;font-family:{FF};">{esc(text)}</p>'
    if marker_id=='drop_cap':
        first=text[:1]; rest=text[1:]
        return f'<p style="font-size:16px;line-height:1.75;color:{TEXT};margin:16px 0;font-family:{FF};"><span style="display:inline-block;font-size:34px;line-height:1;color:{BLUE};font-weight:700;margin-right:5px;vertical-align:-3px;">{esc(first)}</span>{esc(rest)}</p>'
    box_styles={'filled_text_box':f'background:{BLUE_BG};border:1px solid #BFD1EE','top_bar_box':f'background:#FFFFFF;border:1px solid {LINE};border-top:4px solid {BLUE}','bottom_bar_box':f'background:#FFFFFF;border:1px solid {LINE};border-bottom:4px solid {BLUE}','left_bar_box':f'background:#FFFFFF;border-left:4px solid {BLUE}','dashed_border_box':f'background:#FFFFFF;border:1px dashed {BLUE}','minimal_gray_box':f'background:{GREY_BG};border:1px solid {LINE}','definition_box':f'background:{BLUE_BG};border-left:4px solid {BLUE}','fact_box':f'background:{BLUE_BG};border-left:4px solid {BLUE}','example_box':f'background:{ORANGE_BG};border-left:4px solid {ORANGE}','callout_note':f'background:{BLUE_BG};border:1px solid #BFD1EE','callout_tip':f'background:{GREEN_BG};border:1px solid {GREEN}','callout_warning':f'background:{ORANGE_BG};border:1px solid {ORANGE}','callout_important':f'background:{PURPLE_BG};border:1px solid {PURPLE}','callout_caution':f'background:{RED_BG};border:1px solid {RED}'}
    if marker_id in box_styles: return f'<section style="{box_styles[marker_id]};border-radius:7px;padding:14px 16px;margin:18px 0;">{p(text)}</section>'
    if marker_id=='paragraph_lead_symbol':
        bg,color=tone(content.get('tone','data')); variant=content.get('variant','dot')
        symbol={'dot':'●','diamond':'◆','bar':'▌'}.get(variant,'●')
        return f'<p style="font-size:16px;line-height:1.78;color:{TEXT};margin:0 0 16px;font-family:{FF};"><span style="color:{color};font-size:11px;margin-right:8px;vertical-align:2px;">{symbol}</span>{esc(text)}</p>'
    if marker_id=='key_sentence_bracket':
        bg,color=tone(content.get('tone','insight'))
        return f'<section style="margin:20px 0;padding:14px 16px;border-left:2px solid {color};border-top:2px solid {color};border-right:1px solid {LINE};border-bottom:1px solid {LINE};background:#FFFFFF;">{p(text,"font-weight:700")}</section>'
    if marker_id=='block_quote': return f'<blockquote style="background:{PALE};border-left:4px solid {GREY};padding:14px 16px;margin:18px 0;">{p(text)}</blockquote>'
    if marker_id=='pull_quote': return f'<blockquote style="background:#FFFFFF;border-top:2px solid {BLUE};border-bottom:2px solid {BLUE};padding:16px 8px;margin:22px 0;">{p(text,"font-size:19px;font-weight:700;color:#1F2937;text-align:center")}</blockquote>'
    if marker_id=='epigraph': return f'<blockquote style="background:#FFFFFF;border-bottom:1px solid {LINE};padding:10px 18px 15px;margin:18px 0;text-align:right;">{p(text,"font-size:15px;color:#555555;text-align:right")}</blockquote>'
    if marker_id=='quote_with_source': return f'<blockquote style="background:{PALE};border-left:4px solid {PURPLE};padding:14px 16px;margin:18px 0;">{p(text)}<p style="font-size:12px;line-height:1.5;color:{MUTED};margin:8px 0 0;text-align:right;font-family:{FF};">{esc(content.get("source",""))}</p></blockquote>'
    if marker_id=='centered_quote': return f'<blockquote style="background:#FFFFFF;padding:16px 20px;margin:18px 0;text-align:center;">{p(text,"font-size:18px;font-weight:700;text-align:center")}</blockquote>'
    lists={'solid_circle_list':'●','hollow_circle_list':'○','square_list':'■','triangle_list':'▲','diamond_list':'◆'}
    items=content.get('items',[]) if isinstance(content,dict) else []
    if marker_id=='question_stack':
        rows=''.join(f'<p style="font-size:16px;line-height:1.72;color:{TEXT};margin:0 0 11px;font-family:{FF};"><span style="display:inline-block;width:18px;height:18px;border:2px solid {PURPLE};border-radius:50%;margin-right:9px;vertical-align:-3px;"></span>{esc(item)}</p>' for item in items)
        return f'<section style="background:{PURPLE_BG};border-left:3px solid {PURPLE};padding:15px 16px 5px;margin:20px 0;">{rows}</section>'
    if marker_id=='parallel_sentence_rail':
        rows=''.join(f'<p style="font-size:16px;line-height:1.72;color:{TEXT};margin:0 0 10px;padding-left:18px;border-left:2px solid {BLUE_BG};font-family:{FF};"><span style="display:inline-block;width:7px;height:7px;background:{BLUE};border-radius:50%;margin-left:-23px;margin-right:14px;vertical-align:2px;"></span>{esc(item)}</p>' for item in items)
        return f'<section style="margin:19px 0;padding-left:8px;">{rows}</section>'
    if marker_id=='logic_progress_rail':
        rows=''.join(f'<p style="font-size:16px;line-height:1.72;color:{TEXT};margin:0 0 10px;padding:0 0 10px 20px;border-left:2px solid {PURPLE_BG};font-family:{FF};"><span style="display:inline-block;width:8px;height:8px;border:2px solid {PURPLE};border-radius:50%;margin-left:-25px;margin-right:13px;vertical-align:1px;background:#FFFFFF;"></span>{esc(item)}</p>' for item in items)
        return f'<section style="margin:19px 0;padding-left:8px;">{rows}</section>'
    if marker_id=='data_cluster_rail':
        rows=''.join(f'<p style="font-size:16px;line-height:1.7;color:{TEXT};margin:0;padding:11px 13px;border-bottom:1px solid {LINE};font-family:{FF};"><span style="display:inline-block;width:7px;height:7px;background:{BLUE};margin-right:10px;vertical-align:2px;"></span>{esc(item)}</p>' for item in items)
        return f'<section style="background:{BLUE_BG};border-left:3px solid {BLUE};margin:20px 0;padding:2px 10px;">{rows}</section>'
    if marker_id=='contrast_pair_plain' and len(items)>=2:
        return f'<section style="margin:20px 0;border-top:1px solid {LINE};border-bottom:1px solid {LINE};padding:12px 0;"><p style="font-size:16px;line-height:1.72;color:{TEXT};margin:0 0 10px;padding-left:13px;border-left:3px solid {BLUE};font-family:{FF};">{esc(items[0])}</p><p style="font-size:16px;line-height:1.72;color:{TEXT};margin:0;padding-left:13px;border-left:3px solid {PURPLE};font-family:{FF};">{esc(items[1])}</p></section>'
    if marker_id=='closing_focus_frame':
        bg,color=tone(content.get('tone','insight'))
        return f'<section style="margin:26px 0 8px;border-top:2px solid {color};border-bottom:1px solid {LINE};padding:18px 12px;background:{bg};"><p style="font-size:17px;line-height:1.75;color:{TEXT};font-weight:700;margin:0;text-align:center;font-family:{FF};">{esc(text)}</p></section>'
    if marker_id in lists: return f'<section style="margin:16px 0;">{list_rows(items,lists[marker_id])}</section>'
    if marker_id=='decimal_list': return f'<section style="margin:16px 0;">{list_rows(items,number=lambda i:str(i+1)+".")}</section>'
    if marker_id=='zero_padded_list': return f'<section style="margin:16px 0;">{list_rows(items,number=lambda i:f"{i+1:02d}")}</section>'
    if marker_id=='step_cards':
        rows=''.join(f'<section style="background:{PALE};border:1px solid {LINE};border-radius:7px;padding:12px 14px;margin:0 0 10px;"><p style="font-size:12px;line-height:1.4;color:{BLUE};font-weight:700;margin:0 0 5px;font-family:{FF};">STEP {i+1:02d}</p>{p(v)}</section>' for i,v in enumerate(items))
        return f'<section style="margin:18px 0;">{rows}</section>'
    if marker_id=='vertical_timeline':
        rows=''.join(f'<section style="border-left:2px solid {BLUE};padding:0 0 14px 14px;margin:0 0 0 4px;"><p style="font-size:12px;line-height:1.4;color:{BLUE};font-weight:700;margin:0 0 4px;font-family:{FF};">{i+1:02d}</p>{p(v)}</section>' for i,v in enumerate(items))
        return f'<section style="margin:18px 0;">{rows}</section>'
    if marker_id=='data_table':
        rows=content.get('rows',[]); body=''.join('<tr>'+''.join(f'<td style="font-size:14px;line-height:1.6;color:{TEXT};border:1px solid {LINE};padding:8px;">{esc(c)}</td>' for c in row[:3])+'</tr>' for row in rows[:8]); return f'<table style="border-collapse:collapse;width:100%;margin:18px 0;"><tbody>{body}</tbody></table>'
    if marker_id in {'big_number','kpi_card'}: return f'<section style="background:{BLUE_BG};border:1px solid #BFD1EE;border-radius:8px;padding:16px;margin:18px 0;text-align:center;"><p style="font-size:30px;line-height:1.1;color:{BLUE};font-weight:700;margin:0 0 7px;font-family:{FF};">{esc(content.get("value",""))}</p>{p(content.get("text",""),"font-size:13px;color:#555555;text-align:center")}</section>'
    if marker_id=='stat_strip': return f'<section style="background:{PALE};border-top:1px solid {LINE};border-bottom:1px solid {LINE};padding:12px 0;margin:18px 0;">{list_rows(content.get("items",[]),'•')}</section>'
    if marker_id=='percentage_bar':
        value=max(0,min(100,int(content.get('value',0) or 0))); return f'<section style="margin:18px 0;">{p(content.get("text",""),"font-size:14px;font-weight:700;margin-bottom:7px")}<section style="height:8px;background:{GREY_BG};border-radius:4px;"><section style="width:{value}%;height:8px;background:{BLUE};border-radius:4px;"></section></section></section>'
    if marker_id=='pros_cons': return f'<table style="border-collapse:collapse;width:100%;margin:18px 0;"><tbody><tr><td style="width:50%;background:{RED_BG};border:1px solid {LINE};padding:12px;vertical-align:top;">{p(content.get("left",""),"font-size:14px")}</td><td style="width:50%;background:{GREEN_BG};border:1px solid {LINE};padding:12px;vertical-align:top;">{p(content.get("right",""),"font-size:14px")}</td></tr></tbody></table>'
    if marker_id=='formula_block': return f'<section style="background:{PALE};border:1px solid {LINE};border-radius:6px;padding:14px 16px;margin:18px 0;text-align:center;">{p(text,"font-family:Menlo,Consolas,monospace;font-weight:700;text-align:center")}</section>'
    if marker_id=='code_block': return f'<section style="background:#1F2937;border-radius:7px;padding:14px 16px;margin:18px 0;"><p style="font-size:13px;line-height:1.7;color:#FFFFFF;margin:0;font-family:Menlo,Consolas,monospace;">{esc(text)}</p></section>'
    if marker_id in {'author_byline','publish_date','reading_time','category_marker','source_note','citation_block'}: return f'<p style="font-size:12px;line-height:1.6;color:{MUTED};margin:8px 0;font-family:{FF};">{esc(content if isinstance(content,str) else text)}</p>'
    if marker_id=='article_end_mark':
        end_text=content if isinstance(content,str) else text
        tail=p(end_text,"font-size:12px;color:#A5A5A5;text-align:center;margin-top:7px") if end_text else ''
        return f'<section style="margin:30px 0;text-align:center;"><span style="display:inline-block;font-size:14px;line-height:1.5;color:{MUTED};font-family:{FF};">◆</span>{tail}</section>'
    return ''
