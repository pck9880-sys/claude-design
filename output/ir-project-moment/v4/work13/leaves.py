import sys
sys.stdout.reconfigure(encoding="utf-8")
from pptx import Presentation
def leaves(shape, tf=(0,0,1,1)):
    ox,oy,sx,sy=tf
    if shape.shape_type==6:
        x=shape._element.grpSpPr.xfrm
        nsx = sx*(x.ext.cx/x.chExt.cx if x.chExt.cx else 1); nsy = sy*(x.ext.cy/x.chExt.cy if x.chExt.cy else 1)
        nox = ox + sx*x.off.x - nsx*x.chOff.x; noy = oy + sy*x.off.y - nsy*x.chOff.y
        for ch in shape.shapes: yield from leaves(ch,(nox,noy,nsx,nsy))
    else:
        yield shape,(ox+sx*shape.left, oy+sy*shape.top, sx*shape.width, sy*shape.height)
if __name__=="__main__":
    p=Presentation(sys.argv[1]); s=p.slides[int(sys.argv[2])-1]
    g=[x for x in s.shapes if x.name==sys.argv[3]][0]
    for sh,(x,y,w,h) in leaves(g):
        fill=""
        try: fill=sh.fill.fore_color.rgb if sh.fill.type==1 else ""
        except: pass
        print(sh.shape_id,sh.name,round(x/360000,3),round(y/360000,3),round(w/360000,3),round(h/360000,3),sh.text_frame.text[:16].replace("\n","/") if sh.has_text_frame else "",fill)
