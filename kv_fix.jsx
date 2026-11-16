#target illustrator
(function(){
var doc=null;
for(var i=0;i<app.documents.length;i++){ if(app.documents[i].name.indexOf(".pdf")>=0){doc=app.documents[i];} }
app.activeDocument=doc;
var DIR="C:/Users/admin/\uD074\uB85C\uB4DC/";
var log=[]; var L=doc.layers[0];
function B(it){return it.geometricBounds;}
function measure(tf,str){var d=tf.duplicate();d.contents=str;var w=d.width,h=d.height;d.remove();return [w,h];}
var EN="\uFF62Startup Prep ACADEMY VOL.02\uFF63 Pre-Startup Package Key Visual";
for(var i=0;i<doc.textFrames.length;i++){var tf=doc.textFrames[i];var c=tf.contents;
  if(c.indexOf("Donghaeng")>=0&&c.indexOf("Event")<0){tf.contents=EN;log.push("EN");}
  if(c.indexOf("Key Visual Proposal")>=0){
    var plus=null;
    for(var k=0;k<L.pathItems.length;k++){var p=L.pathItems[k];var b=B(p);if(p.width<40&&b[0]>1300&&b[0]<1700&&b[1]<-400&&b[1]>-600){plus=p;}}
    if(plus){var m=measure(tf,"Key Visual Proposal"); var lastTop=tf.top-(tf.height-m[1]);
      plus.left=tf.left+m[0]+4; plus.top=lastTop-(m[1]-plus.height)/2; log.push("plus");}
  }
}
function coverInto(p,b){var w=b[2]-b[0],h=b[1]-b[3];var s=Math.max(w/p.width,h/p.height);
  p.width=p.width*s;p.height=p.height*s;p.left=b[0]+(w-p.width)/2;p.top=b[1]-(h-p.height)/2;}
function processSection(x0,x1,file){
  var gs=[]; for(var i=0;i<L.groupItems.length;i++){var g=L.groupItems[i]; if(g.parent.typename!="Layer")continue; var gb=B(g);
    if(gb[0]<x0||gb[2]>x1||gb[1]>-100||gb[3]>-500)continue; gs.push(g);}
  for(var i=0;i<gs.length;i++){var g=gs[i];
    if(g.clipped){var r=g.rasterItems[0];var clipP=null;for(var k=0;k<g.pathItems.length;k++){if(g.pathItems[k].clipping)clipP=g.pathItems[k];}
      var p=g.placedItems.add();p.file=file;p.move(r,ElementPlacement.PLACEAFTER);coverInto(p,B(clipP));r.remove();p.embed();log.push("poster "+x0);
    }else{var r=null;for(var k=0;k<g.pageItems.length;k++){if(g.pageItems[k].typename=="RasterItem"){r=g.pageItems[k];break;}}
      if(!r)continue;var rb=B(r);var ng=g.groupItems.add();ng.move(r,ElementPlacement.PLACEBEFORE);
      var p=ng.placedItems.add();p.file=file;coverInto(p,rb);
      var rect=ng.pathItems.rectangle(rb[1],rb[0],rb[2]-rb[0],rb[1]-rb[3]);rect.filled=false;rect.stroked=false;
      ng.clipped=true;r.remove();p.embed();log.push("mockup "+x0);}
  }
  log.push("groups "+x0+": "+gs.length);
}
try{processSection(1800,2650,new File(DIR+"poster_A.png"));
processSection(2675,3525,new File(DIR+"poster_B.png"));}catch(e){log.push("ERR "+e+" line "+e.line);}
var lf=new File(DIR+"kv_log.txt");lf.encoding="UTF-8";lf.open("w");lf.write(log.join("\n"));lf.close();
})();
