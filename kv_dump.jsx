#target illustrator
(function(){
var doc=null;
for(var i=0;i<app.documents.length;i++){ if(app.documents[i].name.indexOf("pdf")>=0||app.documents[i].name.indexOf("PDF")>=0){doc=app.documents[i];} }
if(!doc){alert("pdf doc not found");return;}
var out=[];
out.push("DOC "+doc.name);
for(var a=0;a<doc.artboards.length;a++){out.push("AB "+a+" "+doc.artboards[a].name+" "+doc.artboards[a].artboardRect.join(","));}
for(var l=0;l<doc.layers.length;l++){out.push("LAYER "+doc.layers[l].name+" locked="+doc.layers[l].locked);}
function r(n){return Math.round(n);}
function walk(items,depth){
 for(var k=0;k<items.length;k++){
  var it=items[k]; var pre=new Array(depth+1).join("  ");
  var b=it.geometricBounds; var s=pre+it.typename+" ["+r(b[0])+","+r(b[1])+","+r(b[2])+","+r(b[3])+"] nm="+it.name+" lk="+it.locked+" hid="+it.hidden;
  if(it.typename=="TextFrame"){var f="";try{f=it.textRange.characterAttributes.textFont.name+" "+it.textRange.characterAttributes.size;}catch(e){}
   s+=" kind="+it.kind+" font="+f+" TXT="+it.contents.replace(/[\r\n]/g," | ");}
  if(it.typename=="PlacedItem"){try{s+=" file="+it.file.fsName;}catch(e){s+=" file=?";}}
  if(it.typename=="GroupItem"){s+=" clip="+it.clipped; out.push(s); walk(it.pageItems,depth+1); continue;}
  out.push(s);
 }
}
for(var l=0;l<doc.layers.length;l++){out.push("== LAYER "+doc.layers[l].name); walk(doc.layers[l].pageItems,1);}
var f=new File("C:/Users/admin/\uD074\uB85C\uB4DC/kv_dump.txt"); f.encoding="UTF-8"; f.open("w"); f.write(out.join("\n")); f.close();

})();
