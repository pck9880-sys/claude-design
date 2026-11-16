"""검토용 SVG를 PNG와 PDF로 렌더링. 실제 InDesign 출력과 구분."""
from pathlib import Path
import io
import cairosvg
from pypdf import PdfReader,PdfWriter
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parents[1]/'output/full-v004'
w=PdfWriter()
for f in sorted(p.glob('page-*.svg')):
 cairosvg.svg2png(url=str(f),write_to=str(f.with_suffix('.png')),output_width=700)
 w.add_page(PdfReader(io.BytesIO(cairosvg.svg2pdf(url=str(f)))).pages[0])
assert len(w.pages)==24
with (p/'인생사진첩_전체24p_구성_v004_검토용.pdf').open('wb') as o:w.write(o)
for f in sorted(p.glob('spread-*.svg')):cairosvg.svg2png(url=str(f),write_to=str(f.with_suffix('.png')),output_width=1500)
thumbw,thumbh,gap=260,368,20
sheet=Image.new('RGB',(6*(thumbw+gap)+gap,4*(thumbh+38)+gap),'#e7e5e1');d=ImageDraw.Draw(sheet)
for i in range(24):
 im=Image.open(p/f'page-{i+1:02d}.png').convert('RGB');im.thumbnail((thumbw,thumbh))
 x=gap+(i%6)*(thumbw+gap);y=gap+(i//6)*(thumbh+38)
 sheet.paste(im,(x,y));d.text((x,y+thumbh+6),f'{i+1:02d}',fill='#3a3a3a')
sheet.save(p/'전체24p_한눈에보기.png')
print('24쪽 검토 PDF, 페이지24장, 펼침면11개, 전체 보기 생성')
