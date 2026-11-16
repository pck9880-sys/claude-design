"""예시 글과 이번 시안용 생성 사진을 넣은 한 페이지. 실제 고객 원고/자산과 분리한다."""
from pathlib import Path
import json,html,base64,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/interior-sample-v002';OUT.mkdir(exist_ok=True)
PHOTO=ROOT/'links/demo-sample/generated_alley_v001.png'
colors={'ink':[38,51,44],'muted':[101,109,99],'accent':[89,108,88],'soft':[242,244,237],'line':[206,213,201],'paper':[255,255,255]}
styles={'Running':(9.5,'Regular',1.5),'Book':(11,'Bold',1.5),'Section':(10.5,'Bold',1.5),'Title':(32,'Bold',1.16),'Author':(12,'Bold',1.4),'Intro':(12,'Regular',1.55),'Caption':(10,'Regular',1.4),'QuoteLabel':(11,'Bold',1.35),'Quote':(16,'Bold',1.3),'Description':(12,'Regular',1.5),'Folio':(10,'Bold',1.4)}
items=[]
def t(x,y,w,h,text,style,color='ink',align='left',name=''):
 items.append(dict(kind='text',x=x,y=y,w=w,h=h,text=text,style=style,color=color,align=align,name=name or style))
def rect(x,y,w,h,color,name):items.append(dict(kind='block',x=x,y=y,w=w,h=h,fill=color,name=name))
def line(x,y,w):items.append(dict(kind='rule',x=x,y=y,w=w,h=.15,name='Separator'))
t(18,13,62,7,'인생사진첩','Book')
t(92,13,100,7,'프레임에 담긴 나의 세상','Running','muted','right')
line(18,24,174)
t(18,30,102,7,'작가의 시선  01','Section','accent')
t(18,41,106,33,'빛이 머문\n오래된 골목','Title')
t(132,32,60,8,'김정숙 작가','Author')
t(132,45,60,30,'익숙한 동네를 천천히 걷습니다.\n무심코 지나쳤던 풍경에서\n오래된 기억과 새로운 이야기를\n발견하는 시간이 좋습니다.','Intro','muted')
items.append(dict(kind='frame',x=18,y=84,w=174,h=130.5,asset_id='DEMO_ALLEY_01',name='DEMO_ALLEY_01'))
t(18,218,126,6,'빛이 머문 오래된 골목  ·  김정숙','Caption','muted')
t(150,218,42,6,'동네를 걷다','Caption','muted','right')
rect(0,230,210,67,'soft','작품 이야기 바탕')
t(18,240,33,17,'작가의\n한마디','QuoteLabel','accent')
t(62,239,130,20,'매일 걷던 길도,\n카메라로 바라보니 새로웠습니다.','Quote')
t(62,260,130,20,'따뜻한 햇살과 나뭇잎 그림자가 대문에 머물렀습니다.\n평범한 하루에도 오래도록 간직하고 싶은 순간이\n있다는 걸, 사진을 찍으며 새삼 알게 되었습니다.','Description','muted')
line(18,282,174)
t(18,286,27,5,'04','Folio')
t(87,286,105,5,'인생사진첩  /  프레임에 담긴 나의 세상','Running','muted','right')
asset={'id':'DEMO_ALLEY_01','kind':'demo_generated_photo','path':'links/demo-sample/generated_alley_v001.png','title':'빛이 머문 오래된 골목','status':'demo_only_not_client_work','sha256':hashlib.sha256(PHOTO.read_bytes()).hexdigest()}
layout={'project':'2026_11.16_인생사진첩','sample_only':True,'target_page':4,'state':'awaiting_user_design_review','demo_content':True,'demo_note':'작가명·소개·제목·설명은 사용자 허용에 따른 시안용 창작 예시. 사진은 이번 시안용 AI 생성이며 실제 어르신 작품이 아니다.','spec':{'width_mm':210,'height_mm':297,'bleed_mm':3,'size_confirmed':False},'pages':[{'page':4,'role':'artist','artist_id':'DEMO_AUTHOR_01','side':'left','items':items}],'styles':styles,'colors':colors,'demo_assets':[asset]}
(ROOT/'data/interior_sample_v002.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2))
(ROOT/'data/interior_sample_v002.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(layout,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
def hx(key):return '#'+''.join(f'{n:02x}' for n in colors[key])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297"><rect width="210" height="297" fill="white"/>']
for a in items:
 x,y,w,h=[a[k] for k in ('x','y','w','h')]
 if a['kind']=='text':
  pt,weight,leading=styles[a['style']];sz=pt*25.4/72;tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w;anchor={'left':'start','center':'middle','right':'end'}[a['align']]
  for i,value in enumerate(a['text'].split('\n')):
   svg.append(f'<text x="{tx}" y="{y+sz*.95+i*sz*leading}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{sz}" fill="{hx(a["color"])}" text-anchor="{anchor}">{html.escape(value)}</text>')
 elif a['kind']=='frame':
  img=base64.b64encode(PHOTO.read_bytes()).decode()
  svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{img}" preserveAspectRatio="xMidYMid meet"/>')
 else:svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx(a.get("fill","line"))}"/>')
svg.append('</svg>');(OUT/'인생사진첩_내지1p_완성형예시_v002.svg').write_text(''.join(svg))
for a in items:assert a['x']>=0 and a['y']>=0 and a['x']+a['w']<=210 and a['y']+a['h']<=297
print('한 페이지 완성형 예시 생성. 실제 고객 데이터 및 나머지 페이지 변경 없음.')
