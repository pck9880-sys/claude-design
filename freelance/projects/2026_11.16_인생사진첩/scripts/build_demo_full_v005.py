"""사용자 허용 예시 원고/생성 사진으로 full-v004 전체24쪽 시안을 채운다."""
from pathlib import Path
import json,copy,html,csv
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/full-demo-v005';OUT.mkdir(parents=True,exist_ok=True)
L=json.loads((ROOT/'data/layout_full_v004.json').read_text())
D=json.loads((ROOT/'data/demo_content_v005.json').read_text())
L.update(demo_content=True,state='illustrative_demo_not_client_original',demo_assets=D['assets'])
L['styles']['RightTitle']=[18,'Bold',1.4]
L['styles']['DemoNote']=[8.5,'Regular',1.4]
assets={a['id']:a for a in D['assets']}
art={a['id']:a for a in D['artworks']}
authors={a['id']:a for a in D['authors']}
def text(x,y,w,h,value,style='Draft',color='ink',name=''):
 return dict(kind='text',x=x,y=y,w=w,h=h,text=value,style=style,color=color,align='left',name=name or style)
for page in L['pages']:
 n=page['page']
 for a in page['items']:
  if a['kind']=='frame':
   old=a['asset_id']
   if old.startswith(('W','ACT')):
    a['asset_id']='DEMO_'+old;a['name']=a['asset_id'];a['empty_frame']=False
    a['sheet_crop']=assets[a['asset_id']]['sheet_crop'];a['fit']='sheet_crop'
  if a['kind']!='text':continue
  name=a['name']
  if n==2 and name=='GreetingCopy':a['text']=D['greeting']
  if n==3 and name=='ProgramCopy':a['text']=D['program_intro']
  if n==3 and name.startswith('Session_'):a['text']=D['sessions'][int(name.split('_')[1])-1]
  if n==24 and a['text'].startswith('[참여'):a['text']='참여 작가  김정숙 · 박영수 · 이순자 · 최정호 · 정옥희\n강명자 · 윤상철 · 장미숙 · 한정희 · 오영호\n사진 강사  이다은    활동 지원  함께걷기 봉사단'
  if n==24 and a['text'].startswith('[기관'):a['text']='일상의 발견을 함께 나누는 사진·이야기 활동'
 if page['role']=='artist':
  au=authors[page['artist_id']]
  if page['side']=='left':
   w=art[f'DEMO_W{n-3:02d}']
   for a in page['items']:
    if a['kind']!='text':continue
    if a['name']=='Author':a['text']=au['name']+' 작가'
    if a['name']=='Intro':a['text']=au['bio']
    if a['name']=='SideTitle':a['text']=au['side_title']
    if a['name']=='Caption':a['text']='작품 01  /  '+w['title']
    if a['name']=='Body':a['text']=w['description'].split('.')[0]+'. 그 순간의 마음을 담았습니다.'
    if a['name']=='Quote':a['text']=au['quote']
  else:
   w=art[f'DEMO_W{n-3:02d}']
   for a in page['items']:
    if a['name']=='RightWorkDescription':a.update(y=39,h=18,text=w['description'])
    if a['kind']=='frame':a.update(y=65,h=199)
   page['items'].insert(0,text(25,25,161,10,w['title'],'RightTitle','accent_'+page['artist_id'],'RightWorkTitle'))
 if n==1:
  # 원본 로고 미수신: 실제 로고를 위조하지 않고 기관/지원 명칭을 임시 문자표기로 유지.
  page['items']=[a for a in page['items'] if a.get('asset_id') not in ('ORG_LOGO','SUPPORT_LOGO')]
  page['items'].append(text(25,239,14,14,'동래구\n노인\n복지관','DemoNote','accent','TemporaryOrgWordmark'))
  page['items'].append(text(25,259,14,14,'사랑의\n열매','DemoNote','accent','TemporarySupportWordmark'))
 if n in (1,24):page['items'].append(text(25,16,161,5,'사진·인명·본문은 디자인 검토용 예시입니다.','DemoNote','muted','DemoContentNote'))
