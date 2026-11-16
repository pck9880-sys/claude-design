"""HWP 5 문단 텍스트를 읽기만 한다. 문서 안 Scripts 스트림은 실행하지 않는다."""
from pathlib import Path
import struct,zlib,sys
import olefile
root=Path(__file__).resolve().parents[1]
p=next((root/'inputs/manuscript').glob('*.hwp'))
with olefile.OleFileIO(p) as o:
 flags=struct.unpack_from('<I',o.openstream('FileHeader').read(),36)[0]
 if flags&2:raise RuntimeError('암호화 HWP는 처리하지 않습니다.')
 result=[]
 for path in o.listdir():
  if path[0]!='BodyText':continue
  data=o.openstream(path).read()
  if flags&1:data=zlib.decompress(data,-15)
  pos=0
  while pos+4<=len(data):
   h=struct.unpack_from('<I',data,pos)[0];pos+=4;tag=h&0x3ff;size=h>>20
   if size==0xfff:size=struct.unpack_from('<I',data,pos)[0];pos+=4
   block=data[pos:pos+size];pos+=size
   if tag!=67:continue
   units=struct.unpack('<'+'H'*(len(block)//2),block);out=[];i=0
   while i<len(units):
    c=units[i]
    if c in (1,2,3,4,5,6,7,8,9,11,12,14,15,16,17,18,19,20,21,22,23):i+=8;continue
    if c in (10,13):out.append('\n')
    elif c>=32:out.append(chr(c))
    i+=1
   result.append(''.join(out))
 target=root/'data/manuscript-extracted.md'
 target.write_text('# HWP 원고 추출\n\n출처: '+p.name+'\n\n'+'\n\n'.join(x for x in result if x.strip()),encoding='utf-8')
 print(target)
