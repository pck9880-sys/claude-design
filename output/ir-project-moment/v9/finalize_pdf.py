"""렌더한 7p를 원본 PDF에 삽입해 나머지 페이지의 화면을 보존한다."""
from pathlib import Path
import pymupdf
out=Path(__file__).parent
root=out.parents[2]
render=pymupdf.open(out/'deck_v9.pdf')
base=pymupdf.open(root/'output/ir-project-moment/v4/프로젝트모먼트_IR_v8.pdf')
base.delete_page(6);base.insert_pdf(render,from_page=6,to_page=6,start_at=6)
base.save(out/'deck_v9-final.pdf',garbage=3,deflate=True)
base.close();render.close();(out/'deck_v9-final.pdf').replace(out/'deck_v9.pdf')
d=pymupdf.open(out/'deck_v9.pdf');(out/'preview').mkdir(exist_ok=True)
for i,page in enumerate(d,1):page.get_pixmap(dpi=110).save(str(out/'preview'/f'slide-{i:02d}.png'))
one=pymupdf.open();one.insert_pdf(d,from_page=6,to_page=6);one.save(out/'7p-preview.pdf')
one.close(); d.close(); orig=pymupdf.open(root/'output/ir-project-moment/v4/프로젝트모먼트_IR_v8.pdf'); d=pymupdf.open(out/'deck_v9.pdf')
assert len(d)==len(orig)==15
for i in range(15):
 if i!=6:assert d[i].get_pixmap(matrix=pymupdf.Matrix(.25,.25)).digest==orig[i].get_pixmap(matrix=pymupdf.Matrix(.25,.25)).digest,i
print('PDF: 7p 외 14페이지 렌더 일치 확인')
