from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
b=json.loads((root/'data/book-data.json').read_text(encoding='utf-8-sig'))
assert len(b['pages'])==24 and [p['page'] for p in b['pages']]==list(range(1,25))
assert len(b['artists'])==10
assert len([a for a in b['assets'] if a['kind']=='artwork'])==20
assert len({a['id'] for a in b['assets']})==len(b['assets'])
for a in b['assets']:
 if a['path']:
  p=(root/a['path']).resolve()
  assert p.is_relative_to(root.resolve()),'프로젝트 밖 자산 경로 금지'
  assert p.is_file(),a['path']
(root/'data/book-data.jsxinc').write_text('var BOOK_DATA = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',encoding='utf-8-sig')
print('JSON 검사와 JSX 데이터 갱신 완료')
