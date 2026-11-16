"""자체 제작한 배치 SVG의 검토 PNG만 렌더한다. 고객 사진/PDF를 편집하지 않는다."""
from pathlib import Path
import xml.etree.ElementTree as E
import cairosvg
root=Path(__file__).resolve().parents[1];out=root/'output/v002'
for name in ['spread-02-03','spread-04-05','spread-06-07','page-24']:
 cairosvg.svg2png(url=str(out/(name+'.svg')),write_to=str(out/(name+'.png')),output_width=1500)
ns='http://www.w3.org/2000/svg'
E.register_namespace('',ns)
sheet=E.Element('{'+ns+'}svg',viewBox='0 0 1422 1350')
E.SubElement(sheet,'rect',width='1422',height='1350',fill='#e8ebef')
for n in range(1,25):
 x=18+((n-1)%6)*235;y=18+((n-1)//6)*333
 group=E.SubElement(sheet,'g',transform=f'translate({x},{y})')
 source=E.parse(out/f'page-{n:02d}.svg').getroot()
 for child in source:group.append(child)
 label=E.SubElement(group,'text',x='105',y='313',style='font-family:Pretendard;font-size:10px;text-anchor:middle;fill:#454c56');label.text=f'{n:02d}'
source=E.tostring(sheet,encoding='unicode')
(out/'전체24p_내지배치_검토도.svg').write_text(source)
cairosvg.svg2png(bytestring=source.encode(),write_to=str(out/'전체24p_내지배치_검토도.png'),output_width=1800)
print('24쪽 전체 배치 검토도와 내지 4개 PNG 렌더 완료. InDesign 출력물이 아닌 자체 SVG 검토도.')
