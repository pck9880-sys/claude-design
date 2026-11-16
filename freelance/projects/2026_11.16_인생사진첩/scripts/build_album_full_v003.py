"""v007 한 장의 디자인을 전체 24쪽 편집 데이터로 확장. 원본 자료는 변경하지 않음."""
from pathlib import Path
import json,copy,html,csv
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/full-v003';OUT.mkdir(parents=True,exist_ok=True)
B=json.loads((ROOT/'data/book-data.json').read_text())
T=json.loads((ROOT/'data/interior_sample_v007.json').read_text())
L={k:copy.deepcopy(T[k]) for k in ('spec','styles','colors')}
L.update(project=B['project'],state='full_layout_missing_photos_and_copy',pages=[],demo_assets=[],demo_content=False)
L['spec'].update(page_count=24,facing_pages=True)
L['styles'].update(Title=[34,'Bold',1.3],Subtitle=[15,'Regular',1.6],PageTitle=[27,'Bold',1.4],Small=[10,'Regular',1.5],Draft=[12,'Regular',1.6],Label=[12,'Bold',1.4])
palette=['#A0896C','#82917A','#7B9290','#8293A3','#9390A2','#A18C97','#AD8F83','#A59574','#8E9A87','#92958C']
L['palette']={}
for i,h in enumerate(palette,1):
 key=f'accent_A{i:02d}';L['colors'][key]=[int(h[j:j+2],16) for j in (1,3,5)];L['palette'][f'A{i:02d}']=h
pg=None

def new(n,role,artist=None):
 global pg
 pg=dict(page=n,role=role,side='left' if n%2==0 else 'right',items=[])
 if artist:pg['artist_id']=artist
 L['pages'].append(pg)
def text(x,y,w,h,value,style='Draft',color='ink',align='left',name=None):
 pg['items'].append(dict(kind='text',x=x,y=y,w=w,h=h,text=value,style=style,color=color,align=align,name=name or style))
def block(x,y,w,h,fill='line',name='line'):
 pg['items'].append(dict(kind='block',x=x,y=y,w=w,h=h,fill=fill,stroke=None,stroke_weight=0,name=name))
def frame(x,y,w,h,aid):
 pg['items'].append(dict(kind='frame',x=x,y=y,w=w,h=h,asset_id=aid,name=aid,fit='contain',empty_frame=True))
def footer(n,accent='accent',minimal=False):
 if not minimal:
  block(25,275,161,.12)
  text(45 if n%2==0 else 25,278,55,4,B['title'],'Running','muted')
  text(100 if n%2==0 else 85,278,86 if n%2==0 else 77,4,B['subtitle'],'Running','muted','right')
 text(25 if n%2==0 else 174,277.5,12,4.5,f'{n:02d}','Folio',accent,'left' if n%2==0 else 'right',name='Folio')

