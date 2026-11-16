"""v8의 7p만 수정. 나머지 슬라이드와 자산은 원본 ZIP 항목을 보존한다."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
import csv, json
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_DATA_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'output/ir-project-moment/v4/deck_v8.pptx'
OUT=Path(__file__).parent
TOK=json.loads((ROOT/'output/ir-project-moment/tokens.json').read_text())
C=TOK['color']; RED=C['brand']['primary'].lstrip('#'); GRAY=C['neutral']['500'].lstrip('#'); INK=C['text']['primary'].lstrip('#'); WHITE=C['neutral']['0'].lstrip('#')
rows=list(csv.DictReader((ROOT/'ir/data-project-moment/kpi.csv').open(encoding='utf-8-sig')))
# CSV의 첫 열은 식별자이다. 값 필드 이름은 원본 헤더를 따른다.

bykey={list(r.values())[0]:r for r in rows}
def value(key): return float(bykey[key]['value'])
assert value('other_share')==70 and value('share_target')==30
assert value('other_rev')==420 and value('share_target_rev')==180
r=Presentation(SRC); s=r.slides[6]; shapes={x.shape_id:x for x in s.shapes}
def pos(i,x,y,w=None,h=None):
 sh=shapes[i]; sh.left=Cm(x);sh.top=Cm(y)
 if w is not None:sh.width=Cm(w)
 if h is not None:sh.height=Cm(h)
 return sh
def delete(i):
 el=shapes[i]._element;el.getparent().remove(el)
def font(sh,size,color=None):
 for p in sh.text_frame.paragraphs:
  for run in p.runs:
   run.font.size=Pt(size)
   if color:run.font.color.rgb=RGBColor.from_string(color)
def textbox(x,y,w,h,t,size=12,color=INK,bold=False,align=PP_ALIGN.LEFT,name='설명'):
 sh=s.shapes.add_textbox(Cm(x),Cm(y),Cm(w),Cm(h));sh.name=name
 tf=sh.text_frame;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.word_wrap=True
 p=tf.paragraphs[0];p.alignment=align;p.line_spacing=1.2
 rr=p.add_run();rr.text=t;rr.font.name='Pretendard SemiBold' if bold else 'Pretendard Medium';rr.font.size=Pt(size);rr.font.color.rgb=RGBColor.from_string(color)
 for tag in ('a:ea','a:cs'):
  rr._r.get_or_add_rPr().append(parse_xml(f'<{tag} xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{rr.font.name}"/>'))
 return sh
# 기존 상단 메뉴·제목은 보존. 기존 가로 비중 막대와 큰 비율 텍스트만 교체.
for i in (33,34,38,42):delete(i)
pos(35,1.55,5.35,10.0,11.9);pos(36,21.35,5.35,10.97,11.9)
for sid in (35,36): shapes[sid].line.width=Pt(1.6)
# 두 이미지 파트의 숫자·태그·구분선을 같은 기준선에 정렬.
pos(37,2.15,5.95);pos(41,21.95,5.95)
font(pos(39,2.15,6.95,8.8,1.3),32,GRAY)
font(pos(43,21.95,6.95,9.77,1.3),32,RED)
# 숫자와 단위를 분리해 읽기 위계를 만든다.
for sid,number,col in ((39,'420',GRAY),(43,'180',RED)):
 tf=shapes[sid].text_frame;tf.clear();p=tf.paragraphs[0]
 for t,sz in ((number,32),('억',18)):
  run=p.add_run();run.text=t;run.font.name='Pretendard ExtraBold';run.font.size=Pt(sz);run.font.color.rgb=RGBColor.from_string(col)
textbox(2.15,8.35,8.8,.5,'시장 비중 70%',12,GRAY,name='카피캣 비중 설명')
# 목표라는 의미를 유지. 원문 문구와 숫자 그대로.
msg=pos(44,21.95,8.15,9.77,1.15)
for p in msg.text_frame.paragraphs:p.alignment=PP_ALIGN.LEFT
font(msg,12)
pos(40,2.15,9.65,8.8,0);pos(45,21.95,9.65,9.77,0)
# 원본 이미지 재사용: 카피캣 7개, owooii 메인 화보 + 작은 제품 이미지 3개.
for i,sid in enumerate((17,18,19,20)):pos(sid,2.15+i*2.25,10.1,2.05,2.67)
for i,sid in enumerate((21,22,23)):pos(sid,2.15+i*3.0,13.37,2.8,2.82)
pos(24,21.95,10.1,9.77,5.45)
for i,sid in enumerate((25,26,27)):
 sh=shapes[sid]; ar=sh.width/sh.height;h=1.1;w=h*ar
 pos(sid,21.95+i*3.39+(2.99-w)/2,15.95,w,h)
# 수정 가능한 PowerPoint 원형 차트와 포함된 Excel 데이터.
data=CategoryChartData();data.categories=['저가형 카피캣','owooii 확보 목표'];data.add_series('시장 비중',[value('other_share'),value('share_target')])
ch=s.shapes.add_chart(XL_CHART_TYPE.PIE,Cm(12.15),Cm(8.05),Cm(8.6),Cm(8.6),data).chart
ch.has_legend=False;ch.has_title=False
ch.chart_style=10
ch.font.name='Pretendard';ch.font.size=Pt(12)
plot=ch.plots[0];plot.has_data_labels=True
pie=ch._chartSpace.xpath('.//c:pieChart')[0]
pie.append(parse_xml('<c:firstSliceAng xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" val="144"/>'))
labels=plot.data_labels;labels.show_percentage=True;labels.show_value=False;labels.show_category_name=False;labels.position=XL_DATA_LABEL_POSITION.CENTER;labels.number_format='0%';labels.font.name='Pretendard ExtraBold';labels.font.size=Pt(24);labels.font.color.rgb=RGBColor.from_string(WHITE)
for point,col in zip(ch.series[0].points,(GRAY,RED)):
 point.format.fill.solid();point.format.fill.fore_color.rgb=RGBColor.from_string(col)
 point.format.line.color.rgb=RGBColor.from_string(WHITE);point.format.line.width=Pt(1.6)
# 원형 외부에도 색상과 의미를 연결하여 목표 수치를 명확히 한다.
textbox(12.15,6.15,8.6,.7,'카테고리 내 시장 비중',16,INK,True,PP_ALIGN.CENTER,'원형 그래프 제목')
textbox(12.15,7.05,8.6,.55,'70% 카피캣 / 30% owooii 목표',12,GRAY,False,PP_ALIGN.CENTER,'원형 그래프 범례')
textbox(12.15,16.25,8.6,.55,'owooii 30% 확보 목표',14,RED,True,PP_ALIGN.CENTER,'목표 비중')
# 삭제한 도형에 대한 애니메이션 참조 제거(있을 경우).
for timing in s._element.findall(qn('p:timing')):s._element.remove(timing)
b=BytesIO();r.save(b);b.seek(0)
with ZipFile(SRC) as src,ZipFile(b) as changed,ZipFile(OUT/'deck_v9.pptx','w',ZIP_DEFLATED) as dst:
 names=set(src.namelist());added=set(changed.namelist())-names
 replace={'ppt/slides/slide7.xml','ppt/slides/_rels/slide7.xml.rels','[Content_Types].xml'}
 for item in src.infolist():dst.writestr(item,changed.read(item.filename) if item.filename in replace else src.read(item.filename))
 for name in sorted(added):dst.writestr(name,changed.read(name))
with ZipFile(SRC) as a,ZipFile(OUT/'deck_v9.pptx') as b:
 changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
 assert set(changed)==replace,changed
 print('원본 대비 변경 ZIP 항목:',changed,'추가:',sorted(added))
print('저장:',OUT/'deck_v9.pptx')
