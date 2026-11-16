#target illustrator
(function(){
var doc=null;
for(var i=0;i<app.documents.length;i++){ if(app.documents[i].name.indexOf(".pdf")>=0){doc=app.documents[i];} }
if(!doc){alert("pdf doc not found");return;}
app.activeDocument=doc;
var DIR="C:/Users/admin/\uD074\uB85C\uB4DC/";
var log=[];
var L=doc.layers[0]; L.locked=false;
function B(it){return it.geometricBounds;}
function inRange(it,x0,x1,y0,y1){var b=B(it);return b[0]>=x0-1&&b[2]<=x1+1&&b[1]<=y0+1&&b[3]>=y1-1;}
function measure(tf,str){var d=tf.duplicate();d.contents=str;var w=d.width;d.remove();return w;}

// ---------- 1. delete TYPE C ----------
var abC=doc.artboards[4].artboardRect;
var del=[];
for(var i=0;i<L.pageItems.length;i++){var it=L.pageItems[i]; if(inRange(it,abC[0],abC[2],abC[1],abC[3])) del.push(it);}
for(var i=0;i<del.length;i++){del[i].locked=false;del[i].remove();}
doc.artboards.remove(4);
log.push("TYPE C removed items: "+del.length);

// ---------- 2. text ----------
var EN="\uFF62Startup Prep ACADEMY VOL.02\uFF63 Pre-Startup Package Key Visual";
var KR="\uFF62\uC608\uBE44\uCC3D\uC5C5\uD328\uD0A4\uC9C0\uFF63 \uCC3D\uC5C5\uC900\uBE44 \uC544\uCE74\uB370\uBBF8 VOL.02 \uD0A4\uBE44\uC8FC\uC5BC \uC81C\uC548";
var MAP={};
MAP["\uD604\uC7A5\uAC10"]="\uC870\uD615\uBBF8"; // 현장감->조형미
MAP["\uC5ED\uB3D9\uC801"]="\uB9AC\uB4EC\uAC10"; // 역동적->리듬감
MAP["\uBAB0\uC785\uAC10"]="\uAC00\uB3C5\uC131"; // 몰입감->가독성
MAP["\uC785\uCCB4\uAC10"]="\uCE5C\uADFC\uD568"; // 입체감->친근함
MAP["\uCE5C\uADFC\uD568"]="\uB530\uB73B\uD568"; // 친근함->따뜻함
MAP["\uB3C5\uCC3D\uC131"]="\uC0DD\uB3D9\uAC10"; // 독창성->생동감
var HEAD_A="\uCEEC\uB7EC \uB3C4\uD615\uACFC \uD0C0\uC774\uD3EC\uADF8\uB798\uD53C\uB85C\r\uB9AC\uB4EC\uAC10\uC744 \uD45C\uD604\uD55C \uB514\uC790\uC778";
var HEAD_B="\uCC3D\uC5C5 \uC900\uBE44 \uACFC\uC815\uC744 \uC624\uBE0C\uC81C\r\uC77C\uB7EC\uC2A4\uD2B8\uB85C \uD480\uC5B4\uB0B8 \uB514\uC790\uC778";
var BODY_A="\uC608\uBE44\uCC3D\uC5C5 PACKAGE \uCC3D\uC5C5\uC900\uBE44 ACADEMY \uD0C0\uC774\uD2C0\uC744 \uB300\uD615 \uD0C0\uC774\uD3EC\uADF8\uB798\uD53C\uB85C \uAD6C\uC131\uD558\uACE0, \uAE00\uC790 \uC77C\uBD80\uC5D0 \uD3EC\uC778\uD2B8 \uCEEC\uB7EC\uB97C \uB354\uD574 \uC2DC\uAC01\uC801 \uC8FC\uBAA9\uB3C4\uB97C \uB192\uC600\uC2B5\uB2C8\uB2E4.\r\r\uC6D0\uD615\u00B7\uC0BC\uAC01\uD615 \uB4F1 \uAE30\uD558\uD559 \uB3C4\uD615\uC744 \uB9AC\uB4EC\uAC10 \uC788\uAC8C \uBC30\uCE58\uD574 \uCC3D\uC5C5\uC758 \uC2DC\uC791\uACFC \uC131\uC7A5\uC744 \uACBD\uCF8C\uD558\uAC8C \uD45C\uD604\uD558\uACE0, \uAD50\uC2DC\uBCC4 \uC815\uBCF4\uB97C \uD55C\uB208\uC5D0 \uC77D\uD788\uB3C4\uB85D \uC815\uB9AC\uD588\uC2B5\uB2C8\uB2E4.";
var BODY_B="\uC758\uC790, \uCC45, \uC2A4\uD0E0\uB4DC, \uB3CB\uBCF4\uAE30 \uB4F1 \uCC3D\uC5C5 \uC900\uBE44 \uACFC\uC815\uC744 \uC0C1\uC9D5\uD558\uB294 \uC624\uBE0C\uC81C\uB97C \uCEF7\uC544\uC6C3 \uC77C\uB7EC\uC2A4\uD2B8\uB85C \uAD6C\uC131\uD574 \uCE5C\uADFC\uD558\uACE0 \uB530\uB73B\uD55C \uC778\uC0C1\uC744 \uC804\uB2EC\uD569\uB2C8\uB2E4.\r\r\uD074\uB798\uC2DD\uD55C \uC138\uB9AC\uD504 \uD0C0\uC774\uD2C0\uACFC \uB2E4\uCC44\uB85C\uC6B4 \uCEEC\uB7EC\uB97C \uC870\uD569\uD574 \uAD50\uC721 \uD504\uB85C\uADF8\uB7A8\uC758 \uC2E0\uB8B0\uAC10\uACFC \uD65C\uAE30\uB97C \uD568\uAED8 \uD45C\uD604\uD588\uC2B5\uB2C8\uB2E4.";

var titles=[]; var blackTitle=null;
var tfs=[]; for(var i=0;i<doc.textFrames.length;i++) tfs.push(doc.textFrames[i]);
for(var i=0;i<tfs.length;i++){
  var tf=tfs[i]; var c=tf.contents; var x=B(tf)[0];
  var sec = (x>=1800&&x<=2650)?"A":((x>=2675&&x<=3525)?"B":"");
  if(c.indexOf("Together at Jagalchi")==0 && c.indexOf("Key Visual")>0 && c.indexOf("Event")<0){tf.contents=EN;continue;}
  if(c.indexOf("Together at Jagalchi")>=0 && c.indexOf("Event")>=0){blackTitle=tf;continue;}
  if(c.indexOf("\uB2E4\uAC19\uC774 \uC790\uAC08\uCE58\uFF63")>=0){tf.contents=KR;continue;}
  if(c.indexOf("\uB2E4\uAC19\uC774 \uC790\uAC08\uCE58  ")==0){titles.push(tf);continue;}
  if(sec=="A"||sec=="B"){
    if(MAP[c]&&tf.contents.length==3){tf.contents=MAP[c];continue;}
    if(tf.kind==TextType.AREATEXT){tf.contents=(sec=="A")?BODY_A:BODY_B;continue;}
    if(c.indexOf("\uB514\uC790\uC778")>=0){tf.contents=(sec=="A")?HEAD_A:HEAD_B;continue;}
  }
}

// title blocks (cover + closing)
function findTop(test){for(var i=0;i<L.pageItems.length;i++){if(test(L.pageItems[i]))return L.pageItems[i];}return null;}
for(var t=0;t<titles.length;t++){
  var t1=titles[t]; var grp=t1.parent; var t2=null, plus=null;
  for(var k=0;k<grp.pageItems.length;k++){var it=grp.pageItems[k]; if(it.typename=="TextFrame"&&it!=t1)t2=it; if(it.typename=="PathItem")plus=it;}
  var x1=t1.left, y1=t1.top;
  var ob=findTop(function(it){return it.typename=="GroupItem"&&Math.abs(it.top-y1+3)<6&&it.left<x1&&it.left>x1-30;});
  var cb=findTop(function(it){return it.typename=="GroupItem"&&it.width<20&&it.left>x1+100&&it.left<x1+400&&Math.abs(it.top-y1)<40;});
  var wOld=measure(t1,"\uB2E4\uAC19\uC774 \uC790\uAC08\uCE58");
  var cbGap=cb.left-(t1.left+wOld), cbDy=cb.top-y1, obDy=ob.top-y1, obDx=ob.left-x1;
  var t2Dy=t2.top-y1, plusGap=plus.left-(t2.left+t2.width), plusDy=plus.top-t2.top;
  var maxW=t1.width;
  t1.contents="\uC608\uBE44\uCC3D\uC5C5\uD328\uD0A4\uC9C0  \uCC3D\uC5C5\uC900\uBE44 ACADEMY";
  t2.contents="VOL.02 \uD0A4\uBE44\uC8FC\uC5BC \uC81C\uC548";
  var f=1;
  if(t1.width>maxW){f=maxW/t1.width;
    var s=t1.textRange.characterAttributes.size*f;
    t1.textRange.characterAttributes.size=s; t2.textRange.characterAttributes.size=s;
    ob.resize(f*100,f*100); cb.resize(f*100,f*100); plus.resize(f*100,f*100);}
  t1.left=x1; t1.top=y1; t2.left=x1; t2.top=y1+t2Dy*f;
  ob.left=x1+obDx*f; ob.top=y1+obDy*f;
  cb.left=t1.left+measure(t1,"\uC608\uBE44\uCC3D\uC5C5\uD328\uD0A4\uC9C0")+cbGap*f; cb.top=y1+cbDy*f;
  plus.left=t2.left+t2.width+plusGap*f; plus.top=t2.top+plusDy*f;
  log.push("title f="+f);
}
// black page title
if(blackTitle){
  var lines=blackTitle.contents.split("\r");
  var plusB=findTop(function(it){return it.typename=="PathItem"&&it.width<40&&it.left>1300&&it.left<1700&&it.top<-450&&it.top>-560;});
  var bx=blackTitle.left, by=blackTitle.top;
  var gap=plusB.left-(bx+measure(blackTitle,lines[lines.length-1])), pdy=plusB.top-(by-blackTitle.height);
  var L3="Key Visual Proposal";
  blackTitle.contents="\uFF62\uCC3D\uC5C5\uC900\uBE44 ACADEMY VOL.02\uFF63\rPre-Startup Package\r"+L3;
  blackTitle.left=bx; blackTitle.top=by;
  plusB.left=bx+measure(blackTitle,L3)+gap; plusB.top=(by-blackTitle.height)+pdy;
}

// ---------- 3. images ----------
function coverInto(p,b){ // b = [l,t,r,b]
  var w=b[2]-b[0], h=b[1]-b[3]; var s=Math.max(w/p.width,h/p.height);
  p.width=p.width*s; p.height=p.height*s; p.left=b[0]+(w-p.width)/2; p.top=b[1]-(h-p.height)/2;}
function processSection(x0,x1,file){
  for(var i=0;i<L.groupItems.length;i++){
    var g=L.groupItems[i]; if(g.parent!=L)continue; var gb=B(g); if(gb[0]<x0||gb[2]>x1||gb[1]<-100||gb[3]>-500)continue;
    if(g.clipped){ // flat poster
      var r=g.rasterItems[0]; var clipP=null; for(var k=0;k<g.pathItems.length;k++){if(g.pathItems[k].clipping)clipP=g.pathItems[k];}
      var p=g.placedItems.add(); p.file=file; p.move(r,ElementPlacement.PLACEAFTER);
      coverInto(p,B(clipP)); r.remove(); p.embed(); log.push("poster replaced "+x0);
    } else { // mockup
      var r=null; for(var k=0;k<g.pageItems.length;k++){if(g.pageItems[k].typename=="RasterItem"){r=g.pageItems[k];break;}}
      if(!r)continue; var rb=B(r);
      var ng=g.groupItems.add(); ng.move(r,ElementPlacement.PLACEBEFORE);
      var p=ng.placedItems.add(); p.file=file; coverInto(p,rb);
      var rect=ng.pathItems.rectangle(rb[1],rb[0],rb[2]-rb[0],rb[1]-rb[3]); rect.filled=false; rect.stroked=false;
      ng.clipped=true; r.remove(); p.embed(); log.push("mockup replaced "+x0);
    }
  }
}
processSection(1800,2650,new File(DIR+"poster_A.png"));
processSection(2675,3525,new File(DIR+"poster_B.png"));

var lf=new File(DIR+"kv_log.txt"); lf.encoding="UTF-8"; lf.open("w"); lf.write(log.join("\n")); lf.close();
})();
