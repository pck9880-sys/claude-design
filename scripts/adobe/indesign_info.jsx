// 열린 InDesign 문서의 이름/폰트/링크 이미지 정보를 JSON 문자열로 반환 (읽기 전용)
(function () {
  function q(s) { return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"'; }
  if (app.documents.length === 0) return '{"open":false}';
  var d = app.activeDocument, i, parts = [];
  var fonts = [];
  for (i = 0; i < d.fonts.length && i < 80; i++) {
    var f = d.fonts[i];
    fonts.push('{"family":' + q(f.fontFamily) + ',"style":' + q(f.fontStyleName) +
               ',"status":' + q(f.status) + '}');
  }
  var links = [];
  for (i = 0; i < d.links.length && i < 80; i++) {
    var l = d.links[i];
    links.push('{"name":' + q(l.name) + ',"status":' + q(l.status) + '}');
  }
  var path = ""; try { path = d.fullName.fsName; } catch (e) {}
  return '{"open":true,"app":"InDesign","name":' + q(d.name) + ',"path":' + q(path) +
         ',"pages":' + d.pages.length + ',"fonts":[' + fonts.join(",") + '],"links":[' + links.join(",") + ']}';
})();
