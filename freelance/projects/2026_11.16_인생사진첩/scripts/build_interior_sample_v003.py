"""사용자가 준 편집 레퍼런스를 반영한 내지 한 장. 다른 페이지에는 적용하지 않는다."""
from pathlib import Path
import json,html,base64
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/interior-sample-v003';OUT.mkdir(exist_ok=True)
PHOTO=ROOT/'links/demo-sample/generated_alley_v001.png'
colors={'ink':[65,60,53],'muted':[119,111,100],'accent':[160,137,108],'line':[196,182,163],'soft':[244,240,233],'paper':[255,255,255],'white':[255,255,255],'scrim':[83,73,58]}
styles={'Running':(9.5,'Regular',1.5),'Book':(10,'Bold',1.4),'PhotoTitle':(12,'Bold',1.35),'CircleText':(20,'Bold',1.2),'SideTitle':(17,'Bold',1.25),'Author':(14,'Bold',1.45),'Intro':(12,'Regular',1.55),'Section':(10.5,'Bold',1.45),'Body':(11.5,'Regular',1.6),'Quote':(13,'Bold',1.5),'Caption':(9,'Regular',1.4),'Folio':(10.5,'Bold',1.5)}
items=[]
def t(x,y,w,h,text,style,color='ink',align='left',name=''):
 items.append(dict(kind='text',x=x,y=y,w=w,h=h,text=text,style=style,color=color,align=align,name=name or style))
def r(x,y,w,h,color='accent',name='line',stroke=None,weight=0):items.append(dict(kind='block',x=x,y=y,w=w,h=h,fill=color,stroke=stroke,stroke_weight=weight,name=name))
def ellipse(cx,cy,d,fill=None,stroke=None,weight=0,opacity=100,name='circle'):
 items.append(dict(kind='ellipse',x=cx-d/2,y=cy-d/2,w=d,h=d,fill=fill,stroke=stroke,stroke_weight=weight,opacity=opacity,name=name))
# Reference: open corner rules outside a large near-square photo.
t(137,9,53,6,'인생사진첩','Book','accent','right')
r(17,17,28,.16);r(17,17,.16,21)
r(24,21,10,.12,'line');r(24,21,.12,8,'line')
items.append(dict(kind='frame',x=25,y=25,w=165,h=153,asset_id='DEMO_ALLEY_01',name='DEMO_ALLEY_01',fit='fill',demo_crop_only=True))
# White geometric lettering echoes the reference; content stays relevant to the anthology.
for i,ch in enumerate('나의시선'):
 cy=47+i*35
 ellipse(42,cy,19,'scrim',None,0,28,'circle_scrim_'+str(i))
 ellipse(42,cy,19,None,'white',.75,100,'circle_outline_'+str(i))
 ellipse(42,cy,22.5,None,'white',.25,100,'circle_outer_'+str(i))
 t(34,cy-4.4,16,11,ch,'CircleText','white','center','circle_letter_'+str(i))
t(78,34,103,8,'빛이 머문 오래된 골목','PhotoTitle','white','right')
r(194,163,.16,22);r(174,185,20,.16)
t(25,182,155,6,'작품 01  /  빛이 머문 오래된 골목','Caption','muted')
# Lower editorial grid: slender framed title rail, introduction and two text columns.
r(17,198,32,77,'paper','framed_side_title','accent',.45)
t(21,204,24,40,'평범한\n하루를\n새롭게\n바라보다','SideTitle','accent')
for i in range(3):ellipse(23,260+i*4,1.2,'accent',None,0,100,'side_dot_'+str(i))
t(60,198,130,9,'김정숙 작가','Author','accent')
t(60,211,130,22,'익숙한 동네를 천천히 걷습니다.\n무심코 지나쳤던 풍경에서 오래된 기억과\n새로운 이야기를 발견하는 시간이 좋습니다.','Intro','ink')
r(60,238,130,.14,'line')
t(60,245,61,8,'사진에 담은 순간','Section','accent')
t(60,256,61,24,'낮은 담장 위로 햇살이\n내려앉았습니다. 오래된 대문과\n화분 사이에서 잠시 발걸음을\n멈추었습니다.','Body','muted')
t(132,245,58,8,'작가의 한마디','Section','accent')
t(132,256,58,26,'“매일 걷던 길도,\n카메라로 바라보니\n새로웠습니다.”','Quote','ink')
r(17,285,173,.12,'line')
t(17,288,50,5,'인생사진첩','Running','muted')
t(65,288,105,5,'프레임에 담긴 나의 세상','Running','muted','right')
t(178,287.5,12,6,'04','Folio','accent','right')
previous=json.loads((ROOT/'data/interior_sample_v002.json').read_text())
layout={'project':'2026_11.16_인생사진첩','sample_only':True,'target_page':4,'state':'awaiting_user_direction_check','demo_content':True,'reference':'2026-11-16 user-supplied editorial photo/circle/ruled-grid image','palette_name':'작가01 샌드 브라운 제안','author_color_strategy':'작가별 명도·채도가 비슷한 저채도 포인트색 사용. 현재 한 작가의 한 장만 제작.','spec':{'width_mm':210,'height_mm':297,'bleed_mm':3,'size_confirmed':False},'pages':[{'page':4,'role':'artist','artist_id':'DEMO_AUTHOR_01','side':'left','items':items}],'styles':styles,'colors':colors,'demo_assets':previous['demo_assets'],'demo_note':previous['demo_note']}
(ROOT/'data/interior_sample_v003.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2))
(ROOT/'data/interior_sample_v003.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(layout,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
def hx(key):return '#'+''.join(f'{n:02x}' for n in colors[key])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297"><rect width="210" height="297" fill="white"/>']
for a in items:
 x,y,w,h=[a[k] for k in ('x','y','w','h')]
 if a['kind']=='text':
  pt,weight,leading=styles[a['style']];sz=pt*25.4/72;tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w;anchor={'left':'start','center':'middle','right':'end'}[a['align']]
  for i,value in enumerate(a['text'].split('\n')):
   svg.append(f'<text x="{tx}" y="{y+sz*.95+i*sz*leading}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{sz}" fill="{hx(a["color"])}" text-anchor="{anchor}">{html.escape(value)}</text>')
 elif a['kind']=='frame':
  img=base64.b64encode(PHOTO.read_bytes()).decode();svg.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden"><image width="{w}" height="{h}" href="data:image/png;base64,{img}" preserveAspectRatio="xMidYMid slice"/></svg>')
 else:
  fill=hx(a['fill']) if a.get('fill') else 'none';stroke=hx(a['stroke']) if a.get('stroke') else 'none';sw=a.get('stroke_weight',0)*25.4/72
  attr=f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{a.get("opacity",100)/100}"'
  if a['kind']=='ellipse':svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" {attr}/>')
  else:svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {attr}/>')
svg.append('</svg>');(OUT/'인생사진첩_내지1p_레퍼런스반영_v003.svg').write_text(''.join(svg))
for a in items:assert a['x']>=0 and a['y']>=0 and a['x']+a['w']<=210 and a['y']+a['h']<=297
print('레퍼런스 반영 한 장 시안 작성. 샌드 브라운 1인 예시, 전체 적용 없음.')
