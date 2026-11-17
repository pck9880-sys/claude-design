// 열린 Illustrator 문서의 이름/폰트/배치 이미지 정보를 JSON 문자열로 반환 (읽기 전용)
(function () {
  function q(s) { return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"'; }
  if (app.documents.length === 0) return '{"open":false}';
  var d = app.activeDocument, i, seen = {}, fonts = [], links = [];
  for (i = 0; i < d.textFrames.length && i < 300; i++) {
    try {
      var tf = d.textFrames[i].textRange.characterAttributes.textFont;
      var key = tf.family + "/" + tf.style;
      if (!seen[key]) { seen[key] = 1; fonts.push('{"family":' + q(tf.family) + ',"style":' + q(tf.style) + '}'); }
    } catch (e) {}
  }
  for (i = 0; i < d.placedItems.length && i < 80; i++) {
    try { links.push('{"name":' + q(d.placedItems[i].file.name) + '}'); }
    catch (e) { links.push('{"name":"(missing)"}'); }
  }
  var path = ""; try { path = d.fullName.fsName; } catch (e) {}
  return '{"open":true,"app":"Illustrator","name":' + q(d.name) + ',"path":' + q(path) +
         ',"artboards":' + d.artboards.length + ',"fonts":[' + fonts.join(",") + '],"links":[' + links.join(",") + ']}';
})();
