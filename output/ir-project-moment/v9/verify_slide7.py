"""원본 대비 내용 보존과 새 경고 유무를 검사한다."""
from pathlib import Path
from zipfile import ZipFile
import subprocess,sys,json
from pptx import Presentation
from lxml import etree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
SRC=ROOT/'output/ir-project-moment/v4/deck_v8.pptx';DST=OUT/'deck_v9.pptx'
results={}
with ZipFile(SRC) as a,ZipFile(DST) as b:
 changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
 assert set(changed)=={'[Content_Types].xml','ppt/slides/slide7.xml','ppt/slides/_rels/slide7.xml.rels'}
 results['unchanged_other_slides']=True
 ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
 ch=etree.fromstring(b.read('ppt/charts/chart3.xml'))
 vals=ch.xpath('//c:ser/c:val/c:numRef/c:numCache/c:pt/c:v/text()',namespaces=ns)
 assert [float(x) for x in vals]==[70,30],vals
 results['native_pie_values']=vals
for script,args in [('check_margins.py',['--tokens','output/ir-project-moment/tokens.json']),('check_style.py',['--style','output/ir-project-moment/style.json'])]:
 logs=[]
 for label,file in [('baseline',SRC),('candidate',DST)]:
  p=subprocess.run([sys.executable,str(ROOT/'ir/scripts'/script),str(file),*args],cwd=ROOT,capture_output=True,text=True)
  (OUT/f'{script[:-3]}-{label}.txt').write_text(p.stdout+p.stderr)
  logs.append(set(x for x in p.stdout.splitlines() if x.startswith('FAIL')))
 new=sorted(logs[1]-logs[0]);results[script]={'baseline':len(logs[0]),'candidate':len(logs[1]),'new':new}
 assert not new,new
# 7p에서 이동/생성한 본문 도형은 모두 1.5cm 여백 안에 있는지 확인한다.
a=Presentation(SRC);b=Presentation(DST)
old={x.shape_id:x for x in a.slides[6].shapes}
for x in b.slides[6].shapes:
 if x.shape_id in old and etree.tostring(x._element)==etree.tostring(old[x.shape_id]._element):continue
 assert x.left>=540000 and x.top>=540000 and x.left+x.width<=b.slide_width-540000 and x.top+x.height<=b.slide_height-540000,x.name
results['edited_shapes_in_safe_area']=True
(OUT/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
