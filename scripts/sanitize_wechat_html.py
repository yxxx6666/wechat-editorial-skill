#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, html, re
from html.parser import HTMLParser
from pathlib import Path
ALLOWED={'section','p','span','strong','br','img','blockquote','table','tbody','tr','td'}
DROP={'style','script','html','head','body'}
VOID={'br','img'}
ALLOWED_ATTRS={'style','src','alt','colspan','rowspan'}
SAFE_CSS={'font-size','font-weight','line-height','color','background','background-color','border','border-left','border-right','border-top','border-bottom','border-radius','padding','padding-left','padding-right','padding-top','padding-bottom','margin','margin-left','margin-right','margin-top','margin-bottom','text-align','letter-spacing','width','max-width','height','display','vertical-align','border-collapse','text-decoration','text-decoration-color','text-decoration-style','text-decoration-thickness'}
BAD_CSS_RE=[r'display\s*:\s*(flex|grid)',r'position\s*:\s*(absolute|fixed|sticky)',r'animation\s*:',r'transition\s*:',r'@keyframes',r':hover',r'var\s*\(',r'url\s*\(\s*data:']
def clean_style(style):
    style=(style or '').replace('\xa0',' ').replace('\u2002',' ').replace('\u2003',' ')
    low=style.lower()
    if any(re.search(p, low) for p in BAD_CSS_RE): return ''
    out=[]
    for part in style.split(';'):
        if ':' not in part: continue
        k,v=part.split(':',1); k=k.strip().lower(); v=v.strip()
        if k not in SAFE_CSS or k.startswith('--'): continue
        if k=='display' and v.lower() not in {'block','inline-block'}: continue
        out.append(f'{k}:{v}')
    return ';'.join(out)
class S(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=False); self.out=[]; self.drop=[]
    def handle_starttag(self, tag, attrs):
        tag=tag.lower()
        if tag in DROP: self.drop.append(tag); return
        if self.drop: return
        if tag not in ALLOWED: return
        clean=[]
        for k,v in attrs:
            k=k.lower(); v=v or ''
            if k in {'class','id'} or k.startswith('data-') or k.startswith('on'): continue
            if k not in ALLOWED_ATTRS: continue
            if k=='src' and (re.search(r'javascript\s*:',v,re.I) or 'base64' in v.lower() or v.lower().startswith('data:')): continue
            if k=='style':
                v=clean_style(v)
                if not v: continue
            clean.append((k,v))
        self.out.append('<'+tag+''.join(f' {k}="{html.escape(v, quote=True)}"' for k,v in clean)+'>')
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag, attrs)
    def handle_endtag(self, tag):
        tag=tag.lower()
        if self.drop:
            if tag==self.drop[-1]: self.drop.pop()
            return
        if tag in ALLOWED and tag not in VOID: self.out.append(f'</{tag}>')
    def handle_data(self, data):
        if not self.drop: self.out.append(html.escape(data.replace('\xa0',' ').replace('\u2002',' ').replace('\u2003',' '), quote=False))
    def handle_entityref(self, name): self.out.append(' ' if name in {'nbsp','ensp','emsp'} else html.escape('&'+name+';', quote=False))
    def handle_charref(self, name): self.out.append(' ' if name.lower() in {'160','xa0','8194','2002','8195','2003'} else html.escape('&#'+name+';', quote=False))
def sanitize(text): p=S(); p.feed(text); return ''.join(p.out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('-o','--output')
    args=ap.parse_args(); out=sanitize(Path(args.input).read_text(encoding='utf-8'))
    if args.output: Path(args.output).write_text(out, encoding='utf-8')
    else: print(out)
if __name__=='__main__': main()
