"""1쪽 템플릿: 사진/하단 박스 왼쪽선 정렬, 좌우 바깥쪽 쪽번호."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/interior-sample-v005';OUT.mkdir(exist_ok=True)
b=json.loads((ROOT/'data/interior_sample_v004.json').read_text())
page=b['pages'][0];items=page['items']
page['side']='left' if page['page']%2==0 else 'right'
b['spec']['folio_position']='outside: even-left, odd-right'
for a in items:
 if a['name']=='framed_side_title':a['x']=25
 if a['name']=='SideTitle':a['x']=29
 if a['name']=='line' and a['y']==275:a.update(x=25,w=165)
 if a.get('style')=='Running' and a['text']=='인생사진첩':a.update(x=45,w=50)
 if a.get('style')=='Running' and a['text']=='프레임에 담긴 나의 세상':a.update(x=100,w=90)
 if a.get('style')=='Folio':a.update(x=25 if page['side']=='left' else 178,align='left' if page['side']=='left' else 'right')
assert next(a['x'] for a in items if a['kind']=='frame')==next(a['x'] for a in items if a['name']=='framed_side_title')
b['state']='single_page_15mm_template_photo_pending'
b['spec']['margin_mm']={'top':15,'bottom':15,'left':15,'right':15}
b['demo_assets']=[]
b['demo_note']='사진은 나중에 삽입할 빈 프레임. 작가명·소개·작품 문구는 기존 사용자 허용 예시를 유지.'
b['styles'].pop('CircleText',None);b['styles'].pop('PhotoTitle',None)
(ROOT/'data/interior_sample_v005.json').write_text(json.dumps(b,ensure_ascii=False,indent=2))
(ROOT/'data/interior_sample_v005.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
def hx(key):return '#'+''.join(f'{v:02x}' for v in b['colors'][key])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297"><rect width="210" height="297" fill="white"/>']
for a in items:
 x,y,w,h=[a[k] for k in ('x','y','w','h')]
 if a['kind']=='text':
  pt,weight,leading=b['styles'][a['style']];sz=pt*25.4/72
  tx=x if a['align']=='left' else x+w/2 if a['align']=='center' else x+w
  anchor={'left':'start','center':'middle','right':'end'}[a['align']]
  for i,value in enumerate(a['text'].split('\n')):
   svg.append(f'<text x="{tx}" y="{y+sz*.95+i*sz*leading}" font-family="Pretendard" font-weight="{700 if weight=="Bold" else 400}" font-size="{sz}" fill="{hx(a["color"])}" text-anchor="{anchor}">{html.escape(value)}</text>')
 elif a['kind']=='frame':
  svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hx("soft")}" stroke="{hx("line")}" stroke-width="0.12"/>')
 else:
  fill=hx(a['fill']) if a.get('fill') else 'none';stroke=hx(a['stroke']) if a.get('stroke') else 'none'
  sw=a.get('stroke_weight',0)*25.4/72
  svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
base=''.join(svg)
(OUT/'인생사진첩_내지1p_15mm_사진빈프레임_v005.svg').write_text(base+'</svg>')
guide='<rect x="15" y="15" width="180" height="267" fill="none" stroke="#d2519a" stroke-width="0.2" stroke-dasharray="2 1"/>'
(OUT/'인생사진첩_내지1p_15mm_가이드확인_v005.svg').write_text(base+guide+'</svg>')
assert len(b['pages'])==1 and len([a for a in items if a['kind']=='frame'])==1
assert not any(a['kind']=='ellipse' or a['name'].startswith('circle_letter_') for a in items)
for a in items:
 stroke=a.get('stroke_weight',0)*25.4/72/2
 assert a['x']-stroke>=15 and a['y']-stroke>=15,(a['name'],'top/left')
 assert a['x']+a['w']+stroke<=195 and a['y']+a['h']+stroke<=282,(a['name'],'right/bottom')
print('1쪽·빈 사진프레임·원형/사진 위 글자 없음·사방 15mm 안전영역 확인')
