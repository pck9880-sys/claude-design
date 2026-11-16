"""사용자 검토용 내지 한 페이지. 다른 23쪽에는 적용하지 않는다."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/interior-sample-v001'
OUT.mkdir(exist_ok=True)
colors={'ink':[32,45,43],'muted':[99,111,107],'accent':[96,128,121],'soft':[238,242,240],'line':[210,220,216]}
styles={'Running':(9.5,'Regular'),'Section':(11,'Bold'),'Author':(30,'Bold'),'Intro':(13,'Regular'),'WorkTitle':(19,'Bold'),'Description':(13.5,'Regular'),'Folio':(10.5,'Regular'),'PhotoNote':(10.5,'Regular')}
items=[]
def t(x,y,w,h,text,style,color='ink',align='left',name=''):
 items.append(dict(kind='text',x=x,y=y,w=w,h=h,text=text,style=style,color=color,align=align,name=name or style))
def line(x,y,w):items.append(dict(kind='rule',x=x,y=y,w=w,h=.15,name='Separator'))
t(19,14,122,6,'프레임에 담긴 나의 세상','Running','muted')
t(157,14,34,6,'인생사진첩','Running','muted','right')
line(19,25,172)
t(19,35,172,7,'작가 소개','Section','accent')
t(19,47,172,17,'작가 성함','Author')
t(19,70,172,15,'[작가소개글 자리]\n[추후 전달되는 원고로 교체]','Intro','muted')
items.append(dict(kind='frame',x=19,y=101,w=172,h=129,asset_id='W01',name='W01'))
t(28,160,154,8,'작품 사진이 들어갈 자리','PhotoNote','muted','center','Placeholder_W01')
t(19,242,34,8,'작품 소개','Section','accent')
t(60,239,131,11,'작품 제목','WorkTitle')
t(60,254,131,17,'[작품 설명글 자리]\n[사진에 담긴 이야기를 넣는 영역]','Description','muted')
line(19,279,172)
t(19,284,13,6,'04','Folio','ink')
t(150,284,41,6,'인생사진첩','Running','muted','right')
layout={'project':'2026_11.16_인생사진첩','sample_only':True,'target_page':4,'state':'awaiting_user_design_review','spec':{'width_mm':210,'height_mm':297,'bleed_mm':3,'size_confirmed':False},'pages':[{'page':4,'role':'artist','artist_id':'A01','side':'left','items':items}],'styles':styles,'colors':colors}
(ROOT/'data/interior_sample_v001.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2))
(ROOT/'data/interior_sample_v001.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(layout,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
def hx(key):return '#'+''.join(f'{n:02x}' for n in colors[key])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297"><rect width="210" height="297" fill="white"/>']
for a in items:
 x,y,w,h=[a[k] for k in ('x','y','w','h')]
 if a['kind']=='text':
  pt,weight=styles[a['style']];sz=pt*25.4/72;tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w;anchor={'left':'start','center':'middle','right':'end'}[a['align']]
  for i,value in enumerate(a['text'].split('\n')):
   svg.append(f'<text x="{tx}" y="{y+sz*.95+i*sz*1.5}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{sz}" fill="{hx(a["color"])}" text-anchor="{anchor}">{html.escape(value)}</text>')
 else:svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx("soft" if a["kind"]=="frame" else "line")}"/>')
svg.append('</svg>');(OUT/'인생사진첩_내지1p_디자인시안_v001.svg').write_text(''.join(svg))
for a in items:assert a['x']>=0 and a['y']>=0 and a['x']+a['w']<=210 and a['y']+a['h']<=297
print('내지 4p 한 장 시안·InDesign 데이터 생성. 다른 페이지 적용 없음.')
