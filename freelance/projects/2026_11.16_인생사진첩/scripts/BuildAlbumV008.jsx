/* 인생사진첩 v007 — 실제 작품·활동 사진(CMYK) + 남산정 활동북 스타일 내지.
   사진 파일명(작가명 작품제목)을 기준으로 작가·작품을 배치한다. 원고에 없는 글은 (임의) 표기.
   기존 문서는 수정하지 않고 source/indesign/v007_<시각>/ 에 새로 만든다. */
#target indesign
(function () {
    var root = File($.fileName).parent.parent;
    $.evalFile(File(root.fsName + '/data/album_v007.jsxinc'));
    var D = ALBUM, PW = 210, PH = 297, BLEED = 3, BAND = 7;
    function font(f, s) { var x = app.fonts.itemByName(f + '\t' + s); if (!x.isValid) throw Error('폰트 없음: ' + f + ' ' + s); return x; }
    var F = { r: font('Pretendard', 'Regular'), m: font('Pretendard', 'Medium'), b: font('Pretendard', 'Bold'), serif: font('Noto Serif CJK KR', 'Bold') };
    function pad(n) { return n < 10 ? '0' + n : '' + n; }
    var dt = new Date(), stamp = dt.getFullYear() + pad(dt.getMonth() + 1) + pad(dt.getDate()) + '_' + pad(dt.getHours()) + pad(dt.getMinutes()) + pad(dt.getSeconds());
    var out = Folder(root.fsName + '/source/indesign/v008_' + stamp); if (!out.create()) throw Error('결과 폴더 생성 실패');
    var oldUI = app.scriptPreferences.userInteractionLevel;
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.documents.add();
    try {
        doc.documentPreferences.properties = { pageWidth: PW + 'mm', pageHeight: PH + 'mm', facingPages: true, pagesPerDocument: 24,
            documentBleedTopOffset: BLEED + 'mm', documentBleedBottomOffset: BLEED + 'mm', documentBleedInsideOrLeftOffset: BLEED + 'mm', documentBleedOutsideOrRightOffset: BLEED + 'mm' };
        doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
        doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
        doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN;
        doc.textDefaults.appliedFont = F.r;
        // 남산정 톤 CMYK 색상
        function cmyk(n, v) { return doc.colors.add({ name: n, model: ColorModel.PROCESS, space: ColorSpace.CMYK, colorValue: v }); }
        var C = { mauve: cmyk('NS_모브', [8, 62, 28, 12]), rose: cmyk('NS_로즈띠', [0, 20, 7, 3]), beige: cmyk('NS_베이지', [3, 5, 12, 0]),
            sand: cmyk('NS_샌드띠', [6, 9, 22, 2]), ink: cmyk('NS_본문', [0, 0, 0, 85]), gray: cmyk('NS_회색', [0, 0, 0, 55]),
            t1: cmyk('NS_타일로즈', [0, 42, 20, 6]), t2: cmyk('NS_타일샌드', [6, 22, 42, 6]), t3: cmyk('NS_타일세이지', [36, 6, 26, 12]),
            t4: cmyk('NS_타일블루', [38, 16, 10, 10]), t5: cmyk('NS_타일피치', [0, 32, 36, 2]) };
        var paper = doc.swatches.itemByName('Paper'), none = doc.swatches.itemByName('None');
        var lyPhoto = doc.layers.add({ name: '01 사진' }), lyText = doc.layers.add({ name: '02 글' });
        for (var mi = 0; mi < doc.masterSpreads.length; mi++) for (var mp = 0; mp < doc.masterSpreads[mi].pages.length; mp++)
            doc.masterSpreads[mi].pages[mp].marginPreferences.properties = { top: 15, bottom: 15, left: 15, right: 15 };
        var overs = [], placed = 0;
        function gb(x, y, w, h) { return [y, x, y + h, x + w]; }
        function round(o, r) { o.properties = { topLeftCornerOption: CornerOptions.ROUNDED_CORNER, topRightCornerOption: CornerOptions.ROUNDED_CORNER,
            bottomLeftCornerOption: CornerOptions.ROUNDED_CORNER, bottomRightCornerOption: CornerOptions.ROUNDED_CORNER,
            topLeftCornerRadius: r, topRightCornerRadius: r, bottomLeftCornerRadius: r, bottomRightCornerRadius: r }; }
        function rect(pg, x, y, w, h, fill, r, name) { var o = pg.rectangles.add({ itemLayer: lyPhoto, geometricBounds: gb(x, y, w, h), fillColor: fill || none, strokeWeight: 0, strokeColor: none });
            if (r) round(o, r); if (name) o.name = name; return o; }
        function line(pg, x1, y1, x2, y2, col, wt) { var l = pg.graphicLines.add({ itemLayer: lyText }); l.paths[0].pathPoints[0].anchor = [x1, y1]; l.paths[0].pathPoints[1].anchor = [x2, y2];
            l.strokeColor = col; l.strokeWeight = wt || 0.5; return l; }
        function text(pg, x, y, w, h, s, o) {
            o = o || {}; var t = pg.textFrames.add({ itemLayer: lyText, geometricBounds: gb(x, y, w, h), contents: s });
            t.textFramePreferences.insetSpacing = o.inset || [0, 0, 0, 0];
            if (o.vcenter) t.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
            if (o.fill) t.fillColor = o.fill;
            var p = t.parentStory.texts[0];
            p.appliedFont = o.font || F.r; p.pointSize = o.size || 9.5; p.leading = (o.size || 9.5) * (o.lead || 1.6);
            p.fillColor = o.color || C.ink; p.hyphenation = false; p.tracking = o.track || 0;
            // ExtendScript는 중첩 삼항 연산자를 잘못 해석하므로 if 문으로 처리
            var j = Justification.LEFT_ALIGN;
            if (o.align === 'center') j = Justification.CENTER_ALIGN;
            else if (o.align === 'right') j = Justification.RIGHT_ALIGN;
            p.justification = j;
            if (o.name) t.name = o.name;
            return t;
        }
        function photo(pg, path, px, bx, by, bw, bh, mode, r, name) {
            // mode 'fit': 사진 비율 그대로 상자 안에 최대 크기(자르지 않음) / 'fill': 상자를 채움(모자이크·배경)
            var w = bw, h = bh, ar = px[0] / px[1];
            if (mode === 'fit') { if (bw / bh > ar) { h = bh; w = bh * ar; } else { w = bw; h = bw / ar; } }
            var x = bx + (bw - w) / 2, y = by + (bh - h) / 2;
            var fr = rect(pg, x, y, w, h, null, r, name); fr.contentType = ContentType.GRAPHIC_TYPE;
            var f = File(root.fsName + '/' + path); if (!f.exists) throw Error('사진 없음: ' + path);
            fr.place(f); fr.fit(mode === 'fit' ? FitOptions.PROPORTIONALLY : FitOptions.FILL_PROPORTIONALLY); fr.fit(FitOptions.CENTER_CONTENT);
            placed++; return [x, y, w, h];
        }
        function isLeft(n) { return n % 2 === 0; }
        // 남산정식 테두리 띠(위·바깥쪽·아래) + 상단 머리글·쪽번호
        function frame(pg, n, section, band, folioOnly) {
            var L = isLeft(n);
            rect(pg, -BLEED - (L ? 0 : 0), -BLEED, PW + BLEED * 2, BAND + BLEED, band);                 // 위
            rect(pg, -BLEED, PH - BAND, PW + BLEED * 2, BAND + BLEED, band);                              // 아래
            if (L) rect(pg, -BLEED, -BLEED, BAND + BLEED, PH + BLEED * 2, band); else rect(pg, PW - BAND, -BLEED, BAND + BLEED, PH + BLEED * 2, band); // 바깥쪽
            var hy = 11.5, num = pad(n), run = D.title + '  |  ' + D.subtitle.replace(/[「」]/g, '');
            if (folioOnly) {
                if (L) { text(pg, 15, hy, 10, 5, num, { font: F.b, size: 9, color: C.mauve, name: 'Folio' }); }
                else { text(pg, 185, hy, 10, 5, num, { font: F.b, size: 9, color: C.mauve, align: 'right', name: 'Folio' }); }
                return;
            }
            if (L) {
                text(pg, 15, hy, 10, 5, num, { font: F.b, size: 9, color: C.mauve, name: 'Folio' });
                line(pg, 24, hy + 2.3, 32, hy + 2.3, C.mauve, 0.5);
                text(pg, 34, hy + 0.6, 100, 4, run, { size: 6.5, color: C.gray, name: 'Running' });
                text(pg, 120, hy + 0.6, 75, 4, section, { font: F.m, size: 6.5, color: C.mauve, align: 'right', name: 'Section' });
            } else {
                text(pg, 15, hy + 0.6, 75, 4, section, { font: F.m, size: 6.5, color: C.mauve, name: 'Section' });
                text(pg, 76, hy + 0.6, 100, 4, run, { size: 6.5, color: C.gray, align: 'right', name: 'Running' });
                line(pg, 178, hy + 2.3, 186, hy + 2.3, C.mauve, 0.5);
                text(pg, 185, hy, 10, 5, num, { font: F.b, size: 9, color: C.mauve, align: 'right', name: 'Folio' });
            }
        }
        // 섹션 알약 + 큰 명조 제목 + 오른쪽으로 뻗는 선(남산정 '우리의 시간 가까이 보기' 구성)
        function heading(pg, n, pill, title, sub) {
            var x0 = isLeft(n) ? 20 : 17, x1 = isLeft(n) ? 193 : 190;
            var p = text(pg, x0, 22, 46, 6.2, pill, { font: F.m, size: 7.5, color: paper, align: 'center', vcenter: true, fill: C.mauve, name: 'Pill' }); round(p, 3.1);
            text(pg, x0, 30, 120, 12, title, { font: F.serif, size: 20, lead: 1.2, color: C.mauve, name: 'Title' });
            line(pg, x0 + (sub ? 70 : 60), 37, x1 - (sub ? 42 : 0), 37, C.mauve, 0.5);
            if (sub) text(pg, x1 - 40, 35.2, 40, 4, sub, { size: 7, color: C.mauve, align: 'right', name: 'Sub' });
        }
        function capbox(pg, x, y, w, title, desc) {
            var b = rect(pg, x, y, w, 21, C.beige, 2.5, 'CaptionBox');
            text(pg, x + 6, y + 4.2, w - 12, 5, title, { font: F.b, size: 10.5, color: C.mauve, name: 'WorkTitle' });
            text(pg, x + 6, y + 11.2, w - 12, 6, desc, { size: 8.5, color: C.gray, name: 'WorkDesc' });
        }
        // ---------- 1쪽 표지 ----------
        var pg = doc.pages[0];
        // 표지 테두리(사방)
        rect(pg, -BLEED, -BLEED, PW + BLEED * 2, BAND + BLEED, C.rose); rect(pg, -BLEED, PH - BAND, PW + BLEED * 2, BAND + BLEED, C.rose);
        rect(pg, -BLEED, -BLEED, BAND + BLEED, PH + BLEED * 2, C.rose); rect(pg, PW - BAND, -BLEED, BAND + BLEED, PH + BLEED * 2, C.rose);
        var T = 38, G = 5, gx = (PW - (T * 3 + G * 2)) / 2, rows = [[0, 1, 1], [1, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1]], letters = ['ㅇ', 'ㅅ', 'ㅅ', 'ㅈ', 'ㅊ'], tiles = [C.t1, C.t3, C.t2, C.t4, C.t5];
        var li = 0, pi = 0;
        for (var r = 0; r < 5; r++) {
            var ry = 14 + r * (T + G) + (r >= 3 ? 34 : 0);
            for (var c = 0; c < 3; c++) {
                var tx = gx + c * (T + G);
                if (rows[r][c] === 0) { var tt = text(pg, tx, ry, T, T, letters[li], { font: F.serif, size: 54, lead: 1, color: paper, align: 'center', vcenter: true, fill: tiles[li], name: 'LetterTile' }); round(tt, 4); li++; }
                else { var a = D.artists[pi]; photo(pg, a.works[0].path, a.works[0].px, tx, ry, T, T, 'fill', 4, 'Cover_' + a.name); pi++; }
            }
        }
        var by = 14 + 3 * (T + G);
        text(pg, 20, by + 1, 170, 15, D.title, { font: F.serif, size: 30, lead: 1.1, color: C.mauve, align: 'center', name: 'CoverTitle' });
        text(pg, 20, by + 17, 170, 7, D.subtitle, { font: F.m, size: 12, color: C.ink, align: 'center', name: 'CoverSubtitle' });
        var ly = 266;
        text(pg, 30, ly, 22, 9, '(임시) 기관마크', { size: 6.5, color: C.gray, align: 'center', vcenter: true, fill: C.beige, name: 'TempOrgLogo' });
        text(pg, 54, ly, 60, 9, D.org, { font: F.m, size: 7.5, color: C.ink, vcenter: true, name: 'CoverOrg' });
        text(pg, 116, ly, 22, 9, '(임시) 사랑의열매', { size: 6.5, color: C.gray, align: 'center', vcenter: true, fill: C.beige, name: 'TempSupportLogo' });
        text(pg, 140, ly, 50, 9, D.support, { size: 6.5, lead: 1.4, color: C.gray, vcenter: true, name: 'CoverSupport' });
        // ---------- 2쪽 목차 + 인사말 ----------
        pg = doc.pages[1]; frame(pg, 2, '목차 · 인사말', C.sand);
        for (var g = 0; g < 6; g++) { var tp = D.toc_photos[g]; photo(pg, tp.path, tp.px, BAND + (g % 3) * ((PW - BAND) / 3), 17 + Math.floor(g / 3) * 55, (PW - BAND) / 3, 55, 'fill', 0, 'TocBgTemp_' + tp.no); }
        text(pg, 160, 121, 48, 4, '(임의) 배경 사진은 임시 배치', { size: 5.5, color: paper, align: 'right', name: 'TempNote' });
        var card = rect(pg, 30, 28, 88, 100, paper, 0, 'TocCard');
        text(pg, 40, 37, 60, 10, '목차', { font: F.serif, size: 18, color: C.mauve, name: 'TocTitle' });
        line(pg, 40, 49, 108, 49, C.mauve, 0.5);
        text(pg, 40, 51.5, 68, 5, D.title + ' ' + D.subtitle, { font: F.m, size: 7, color: C.gray, name: 'TocSub' });
        var toc = [['인사말', '02'], ['프로그램 소개', '03'], ['어르신 작품', '04'], ['함께한 순간들', '24']], ty = 60;
        for (var k = 0; k < toc.length; k++) {
            text(pg, 40, ty, 52, 5, '→  ' + toc[k][0], { font: F.m, size: 8.5, color: C.ink, name: 'TocItem' });
            text(pg, 94, ty, 14, 5, toc[k][1], { size: 8.5, color: C.mauve, align: 'right', name: 'TocPage' });
            if (k === 2) { var names = []; for (var q = 0; q < D.artists.length; q++) names.push(D.artists[q].name + ' ' + pad(4 + q * 2));
                text(pg, 46, ty + 6.5, 62, 22, names.slice(0, 5).join('\r'), { size: 7, lead: 1.55, color: C.gray, name: 'TocArtistsA' });
                text(pg, 78, ty + 6.5, 30, 22, names.slice(5).join('\r'), { size: 7, lead: 1.55, color: C.gray, name: 'TocArtistsB' }); ty += 27; }
            else ty += 8;
        }
        heading2: {
            var p2 = text(pg, 20, 140, 30, 6.2, '인사말', { font: F.m, size: 7.5, color: paper, align: 'center', vcenter: true, fill: C.mauve, name: 'Pill' }); round(p2, 3.1);
            text(pg, 20, 149, 120, 11, '마음으로 담은 한 장의 사진', { font: F.serif, size: 17, color: C.mauve, name: 'Title' });
            text(pg, 20, 163, 170, 92, D.greeting, { size: 9.3, lead: 1.75, color: C.ink, name: 'GreetingCopy' });
            text(pg, 100, 262, 93, 10, D.org + ' 센터장', { font: F.m, size: 8, color: C.ink, align: 'right', name: 'GreetingSign' });
        }
        // ---------- 3쪽 프로그램 소개 ----------
        pg = doc.pages[2]; frame(pg, 3, '프로그램 소개', C.sand);
        heading(pg, 3, '프로그램 소개', '“인생사진첩”을 소개합니다.', null);
        text(pg, 17, 52, 34, 12, '프로그램\r소개글', { font: F.serif, size: 10.5, lead: 1.35, color: C.mauve, name: 'Label' });
        text(pg, 56, 52, 134, 26, D.program_copy, { size: 9.3, lead: 1.75, name: 'ProgramCopy' });
        line(pg, 17, 82, 190, 82, C.rose, 0.5);
        text(pg, 17, 87, 34, 18, '출사 및\r스토리텔링\r8회기', { font: F.serif, size: 10.5, lead: 1.35, color: C.mauve, name: 'Label' });
        for (var s = 0; s < 8; s++) {
            var sx = 56 + (s % 2) * 68, sy = 87 + Math.floor(s / 2) * 9;
            text(pg, sx, sy, 9, 5, pad(s + 1), { font: F.b, size: 8, color: C.mauve, name: 'SessionNo' });
            text(pg, sx + 9, sy, 58, 5, D.sessions[s], { size: 8.5, name: 'Session_' + (s + 1) });
        }
        line(pg, 17, 126, 190, 126, C.rose, 0.5);
        text(pg, 17, 131, 40, 6, '활동 사진', { font: F.serif, size: 10.5, color: C.mauve, name: 'Label' });
        // 왼쪽 열: 1·2번(가로) 위아래, 오른쪽 열: 3번(세로). 비율 그대로 배치해 자르지 않는다.
        var colW = 84, ph = colW * D.program_photos[0].px[1] / D.program_photos[0].px[0];
        photo(pg, D.program_photos[0].path, D.program_photos[0].px, 17, 140, colW, ph, 'fit', 3, 'Activity_' + D.program_photos[0].no);
        photo(pg, D.program_photos[1].path, D.program_photos[1].px, 17, 145 + ph, colW, ph, 'fit', 3, 'Activity_' + D.program_photos[1].no);
        photo(pg, D.program_photos[2].path, D.program_photos[2].px, 106, 140, colW, ph * 2 + 5, 'fit', 3, 'Activity_' + D.program_photos[2].no);
        // ---------- 4~23쪽 작가 ----------
        // v005 내지 레이아웃(좌표·글 구성) 유지 + 남산정식 테두리·상단 쪽번호. 사진은 원래 틀 안에 비율 그대로(자르지 않음).
        var V = D.v005_colors, vInk = cmyk('V5_본문', V.ink), vMuted = cmyk('V5_보조', V.muted), vLine = cmyk('V5_선', V.line);
        for (var ai = 0; ai < D.artists.length; ai++) {
            var A = D.artists[ai], nL = 4 + ai * 2, sec = '어르신 작품 ' + pad(ai + 1);
            var acc = cmyk('V5_포인트_' + A.name, A.accent);
            var tint = cmyk('V5_테두리_' + A.name, [A.accent[0] * 0.3, A.accent[1] * 0.3, A.accent[2] * 0.3, A.accent[3] * 0.3]);
            // 왼쪽 쪽
            pg = doc.pages[nL - 1]; frame(pg, nL, sec, tint, true);
            text(pg, 137, 15, 49, 6, D.title, { font: F.b, size: 8, color: vMuted, align: 'right', name: 'Book' });
            line(pg, 17, 17, 45, 17, acc, 0.45); line(pg, 17, 17, 17, 38, acc, 0.45);
            var w0 = A.works[0]; photo(pg, w0.path, w0.px, 25, 25, 161, 145, 'fill', 0, 'Work_' + A.name + '_1');
            line(pg, 194, 156, 194, 178, acc, 0.45); line(pg, 174, 178, 194, 178, acc, 0.45);
            text(pg, 25, 174, 155, 6, '작품 01  /  ' + w0.title, { size: 9, lead: 1.4, color: vMuted, name: 'Caption' });
            var sb = rect(pg, 25, 190, 32, 73, paper, 0, 'SideTitleBox'); sb.strokeColor = acc; sb.strokeWeight = 0.45;
            text(pg, 29, 196, 24, 62, A.side_title, { font: F.b, size: 15, lead: 1.25, color: acc, name: 'SideTitle' });
            text(pg, 65, 190, 121, 9, A.name + ' 작가', { font: F.b, size: 14, lead: 1.45, color: acc, name: 'Author' });
            text(pg, 65, 203, 121, 20, A.bio, { size: 11, lead: 1.55, color: vInk, name: 'Intro' });
            line(pg, 65, 226, 186, 226, vLine, 0.4);
            text(pg, 65, 229, 56, 7, '사진에 담은 순간', { font: F.b, size: 10.5, lead: 1.45, color: acc, name: 'Section' });
            text(pg, 65, 240, 56, 26, D.desc_placeholder, { size: 10.5, lead: 1.6, color: vMuted, name: 'Body' });
            text(pg, 132, 229, 54, 7, '작가의 한마디', { font: F.b, size: 10.5, lead: 1.45, color: acc, name: 'Section' });
            text(pg, 132, 240, 54, 26, A.quote, { font: F.b, size: 11.5, lead: 1.5, color: vInk, name: 'Quote' });
            line(pg, 25, 275, 186, 275, vLine, 0.35);
            text(pg, 45, 278, 50, 4, D.title, { size: 8, color: vMuted, name: 'Running' });
            text(pg, 100, 278, 86, 4, D.subtitle.replace(/[「」]/g, ''), { size: 8, color: vMuted, align: 'right', name: 'Running' });
            // 오른쪽 쪽
            pg = doc.pages[nL]; frame(pg, nL + 1, sec, tint, true);
            var w1 = A.works[1];
            text(pg, 25, 25, 161, 10, w1.title, { font: F.b, size: 18, lead: 1.4, color: acc, name: 'RightWorkTitle' });
            text(pg, 25, 39, 161, 18, D.desc_placeholder, { size: 11, lead: 1.6, color: vMuted, name: 'RightWorkDescription' });
            photo(pg, w1.path, w1.px, 25, 65, 161, 199, 'fill', 0, 'Work_' + A.name + '_2');
        }
        // ---------- 24쪽 함께한 순간들 ----------
        pg = doc.pages[23]; frame(pg, 24, '함께한 순간들', C.sand);
        heading(pg, 24, '마무리', '함께한 순간들', '활동 사진');
        var cw = (173 - 2 * 5) / 3, ch = 52;
        for (var c6 = 0; c6 < 6; c6++) { var cp = D.closing_photos[c6]; photo(pg, cp.path, cp.px, 20 + (c6 % 3) * (cw + 5), 47 + Math.floor(c6 / 3) * (ch + 5), cw, ch, 'fill', 3, 'Closing_' + cp.no); }
        var ib = rect(pg, 20, 165, 173, 70, C.beige, 3, 'ThanksBox');
        text(pg, 28, 172, 80, 6, '함께해 주신 분들', { font: F.serif, size: 11, color: C.mauve, name: 'Label' });
        var nm = []; for (var z = 0; z < D.artists.length; z++) nm.push(D.artists[z].name);
        text(pg, 28, 182, 22, 5, '참여 어르신', { font: F.b, size: 8.5, color: C.mauve, name: 'Label' });
        text(pg, 52, 182, 133, 12, nm.join('  ·  '), { size: 8.8, lead: 1.6, name: 'Participants' });
        text(pg, 28, 198, 22, 5, '강사·봉사자', { font: F.b, size: 8.5, color: C.mauve, name: 'Label' });
        text(pg, 52, 198, 133, 6, D.staff, { size: 8.8, name: 'Staff' });
        line(pg, 28, 210, 185, 210, C.mauve, 0.4);
        text(pg, 28, 214, 22, 5, '기관 정보', { font: F.b, size: 8.5, color: C.mauve, name: 'Label' });
        text(pg, 52, 214, 133, 5, D.org, { font: F.m, size: 8.8, name: 'OrgName' });
        text(pg, 52, 221, 133, 5, D.org_info, { size: 8.3, color: C.gray, name: 'OrgInfo' });
        text(pg, 20, 244, 22, 9, '(임시) 기관마크', { size: 6.5, color: C.gray, align: 'center', vcenter: true, fill: C.beige, name: 'TempOrgLogo' });
        text(pg, 44, 244, 22, 9, '(임시) 사랑의열매', { size: 6.5, color: C.gray, align: 'center', vcenter: true, fill: C.beige, name: 'TempSupportLogo' });
        text(pg, 70, 244, 123, 9, D.support, { size: 7, color: C.gray, vcenter: true, name: 'Support' });
        // ---------- 검사·저장 ----------
        doc.recompose();
        for (var o = 0; o < doc.textFrames.length; o++) if (doc.textFrames[o].overflows) overs.push('p' + doc.textFrames[o].parentPage.name + ' ' + doc.textFrames[o].name);
        var stem = '인생사진첩_24p_v008_실사진_내지배치';
        doc.save(File(out.fsName + '/' + stem + '.indd'));
        var rep = File(out.fsName + '/BUILD-REPORT.txt'); rep.encoding = 'UTF-8'; rep.open('w');
        rep.writeln('v007 실사진(CMYK JapanColor2001Coated) + 남산정 스타일. 원고에 없는 글은 (임의), 로고는 (임시).');
        rep.writeln('페이지: ' + doc.pages.length + ' / 사진: ' + placed + ' / 오버셋: ' + overs.length); rep.writeln(overs.join('\n')); rep.close();
        $.writeln(out.fsName);
        return 'OK pages=' + doc.pages.length + ' placed=' + placed + ' overflow=' + overs.length + ' ' + overs.join(', ') + ' out=' + out.fsName;
    } catch (e) { var lg = File(out.fsName + '/ERROR.txt'); lg.encoding = 'UTF-8'; lg.open('w'); lg.write(e + ' line=' + e.line); lg.close(); return 'FAIL ' + e + ' line=' + e.line; }
    finally { app.scriptPreferences.userInteractionLevel = oldUI; }
}());
