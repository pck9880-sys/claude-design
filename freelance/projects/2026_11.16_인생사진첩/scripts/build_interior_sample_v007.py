"""1쪽 템플릿: 사진 높이8mm 축소, 하단 편집 묶음8mm 위로 이동."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/interior-sample-v007';OUT.mkdir(exist_ok=True)
b=json.loads((ROOT/'data/interior_sample_v006.json').read_text())
page=b['pages'][0];items=page['items']
for a in items:
 if a['kind']=='frame':a['h']-=8
 elif a['name']=='Caption':a['y']-=8
 elif a['name']=='line' and a['x']==194 and a['y']==164:a['y']-=8
 elif a['name']=='line' and a['y']==186:a['y']-=8
 elif 198<=a['y']<=248:a['y']-=8
frame=next(a for a in items if a['kind']=='frame')
rail=next(a for a in items if a['name']=='framed_side_title')
author=next(a for a in items if a['name']=='Author')
assert frame['h']==145
assert author['y']==rail['y']==190
assert author['x']-rail['x']-rail['w']==8
assert max(a['y']+a['h'] for a in items if a.get('style') in ('Body','Quote'))==264
assert next(a['y'] for a in items if a['name']=='line' and a['y']==275)-264==11
assert 194-frame['x']-frame['w']==178-frame['y']-frame['h']==8
b['state']='single_page_15mm_template_photo_pending'
b['spec']['margin_mm']={'top':15,'bottom':15,'left':15,'right':15}
b['demo_assets']=[]
b['demo_note']='사진은 나중에 삽입할 빈 프레임. 작가명·소개·작품 문구는 기존 사용자 허용 예시를 유지.'
b['styles'].pop('CircleText',None);b['styles'].pop('PhotoTitle',None)
(ROOT/'data/interior_sample_v007.json').write_text(json.dumps(b,ensure_ascii=False,indent=2))
(ROOT/'data/interior_sample_v007.jsxinc').write_text('var ALBUM_LAYOUT = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
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
(OUT/'인생사진첩_내지1p_15mm_사진빈프레임_v007.svg').write_text(base+'</svg>')
guide='<rect x="15" y="15" width="180" height="267" fill="none" stroke="#d2519a" stroke-width="0.2" stroke-dasharray="2 1"/>'
(OUT/'인생사진첩_내지1p_15mm_가이드확인_v007.svg').write_text(base+guide+'</svg>')
assert len(b['pages'])==1 and len([a for a in items if a['kind']=='frame'])==1
assert not any(a['kind']=='ellipse' or a['name'].startswith('circle_letter_') for a in items)
for a in items:
 stroke=a.get('stroke_weight',0)*25.4/72/2
 assert a['x']-stroke>=15 and a['y']-stroke>=15,(a['name'],'top/left')
 assert a['x']+a['w']+stroke<=195 and a['y']+a['h']+stroke<=282,(a['name'],'right/bottom')
print('1쪽·빈 사진프레임·원형/사진 위 글자 없음·사방 15mm 안전영역 확인')