# 줄바꿈은 승인 폰트 실측치로 정리. 원본 예시문구는 별도 JSON에 보존.
repo=ROOT.parents[2]
fonts={name:TTFont(repo/f'assets/fonts/Pretendard/Pretendard-{name}.ttf') for name in ('Regular','Bold')}
def width(s,style):
 pt,weight,_=L['styles'][style];f=fonts[weight];cm=f.getBestCmap();hm=f['hmtx'].metrics
 return sum(hm[cm.get(ord(c),'.notdef')][0] for c in s)/f['head'].unitsPerEm*pt*25.4/72
def wrap(s,style,w):
 lines=[]
 for line in s.split('\n'):
  if not line:lines.append('');continue
  current=''
  for ch in line:
   if width(current+ch,style)>w and current:
    # Prefer word spaces, but allow Korean character wrapping for a long word.
    split=current.rfind(' ')
    if split>len(current)//2:lines.append(current[:split]);current=current[split+1:]+ch
    else:lines.append(current);current=ch.lstrip()
   else:current+=ch
  lines.append(current.rstrip())
 return '\n'.join(lines)
errors=[]
for page in L['pages']:
 for a in page['items']:
  if a['kind']=='text':
   a['text']=wrap(a['text'],a['style'],a['w'])
   pt,_,leading=L['styles'][a['style']]
   height=(.95+(len(a['text'].split('\n'))-1)*leading)*pt*25.4/72
   if height>a['h']+.05:errors.append((page['page'],a['name'],round(height,2),a['h']))
  assert a['x']>=15 and a['y']>=15 and a['x']+a['w']<=195 and a['y']+a['h']<=282
  assert '[' not in a.get('text',''),(page['page'],a)
 if page['role']=='artist' and page['side']=='right':
  assert len([a for a in page['items'] if a['name']=='RightWorkTitle'])==1
assert len(L['pages'])==24
if errors:raise ValueError(errors)
(ROOT/'data/layout_demo_full_v005.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
(ROOT/'data/layout_demo_full_v005.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(L,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
def hx(k):return '#'+''.join(f'{v:02x}' for v in L['colors'][k])
def page_svg(page,offset=0):
 s=[f'<g transform="translate({offset},0)"><rect width="210" height="297" fill="white"/>']
 for idx,a in enumerate(page['items']):
  x,y,w,h=[a[k] for k in ('x','y','w','h')]
  if a['kind']=='text':
   pt,weight,leading=L['styles'][a['style']];sz=pt*25.4/72
   tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w
   anchor={'left':'start','center':'middle','right':'end'}[a['align']]
   for i,line in enumerate(a['text'].split('\n')):s.append(f'<text x="{tx}" y="{y+sz*.95+i*sz*leading}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{sz}" fill="{hx(a["color"])}" text-anchor="{anchor}">{html.escape(line)}</text>')
  elif a['kind']=='frame':
   asset=assets[a['asset_id']];cx,cy,cw,ch=asset['sheet_crop'];pw,ph=asset['pixel_width'],asset['pixel_height']
   scale=max(w/(pw*cw),h/(ph*ch));iw,ih=pw*scale,ph*scale
   ix=x+w/2-(cx+cw/2)*iw;iy=y+h/2-(cy+ch/2)*ih
   clip=f'crop{page["page"]}_{idx}';href='../../'+asset['path']
   s.append(f'<defs><clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{clip})"><image x="{ix}" y="{iy}" width="{iw}" height="{ih}" xlink:href="{href}"/></g>')
  else:s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx(a["fill"]) if a.get("fill") else "none"}" stroke="{hx(a["stroke"]) if a.get("stroke") else "none"}" stroke-width="{a.get("stroke_weight",0)*25.4/72}"/>')
 return ''.join(s)+'</g>'
for pg in L['pages']:(OUT/f'page-{pg["page"]:02d}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="210mm" height="297mm" viewBox="0 0 210 297">'+page_svg(pg)+'</svg>')
for left in range(2,24,2):(OUT/f'spread-{left:02d}-{left+1:02d}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="422mm" height="297mm" viewBox="0 0 422 297"><rect width="422" height="297" fill="#e8e8e8"/>'+page_svg(L['pages'][left-1])+page_svg(L['pages'][left],212)+'</svg>')
print('24쪽·작가10명/20작품·모든 대기문구 교체·우측 제목/설명·텍스트 폭/높이·15mm 검사 완료')
