/* Adobe ExtendScript 실행 점검. 문서 생성/수정/저장과 네트워크 요청 없음. */
(function () {
    var name = String(app.name);
    var version = String(app.version);
    alert('Adobe script connection OK\nApplication: ' + name + '\nVersion: ' + version + '\nNo document was changed.');
}());