# 표지는 원고대로 작가별 한 장씩 총10장. 사진은 빈 프레임.
new(1,'cover')
text(25,23,161,17,B['title'],'Title','accent')
text(25,46,161,12,B['subtitle'],'Subtitle','muted')
block(25,66,161,.2,'accent')
# 기존 표지 초안의 3열 모자이크 구조 유지, 10장 배치.
cover_cells=[0,1,3,4,5,6,7,8,10,11]
for i,a in enumerate(B['artists']):
 cell=cover_cells[i];frame(25+(cell%3)*55,79+(cell//3)*36,51,32,a['cover_asset'])
frame(25,240,12,10,'ORG_LOGO')
text(42,239,144,13,'동래구노인복지관\n재가노인지원서비스센터','Small')
frame(25,260,12,10,'SUPPORT_LOGO')
text(42,258,144,15,'본 제작물은 부산사회복지공동모금회의\n지원으로 제작되었습니다.','Small','muted')
new(2,'greeting')
text(25,25,161,16,'인사말','PageTitle','accent');block(25,49,161,.15)
text(25,67,161,160,B['greeting'] or '[센터장 인사말 원고 대기]','Draft','muted',name='GreetingCopy')
text(25,241,161,18,'동래구노인복지관\n재가노인지원서비스센터 센터장','Small','ink','right');footer(2)
new(3,'program')
text(25,25,161,16,'프로그램 소개','PageTitle','accent')
text(25,50,161,27,B['program_intro'] or '[프로그램 소개 원고 대기]','Draft','muted',name='ProgramCopy')
block(25,86,161,.15)
text(25,94,161,10,'출사 및 스토리텔링','Label','accent')
for i in range(8):
 x=25+(i%2)*83;y=111+(i//2)*20
 text(x,y,10,7,f'{i+1:02d}','Label','accent')
 text(x+15,y,63,12,B['sessions'][i] or '[회기 주제]','Small','muted',name=f'Session_{i+1}')
for i in range(3):frame(25+i*55,205,51,48,f'ACT{i+1:02d}')
footer(3)

for i,a in enumerate(B['artists']):
 n=4+2*i;new(n,'artist',a['id']);pg['items']=copy.deepcopy(T['pages'][0]['items'])
 accent='accent_'+a['id'];asset=next(v for v in B['assets'] if v['id']==a['left_asset'])
 for it in pg['items']:
  if it.get('color')=='accent':it['color']=accent
  if it.get('fill')=='accent':it['fill']=accent
  if it.get('stroke')=='accent':it['stroke']=accent
  if it['kind']=='frame':it.update(asset_id=a['left_asset'],name=a['left_asset'])
  if it['name']=='Caption':it['text']=asset['title'] or '[작품 제목]'
  if it['name']=='Author':it['text']=(a['name']+' 작가') if a['name'] else '[작가 성함]'
  if it['name']=='Intro':it['text']=a['bio'] or '[작가소개 원고 대기]'
  if it['name']=='SideTitle':it['text']='작품에\n담긴\n이야기'
  if it['name']=='Body':it['text']=asset['description'] or '[작품 설명 원고 대기]'
  if it['name']=='Quote':it['text']='[원고 대기]'
  if it.get('style')=='Folio':it['text']=f'{n:02d}'
 new(n+1,'artist',a['id'])
 # Right-hand page: artwork only, no duplicated biography, caption, running title or decorative corners.
 frame(25,25,161,239,a['right_asset']);footer(n+1,accent,minimal=True)
new(24,'closing')
text(25,25,161,16,'함께한 순간들','PageTitle','accent')
for i in range(6):frame(25+(i%2)*83,54+(i//2)*40,78,35,f'ACT{i+4:02d}')
text(25,185,161,9,'함께해 주신 분들','Label','accent')
text(25,201,161,24,B['contributors'] or '[참여 어르신 · 강사 · 봉사자 명단 대기]','Draft','muted')
block(25,239,161,.15)
text(25,246,161,13,'동래구노인복지관\n재가노인지원서비스센터','Small')
text(25,264,161,8,B['organization_info'] or '[기관 정보 대기]','Small','muted')
footer(24)
# Layout invariants: all elements inside 15mm margins and parity-correct folios.
assert len(L['pages'])==24
for page in L['pages']:
 for it in page['items']:
  sw=it.get('stroke_weight',0)*25.4/72/2
  assert it['x']-sw>=15 and it['y']-sw>=15,(page['page'],it)
  assert it['x']+it['w']+sw<=195 and it['y']+it['h']+sw<=282,(page['page'],it)
 for it in page['items']:
  if it.get('style')=='Folio':assert it['align']==('left' if page['page']%2==0 else 'right')
 if page['role']=='artist' and page['side']=='right':
  assert len(page['items'])==2 and page['items'][0]['kind']=='frame'
assert not any('김정숙' in it.get('text','') for p in L['pages'] for it in p['items'])
(ROOT/'data/layout_full_v003.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
(ROOT/'data/layout_full_v003.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(L,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
def hx(key):return '#'+''.join(f'{v:02x}' for v in L['colors'][key])
def page_svg(page,offset=0):
 s=[f'<g transform="translate({offset},0)"><rect width="210" height="297" fill="white"/>']
 for a in page['items']:
  x,y,w,h=[a[k] for k in ('x','y','w','h')]
  if a['kind']=='text':
   pt,weight,leading=L['styles'][a['style']];sz=pt*25.4/72
   tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w
   anchor={'left':'start','center':'middle','right':'end'}[a['align']]
   for i,value in enumerate(a['text'].split('\n')):
    s.append(f'<text x="{tx}" y="{y+sz*.95+i*sz*leading}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{sz}" fill="{hx(a["color"])}" text-anchor="{anchor}">{html.escape(value)}</text>')
  elif a['kind']=='frame':s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx("soft")}" stroke="{hx("line")}" stroke-width="0.12"/>')
  else:s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx(a["fill"]) if a.get("fill") else "none"}" stroke="{hx(a["stroke"]) if a.get("stroke") else "none"}" stroke-width="{a.get("stroke_weight",0)*25.4/72}"/>')
 return ''.join(s)+'</g>'
for page in L['pages']:(OUT/f'page-{page["page"]:02d}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'+page_svg(page)+'</svg>')
for left in range(2,24,2):(OUT/f'spread-{left:02d}-{left+1:02d}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="422mm" height="297mm" viewBox="0 0 422 297"><rect width="422" height="297" fill="#e8e8e8"/>'+page_svg(L['pages'][left-1])+page_svg(L['pages'][left],212)+'</svg>')
with (OUT/'page-map.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['page','role','side','artist_id','color','photo_ids'])
 for pg in L['pages']:writer.writerow([pg['page'],pg['role'],pg['side'],pg.get('artist_id',''),L['palette'].get(pg.get('artist_id',''),''),' '.join(it['asset_id'] for it in pg['items'] if it['kind']=='frame')])
print('24쪽 구성·15mm 여백·10개 작가 펼침면·바깥쪽 쪽번호·우측 사진 전용·예시 인명 미포함 확인')
