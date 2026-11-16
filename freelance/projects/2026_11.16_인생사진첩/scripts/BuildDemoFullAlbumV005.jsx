/* InDesign 네이티브 DOM으로 전체24쪽을 생성. 기존 문서는 수정하지 않는다. */
#target indesign
(function () {
    var root=File($.fileName).parent.parent;
    $.evalFile(File(root.fsName+'/data/book-data.jsxinc'));
    $.evalFile(File(root.fsName+'/data/layout_demo_full_v005.jsxinc'));
    var B=BOOK_DATA,L=ALBUM_LAYOUT;
    B.assets=B.assets.concat(L.demo_assets||[]);
    if(L.pages.length!==24)throw Error('24쪽 배치 데이터가 필요합니다.');
    var normal=app.fonts.itemByName('Pretendard\tRegular'),bold=app.fonts.itemByName('Pretendard\tBold');
    if(!normal.isValid||!bold.isValid)throw Error('Pretendard Regular와 Bold를 설치해야 합니다.');
    var oldUI=app.scriptPreferences.userInteractionLevel,oldRange=app.pdfExportPreferences.pageRange,oldSpread=app.pdfExportPreferences.exportReaderSpreads;
    function pad(n){return n<10?'0'+n:''+n;}
    var d=new Date(),stamp=d.getFullYear()+pad(d.getMonth()+1)+pad(d.getDate())+'_'+pad(d.getHours())+pad(d.getMinutes())+pad(d.getSeconds());
    var output=Folder(root.fsName+'/source/indesign/full_demo_v005_'+stamp);
    if(output.exists||!output.create())throw Error('새 결과 폴더 생성 실패');
    var document=null,missing=[],overflow=[],placed=0;
    function getAsset(id){for(var i=0;i<B.assets.length;i++)if(B.assets[i].id===id)return B.assets[i];return null;}
    function assetFile(id){var a=getAsset(id);if(!a||!a.path)return null;if(/^(?:[A-Za-z]:|[\\\/])/.test(a.path)||/(?:^|[\\\/])\.\.(?:[\\\/]|$)/.test(a.path))throw Error('프로젝트 밖 자산 경로: '+id);var f=File(root.fsName+'/'+a.path);if(!f.exists)throw Error('등록된 자산 파일 누락: '+id);return f;}
    try {
        app.scriptPreferences.userInteractionLevel=UserInteractionLevels.NEVER_INTERACT;
        document=app.documents.add();
        document.documentPreferences.properties={pageWidth:L.spec.width_mm+'mm',pageHeight:L.spec.height_mm+'mm',facingPages:true,pagesPerDocument:24,documentBleedTopOffset:L.spec.bleed_mm+'mm',documentBleedBottomOffset:L.spec.bleed_mm+'mm',documentBleedInsideOrLeftOffset:L.spec.bleed_mm+'mm',documentBleedOutsideOrRightOffset:L.spec.bleed_mm+'mm'};
        document.viewPreferences.horizontalMeasurementUnits=MeasurementUnits.MILLIMETERS;
        document.viewPreferences.verticalMeasurementUnits=MeasurementUnits.MILLIMETERS;
        document.viewPreferences.rulerOrigin=RulerOrigin.SPREAD_ORIGIN;
        document.sections[0].continueNumbering=false;document.sections[0].pageNumberStart=1;
        for(var mi=0;mi<document.masterSpreads.length;mi++){for(var mp=0;mp<document.masterSpreads[mi].pages.length;mp++)document.masterSpreads[mi].pages[mp].marginPreferences.properties={top:15,bottom:15,left:15,right:15};}
        var pictures=document.layers.add({name:'01 사진·로고'}),copy=document.layers.add({name:'02 원고·제목'}),colors={};
        var none=document.swatches.itemByName('None');
        for(var name in L.colors)colors[name]=document.colors.add({name:'Album_'+name,model:ColorModel.PROCESS,space:ColorSpace.RGB,colorValue:L.colors[name]});
        for(name in L.styles){var st=L.styles[name];document.paragraphStyles.add({name:'Album_'+name,appliedFont:st[1]==='Bold'?bold:normal,pointSize:st[0],leading:st[0]*(st[2]||1.5),hyphenation:false});}
        function bounds(page,a){var b=page.bounds;return[b[0]+a.y,b[1]+a.x,b[0]+a.y+a.h,b[1]+a.x+a.w];}
        for(var pi=0;pi<L.pages.length;pi++){
            var design=L.pages[pi],page=document.pages[pi];
            page.marginPreferences.properties={top:15,bottom:15,left:15,right:15};
            for(var ii=0;ii<design.items.length;ii++){
                var a=design.items[ii],obj;
                if(a.kind==='text'){
                    if(a.name.indexOf('Placeholder_')===0&&assetFile(a.name.substring(12)))continue;
                    obj=page.textFrames.add({itemLayer:copy});obj.geometricBounds=bounds(page,a);obj.contents=a.text;obj.name=a.name;
                    if(a.style==='Folio'){obj.geometricBounds=bounds(page,{x:design.page%2===0?25:174,y:a.y,w:a.w,h:a.h});}
                    obj.strokeWeight=0;obj.strokeColor=none;obj.textFramePreferences.insetSpacing=[0,0,0,0];
                    obj.parentStory.paragraphs.everyItem().appliedParagraphStyle=document.paragraphStyles.itemByName('Album_'+a.style);
                    obj.parentStory.texts.everyItem().fillColor=colors[a.color];
                    obj.parentStory.paragraphs.everyItem().justification=a.style==='Folio'?(design.page%2===0?Justification.LEFT_ALIGN:Justification.RIGHT_ALIGN):(a.align==='center'?Justification.CENTER_ALIGN:a.align==='right'?Justification.RIGHT_ALIGN:Justification.LEFT_ALIGN);
                }else{
                    obj=a.kind==='ellipse'?page.ovals.add({itemLayer:pictures}):page.rectangles.add({itemLayer:pictures});obj.geometricBounds=bounds(page,a);obj.name=a.name;obj.fillColor=a.kind==='frame'?colors.soft:(a.fill?colors[a.fill]:none);
                    obj.strokeWeight=a.stroke_weight||0;obj.strokeColor=a.stroke?colors[a.stroke]:none;
                    if(a.opacity!==undefined)obj.transparencySettings.blendingSettings.opacity=a.opacity;
                    if(a.kind==='frame'){
                        obj.contentType=ContentType.GRAPHIC_TYPE;obj.insertLabel('asset_id',a.asset_id);
                        var image=assetFile(a.asset_id);
                        if(image){
                            var graphic=obj.place(image)[0];
                            if(a.sheet_crop){
                                var sourceAsset=getAsset(a.asset_id),crop=a.sheet_crop;
                                var scale=Math.max(a.w/(sourceAsset.pixel_width*crop[2]),a.h/(sourceAsset.pixel_height*crop[3]));
                                var iw=sourceAsset.pixel_width*scale,ih=sourceAsset.pixel_height*scale;
                                graphic.geometricBounds=bounds(page,{x:a.x+a.w/2-(crop[0]+crop[2]/2)*iw,y:a.y+a.h/2-(crop[1]+crop[3]/2)*ih,w:iw,h:ih});
                            }else{obj.fit(a.fit==='fill'?FitOptions.FILL_PROPORTIONALLY:FitOptions.PROPORTIONALLY);obj.fit(FitOptions.CENTER_CONTENT);}
                            placed++;
                        }else missing.push(a.asset_id);
                    }
                }
                obj.insertLabel('layout_page',''+design.page);
            }
        }
        document.recompose();
        for(var ti=0;ti<document.textFrames.length;ti++){var tf=document.textFrames[ti];if(tf.overflows)overflow.push(tf.parentPage.name+': '+tf.contents.substring(0,60));}
        document.insertLabel('project',B.project);document.insertLabel('draft_state','DEMO_PHOTOS_NAMES_TEXT_NOT_CLIENT_ORIGINAL');
        var stem='인생사진첩_전체24p_사진원고예시_v005';
        document.save(File(output.fsName+'/'+stem+'.indd'));
        document.exportFile(ExportFormat.INDESIGN_MARKUP,File(output.fsName+'/'+stem+'.idml'));
        app.pdfExportPreferences.pageRange=PageRange.ALL_PAGES;app.pdfExportPreferences.exportReaderSpreads=false;
        document.exportFile(ExportFormat.PDF_TYPE,File(output.fsName+'/'+stem+'.pdf'));
        var report=File(output.fsName+'/BUILD-REPORT.txt');report.encoding='UTF-8';report.open('w');
        report.writeln('전체24쪽 디자인 예시. 인명·원고·AI 사진은 사용자 허용 임의자료. 고객 실제기록/최종 인쇄본 아님.');
        report.writeln('실제 페이지: '+document.pages.length+' / 이미지 배치: '+placed+' / 오버셋: '+overflow.length);
        report.writeln('미배치 자산:\n'+missing.join('\n'));report.writeln('오버셋:\n'+overflow.join('\n'));report.close();
        $.writeln('생성: '+output.fsName);
    }catch(e){var log=File(output.fsName+'/ERROR.txt');log.encoding='UTF-8';log.open('w');log.write(String(e)+'\nline='+e.line);log.close();throw e;}
    finally{app.scriptPreferences.userInteractionLevel=oldUI;app.pdfExportPreferences.pageRange=oldRange;app.pdfExportPreferences.exportReaderSpreads=oldSpread;}
}());
