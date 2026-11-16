"""고객 원고 기준의 24쪽 구성과 자료 매핑을 준비한다. 사진·이름·작품 문구를 만들지 않는다."""
from pathlib import Path
import csv,json,hashlib
root=Path(__file__).resolve().parents[1];data=root/'data';data.mkdir(exist_ok=True)
assets=[]
for i in range(1,21):
 assets.append({'id':f'W{i:02d}','kind':'artwork','artist_id':f'A{(i+1)//2:02d}','path':'','title':'','description':'','status':'awaiting_zip_and_mapping'})
for i in range(1,10):assets.append({'id':f'ACT{i:02d}','kind':'activity','artist_id':'','path':'','title':'','description':'','status':'awaiting_zip'})
assets.extend([{'id':k,'kind':'logo','artist_id':'','path':'','title':'','description':'','status':'not_received'} for k in ('ORG_LOGO','SUPPORT_LOGO')])
artists=[{'id':f'A{i:02d}','name':'','bio':'','left_asset':f'W{i*2-1:02d}','right_asset':f'W{i*2:02d}','cover_asset':f'W{i*2-1:02d}','mapping_confirmed':False} for i in range(1,11)]
pages=[{'page':1,'role':'cover','content':'인생사진첩 / 프레임에 담긴 나의 세상','asset_ids':[a['cover_asset'] for a in artists]}, {'page':2,'role':'greeting','content':'센터장 인사말 (원고 대기)','asset_ids':[]}, {'page':3,'role':'program','content':'프로그램 소개·출사 및 스토리텔링 8회기 주제','asset_ids':['ACT01','ACT02','ACT03']}]
for i,a in enumerate(artists):
 for side,key in [('left','left_asset'),('right','right_asset')]:
  pages.append({'page':4+i*2+(side=='right'),'role':'artist','artist_id':a['id'],'side':side,'asset_ids':[a[key]]})
pages.append({'page':24,'role':'closing','content':'함께한 순간들 / 참여 어르신·강사·봉사자·기관 정보','asset_ids':[f'ACT{i:02d}' for i in range(4,10)]})
book={'project':'2026_11.16_인생사진첩','title':'인생사진첩','subtitle':'프레임에 담긴 나의 세상','organization':'동래구노인복지관 재가노인지원서비스센터','support_note':'본 제작물은 부산사회복지공동모금회의 지원으로 제작되었습니다.','greeting':'','program_intro':'','sessions':['']*8,'contributors':'','organization_info':'','pages':pages,'artists':artists,'assets':assets,'spec':{'page_count':24,'width_mm':210,'height_mm':297,'bleed_mm':3,'size_confirmed':False,'bleed_confirmed':False,'facing_pages':True,'font':'Pretendard','font_style':'Regular','heading_style':'Bold','body_pt':14,'caption_pt':12,'font_note':'판형 A4·도련 3mm는 검토용 임시값. 인쇄 사양 확인 전 확정 금지.'},'colors':{'ink':[23,26,31],'muted':[89,96,102],'line':[215,219,220],'soft':[245,246,245]},'production_state':'layout_preparation_missing_photos_and_copy'}
target=data/'book-data.json'
# 재실행 시 기존 입력 데이터를 지우지 않는다.
if target.exists():raise SystemExit('book-data.json이 이미 있어 덮어쓰지 않았습니다. 변경은 해당 파일에 반영하세요.')
target.write_text(json.dumps(book,ensure_ascii=False,indent=2),encoding='utf-8')
(data/'book-data.jsxinc').write_text('var BOOK_DATA = '+json.dumps(book,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
with (data/'asset-mapping.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(assets[0]));w.writeheader();w.writerows(assets)
rows=[]
for p in sorted((root/'inputs').rglob('*')):
 if p.is_file():rows.append({'name':p.name,'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'manuscript' if p.suffix=='.hwp' else 'cover_reference_only','status':'received'})
for n in ['활동사진 (2).Zip','작품사진 20장 (1).Zip']:
 rows.append({'name':n,'path':None,'bytes':None,'sha256':None,'role':'activity_photos' if n.startswith('활동') else 'artwork_photos','status':'blocked_transfer_limit_over_32MiB'})
(data/'input-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with (data/'page-plan.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['page','role','artist_id','side','assets','content'])
 for p in pages:w.writerow([p['page'],p['role'],p.get('artist_id',''),p.get('side',''),';'.join(p['asset_ids']),p.get('content','')])
print('24쪽 구성·10명·20작품 자리·9활동사진 자리 준비. 매핑은 미확정.')
