"""24쪽 편집 좌표·SVG 검토도·InDesign DOM 스크립트용 데이터를 작성한다."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/'output/v002';PREVIEW.mkdir(parents=True,exist_ok=True)
B=json.loads((ROOT/'data/book-data.json').read_text())
MM=72/25.4;W=210*MM;H=297*MM
NS='http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging'
DOM='7.5';N={'idPkg':NS};P=[];pg=None
INK='ink';MUTED='muted';COL=B['colors']
STYLES={'BookTitle':(38,'Bold'),'Subtitle':(14,'Regular'),'PageTitle':(27,'Bold'),'AuthorName':(26,'Bold'),'Section':(17,'Bold'),'WorkTitle':(18,'Bold'),'Body':(14,'Regular'),'Caption':(13,'Regular'),'Small':(10.5,'Regular'),'Folio':(10,'Regular'),'Placeholder':(11,'Regular')}
def text(x,y,w,h,value,style='Body',color=INK,align='left',name=''):
 pg['items'].append(dict(kind='text',x=x,y=y,w=w,h=h,text=value,style=style,color=color,align=align,name=name or style))
def frame(x,y,w,h,asset_id,label='작품 사진'):
 pg['items'].append(dict(kind='frame',x=x,y=y,w=w,h=h,asset_id=asset_id,name=asset_id))
 if label:text(x+3,y+h/2-6,w-6,15,label+'\n'+asset_id,'Placeholder',MUTED,'center','Placeholder_'+asset_id)
def rule(x,y,w):pg['items'].append(dict(kind='rule',x=x,y=y,w=w,h=.2,name='Separator'))
def page(n,role):
 global pg
 pg={'page':n,'role':role,'items':[]};P.append(pg)
def folio(n):
 text(20,280,100,6,'인생사진첩','Small',MUTED)
 text(168,280,22,6,f'{n:02d}','Folio',MUTED,'right')
page(1,'cover')
text(20,20,170,18,B['title'],'BookTitle',INK,'center')
text(20,43,170,10,B['subtitle'],'Subtitle',MUTED,'center')
cover_cells=[0,1,3,4,5,6,7,8,10,11]
for i,cell in enumerate(cover_cells):frame(20+(cell%3)*59,66+(cell//3)*43,52,37,B['artists'][i]['cover_asset'],'표지 작품 사진')
frame(20,244,12,10,'ORG_LOGO','')
text(37,244,153,13,B['organization'],'Small',INK,'left')
frame(20,263,12,10,'SUPPORT_LOGO','')
text(37,261,153,13,B['support_note'],'Small',MUTED,'left')
text(20,278,170,6,'기관·지원 로고 원본 대기','Small',MUTED,'center')
page(2,'greeting');text(20,24,170,17,'인사말','PageTitle')
rule(20,48,170)
text(20,65,170,175,B['greeting'] or '[센터장 인사말 원고가 들어갈 자리]','Body',MUTED)
text(20,253,170,16,B['organization']+'\n센터장','Small',INK,'right');folio(2)
page(3,'program');text(20,24,170,17,'프로그램 소개','PageTitle')
text(20,52,170,35,B['program_intro'] or '[프로그램 소개 원고가 들어갈 자리]','Body',MUTED)
text(20,96,170,12,'출사 및 스토리텔링','Section');rule(20,112,170)
for i in range(8):text(20,119+i*7.7,170,7,f'{i+1:02d}   '+(B['sessions'][i] or '[회기 주제 대기]'),'Caption',MUTED)
for i in range(3):frame(20+i*59,191,52,61,'ACT0'+str(i+1),'활동 사진')
folio(3)
# 두 가지 펼침면 변형. 실제 작품 방향을 받은 뒤 데이터에서 재지정한다.
for i,a in enumerate(B['artists']):
 variant='wide' if i%2==0 else 'portrait'
 for side in range(2):
  n=4+2*i+side;page(n,'artist');pg.update(artist_id=a['id'],side='left' if side==0 else 'right',layout=variant)
  aid=a['left_asset'] if side==0 else a['right_asset'];art=next(x for x in B['assets'] if x['id']==aid)
  if side==0:
   text(20,23,170,17,a['name'] or '[작가명]','AuthorName')
   text(20,47,170,22,a['bio'] or '[작가소개 원고가 들어갈 자리]','Caption',MUTED)
   if variant=='wide':frame(20,88,170,114,aid,'작품 사진')
   else:frame(46,78,118,157,aid,'작품 사진')
  else:
   text(20,25,170,9,B['title'],'Small',MUTED)
   if variant=='wide':frame(36,49,138,184,aid,'작품 사진')
   else:frame(20,79,170,128,aid,'작품 사진')
  cy=238 if (side==1 and variant=='wide') or (side==0 and variant=='portrait') else 221
  text(20,cy,170,11,art['title'] or '[작품 제목]','WorkTitle')
  text(20,cy+15,170,23,art['description'] or '[작품 설명 원고가 들어갈 자리]','Caption',MUTED)
  folio(n)
page(24,'closing');text(20,24,170,17,'함께한 순간들','PageTitle')
for i in range(6):frame(20+(i%2)*89,53+(i//2)*47,81,40,'ACT0'+str(i+4),'활동 사진')
text(20,205,170,27,B['contributors'] or '[참여 어르신·강사·봉사자 명단 대기]','Caption',MUTED)
rule(20,244,170);text(20,251,170,13,B['organization'],'Small')
text(20,270,170,13,B['organization_info'] or '[기관 정보 대기]','Small',MUTED)
(ROOT/'data/layout_v002.json').write_text(json.dumps({'pages':P,'spec':B['spec'],'status':'draft_missing_inputs'},ensure_ascii=False,indent=2))

layout={'pages':P,'spec':B['spec'],'styles':STYLES,'colors':COL,'status':'draft_missing_inputs'}
(ROOT/'data/layout_v002.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(layout,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
# SVGs visualize exactly the same native frame coordinates. No external images loaded.
def hx(name):return '#'+''.join(f'{c:02x}' for c in COL[name])
def page_svg(n,offset=0):
 content=[f'<g transform="translate({offset},0)"><rect width="210" height="297" fill="white"/>']
 for a in P[n-1]['items']:
  x,y,w,h=[a[k] for k in ('x','y','w','h')]
  if a['kind']!='text':
   content.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx("soft" if a["kind"]=="frame" else "line")}" stroke="{hx("line")}" stroke-width="0.18"/>')
  else:
   size,weight=STYLES[a['style']];s=size*25.4/72;tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w;anchor={'left':'start','center':'middle','right':'end'}[a['align']]
   for i,line in enumerate(a['text'].split('\n')):
    content.append(f'<text x="{tx}" y="{y+s*.95+i*s*1.5}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{s}" text-anchor="{anchor}" fill="{hx(a["color"])}">{html.escape(line)}</text>')
 content.append('</g>');return ''.join(content)
for n in range(1,25):
 (PREVIEW/f'page-{n:02d}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297">'+page_svg(n)+'</svg>')
for left in range(2,24,2):
 (PREVIEW/f'spread-{left:02d}-{left+1:02d}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 422 297"><rect width="422" height="297" fill="#dddddd"/>'+page_svg(left)+page_svg(left+1,212)+'</svg>')

print('24쪽 내지 포함 배치 데이터·SVG 검토도·JSX include 생성 완료')
