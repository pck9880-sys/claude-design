/* InDesign에서 실행. 새 24쪽 검토본만 생성하며 고객 원본/기존 문서를 수정하지 않는다. */
#target indesign
(function () {
    var root = File($.fileName).parent.parent;
    var dataFile = File(root.fsName + '/data/book-data.jsxinc');
    if (!dataFile.exists) throw Error('book-data.jsxinc가 없습니다. sync_jsx_data.py를 먼저 실행하세요.');
    $.evalFile(dataFile);
    var B = BOOK_DATA, S = B.spec, unresolved = [], placed = 0;
    var bodyFont = app.fonts.itemByName(S.font + '\t' + S.font_style);
    var headFont = app.fonts.itemByName(S.font + '\t' + S.heading_style);
    if (!bodyFont.isValid || !headFont.isValid) throw Error('Pretendard Regular/Bold를 설치한 뒤 다시 실행하세요.');
    if (B.pages.length !== 24 || B.artists.length !== 10) throw Error('24쪽/10명 구성과 일치하지 않습니다.');
    var oldUI = app.scriptPreferences.userInteractionLevel, doc = null;
    var oldRange = app.pdfExportPreferences.pageRange, oldSpreads = app.pdfExportPreferences.exportReaderSpreads;
    function pad(n) { return n < 10 ? '0' + n : '' + n; }
    var now = new Date();
    var stamp = now.getFullYear() + pad(now.getMonth()+1) + pad(now.getDate()) + '_' + pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
    var out = Folder(root.fsName + '/source/indesign/review_' + stamp);
    if (out.exists) throw Error('동일한 출력 폴더가 있습니다. 잠시 후 다시 실행하세요.');
    if (!out.create()) throw Error('출력 폴더 생성 실패');
    try {
        app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
        doc = app.documents.add();
        doc.documentPreferences.properties = {pageWidth: S.width_mm+'mm', pageHeight:S.height_mm+'mm', facingPages:true, pagesPerDocument:24, documentBleedTopOffset:S.bleed_mm+'mm', documentBleedBottomOffset:S.bleed_mm+'mm', documentBleedInsideOrLeftOffset:S.bleed_mm+'mm', documentBleedOutsideOrRightOffset:S.bleed_mm+'mm'};
        doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
        doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
        doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN;
        var imageLayer = doc.layers.add({name:'01 사진·로고'});
        var textLayer = doc.layers.add({name:'02 원고·제목'});
        var colors = {};
        for (var key in B.colors) colors[key] = doc.colors.add({name:'Album_'+key,model:ColorModel.PROCESS,space:ColorSpace.RGB,colorValue:B.colors[key]});
        var none = doc.swatches.itemByName('None');
        for (var p=0;p<24;p++) doc.pages[p].marginPreferences.properties={top:18,bottom:18,left:18,right:18};
        function text(page, x,y,w,h,content,size,bold,align,color) {
            var f=page.textFrames.add({itemLayer:textLayer});f.geometricBounds=[y,x,y+h,x+w];
            f.contents=content;f.label='copy';f.textFramePreferences.insetSpacing=[0,0,0,0];
            f.parentStory.texts.everyItem().properties={appliedFont:bold?headFont:bodyFont,pointSize:size,leading:size*1.4,fillColor:colors[color||'ink']};
            f.parentStory.paragraphs.everyItem().justification=align==='center'?Justification.CENTER_ALIGN:Justification.LEFT_ALIGN;
            f.strokeWeight=0;f.strokeColor=none;return f;
        }
        function asset(id) { for(var i=0;i<B.assets.length;i++)if(B.assets[i].id===id)return B.assets[i]; return null; }
        function photo(page,id,x,y,w,h,caption) {
            var a=asset(id),f=page.rectangles.add({itemLayer:imageLayer});f.geometricBounds=[y,x,y+h,x+w];f.label=id;f.insertLabel('asset_id',id);
            f.contentType=ContentType.GRAPHIC_TYPE;f.strokeWeight=.5;f.strokeColor=colors.line;f.fillColor=colors.soft;
            if(a&&a.path) {
                if (/^(?:[A-Za-z]:|[\\\/])/.test(a.path) || /(?:^|[\\\/])\.\.(?:[\\\/]|$)/.test(a.path)) throw Error('프로젝트 밖 사진 경로 금지: '+id);
                var input=File(root.fsName+'/'+a.path);
                if(!input.exists)throw Error('사진 파일 누락: '+id+' / '+a.path);
                f.place(input);f.fit(FitOptions.PROPORTIONALLY);f.fit(FitOptions.CENTER_CONTENT);placed++;
            } else {
                unresolved.push(id);text(page,x+3,y+h/2-6,w-6,15,caption||('사진 수신 대기\n'+id),11,false,'center','muted');
            }
            return f;
        }
        function footer(page,n) {text(page,18,281,174,6,''+n,10,false,'center','muted');}
        var W=S.width_mm,H=S.height_mm;
        if(W!==210 || H!==297)throw Error('현재 검토 레이아웃은 임시 A4 기준입니다. 판형 변경 시 배치도 함께 조정하세요.');
        var cover=doc.pages[0];
        text(cover,18,20,174,16,B.title,30,true,'center');
        text(cover,18,40,174,10,B.subtitle,14,false,'center','muted');
        // 3×4 그리드의 두 셀은 여백으로 남긴다. 작품 10장은 각 작가 1장씩.
        var cells=[0,1,3,4,5,6,7,8,10,11],cw=54,ch=38,gap=6;
        for(var i=0;i<10;i++) {
            var cell=cells[i],row=Math.floor(cell/3),col=cell%3;
            photo(cover,B.artists[i].cover_asset,18+col*(cw+gap),62+row*(ch+gap),cw,ch,'표지 작품 '+(i+1)+'\n사진 대기');
        }
        photo(cover,'ORG_LOGO',18,246,16,10,'기관마크');
        text(cover,38,246,154,13,B.organization,11,true,'left');
        photo(cover,'SUPPORT_LOGO',18,264,16,10,'지원마크');
        text(cover,38,263,154,18,B.support_note,10.5,false,'left','muted');
        var greeting=doc.pages[1];
        text(greeting,18,24,174,15,'인사말',26,true);
        text(greeting,18,55,174,195,B.greeting||'[센터장 인사말 원고 추후 전달]',S.body_pt,false);
        text(greeting,18,257,174,15,B.organization+' 센터장',12,false,'left','muted');footer(greeting,2);
        var program=doc.pages[2];
        text(program,18,24,174,15,'프로그램 소개',26,true);
        text(program,18,48,174,35,B.program_intro||'[프로그램 소개글 대기]',14,false);
        text(program,18,92,174,12,'출사 및 스토리텔링',18,true);
        for(i=0;i<8;i++)text(program,18,110+i*8,174,8,(i+1)+'회기  '+(B.sessions[i]||'[주제 대기]'),12,false);
        for(i=0;i<3;i++)photo(program,'ACT0'+(i+1),18+i*60,184,54,64,'활동사진 '+(i+1)+'\n수신 대기');
        footer(program,3);
        for(i=0;i<10;i++) {
            var a=B.artists[i];
            if(!a.mapping_confirmed)unresolved.push(a.id+' 작가·작품 대응 미확정');
            for(var side=0;side<2;side++) {
                var page=doc.pages[3+i*2+side],wid=side===0?a.left_asset:a.right_asset,art=asset(wid);
                text(page,18,22,174,14,a.name||'[작가명 대기]',24,true);
                if(side===0)text(page,18,42,174,23,a.bio||'[작가소개글 추후 전달]',12,false,'left','muted');
                photo(page,wid,18,side===0?74:46,174,side===0?146:174,'작품사진 수신 대기\n'+wid);
                text(page,18,229,174,11,art.title||'[작품 제목 대기]',18,true);
                text(page,18,245,174,28,art.description||'[작품 설명 대기]',13,false);
                footer(page,4+i*2+side);
            }
        }
        var last=doc.pages[23];
        text(last,18,22,174,15,'함께한 순간들',26,true);
        for(i=0;i<6;i++)photo(last,'ACT0'+(i+4),18+(i%2)*90,48+Math.floor(i/2)*46,84,40,'활동사진 '+(i+4)+'\n수신 대기');
        text(last,18,196,174,39,B.contributors||'[참여 어르신·강사·봉사자 명단 대기]',12,false);
        text(last,18,246,174,13,B.organization,12,true);
        text(last,18,264,174,13,B.organization_info||'[기관 정보 대기]',10.5,false,'left','muted');
        doc.insertLabel('project_id',B.project);doc.insertLabel('production_state','DRAFT_MISSING_INPUTS');
        doc.recompose();
        var overflow=[];
        for(i=0;i<doc.textFrames.length;i++)if(doc.textFrames[i].overflows)overflow.push(doc.textFrames[i].parentPage.name+': '+doc.textFrames[i].contents.substring(0,45));
        var filename='인생사진첩_24p_검토구조';
        doc.save(File(out.fsName+'/'+filename+'.indd'));
        doc.exportFile(ExportFormat.INDESIGN_MARKUP,File(out.fsName+'/'+filename+'.idml'));
        // PDF 출력은 Adobe의 현재 설정을 사용한 검토본이며 인쇄용 납품본이 아니다.
        app.pdfExportPreferences.pageRange=PageRange.ALL_PAGES;
        app.pdfExportPreferences.exportReaderSpreads=false;
        doc.exportFile(ExportFormat.PDF_TYPE,File(out.fsName+'/'+filename+'_검토용.pdf'));
        var report=File(out.fsName+'/BUILD-REPORT.txt');report.encoding='UTF-8';report.open('w');
        report.writeln('검토 구조 생성. 인쇄용 완성본 아님.');
        report.writeln('페이지: '+doc.pages.length+' / 배치 사진: '+placed);
        report.writeln('임시 판형: A4, 도련 3mm. 고객 확인 전 확정 금지.');
        report.writeln('미해결:\n'+unresolved.join('\n'));
        report.writeln('오버셋:\n'+(overflow.length?overflow.join('\n'):'없음'));
        report.close();
        $.writeln('생성 완료: '+out.fsName);
    } catch(e) {
        var err=File(out.fsName+'/ERROR.txt');err.encoding='UTF-8';err.open('w');err.write(String(e)+'\nline='+e.line);err.close();throw e;
    } finally {
        app.scriptPreferences.userInteractionLevel=oldUI;
        app.pdfExportPreferences.pageRange=oldRange;
        app.pdfExportPreferences.exportReaderSpreads=oldSpreads;
    }
}());
