from pathlib import Path
import json,collections
root=Path(__file__).resolve().parents[1]
b=json.loads((root/'data/book-data.json').read_text());l=json.loads((root/'data/layout_v002.json').read_text());p=l['pages']
assert [x['page'] for x in p]==list(range(1,25))
assert [x['role'] for x in p[:3]]==['cover','greeting','program'] and p[-1]['role']=='closing'
assert len([x for x in p if x['role']=='artist'])==20
asset_ids={a['id'] for a in b['assets']};body=[];frames=[]
for page in p:
 for x in page['items']:
  assert x['x']>=0 and x['y']>=0 and x['w']>0 and x['h']>0
  assert x['x']+x['w']<=210.01 and x['y']+x['h']<=297.01,(page['page'],x['name'])
  if x['kind']=='frame':
   assert x['asset_id'] in asset_ids;frames.append(x['asset_id'])
   if page['role']=='artist':body.append(x['asset_id'])
assert len(body)==20 and len(set(body))==20
assert len([x for x in p[0]['items'] if x['kind']=='frame' and x['asset_id'].startswith('W')])==10
assert len([x for x in p[2]['items'] if x['kind']=='frame'])==3
assert 4<=len([x for x in p[-1]['items'] if x['kind']=='frame'])<=6
pairs=collections.defaultdict(list)
for page in p:
 if page['role']=='artist':pairs[page['artist_id']].append(page['page'])
for nums in pairs.values():assert len(nums)==2 and nums[0]%2==0 and nums[1]==nums[0]+1
for n in range(1,25):assert (root/f'output/v002/page-{n:02d}.svg').is_file()
report={'pages':24,'artist_spreads':10,'body_artwork_slots':20,'cover_artwork_slots':10,'frames_including_reused_cover_and_logos':len(frames),'within_page_bounds':True,'in_design_native_visual_verified':False,'photo_archives_received':False,'preview_type':'own_SVG_layout_preview_not_Adobe_output'}
(root/'output/v002/layout-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
