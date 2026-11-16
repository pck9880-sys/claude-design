/* Photoshop: 활동사진 15장, 폭10cm/300ppi/비율유지/자동리샘플. 원본 보존. */
#target photoshop
(function () {
    var REQUIRED=15, WIDTH_CM=10, PPI=300;
    var source=Folder.selectDialog('활동사진 15장이 있는 폴더를 선택하세요.');
    if(!source)return;
    function supported(f){return f instanceof File&&/\.(jpe?g|png|tiff?|psd)$/i.test(f.name);}
    function nameOf(f){try{return decodeURI(f.name);}catch(e){return f.name;}}
    var files=source.getFiles(supported);
    if(files.length!==REQUIRED){
        Folder.current=source;
        files=File.openDialog('활동사진을 정확히 15장 선택하세요.','Images:*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.psd',true);
        if(!files)return;
    }
    if(files.length!==REQUIRED){alert('15장을 선택해야 합니다. 현재 '+files.length+'장. 파일은 수정하지 않았습니다.');return;}
    var seen={};
    for(var i=0;i<files.length;i++){
        if(!supported(files[i])||files[i].parent.fsName!==source.fsName){alert('처음 선택한 활동사진 폴더 안의 JPG/PNG/TIFF/PSD만 선택하세요. 파일은 수정하지 않았습니다.');return;}
        if(seen[files[i].fsName]){alert('중복 파일이 있습니다. 파일은 수정하지 않았습니다.');return;}
        seen[files[i].fsName]=true;
    }
    files.sort(function(a,b){var aa=nameOf(a).toLowerCase(),bb=nameOf(b).toLowerCase();return aa<bb?-1:aa>bb?1:0;});
    if(typeof ResampleMethod.AUTOMATIC==='undefined'){alert('이 Photoshop 버전에서 자동 리샘플링을 확인할 수 없어 중단했습니다. 원본은 변경하지 않았습니다.');return;}
    function pad(n){return n<10?'0'+n:''+n;}
    var now=new Date(),stamp=now.getFullYear()+pad(now.getMonth()+1)+pad(now.getDate())+'_'+pad(now.getHours())+pad(now.getMinutes())+pad(now.getSeconds());
    var output=Folder(source.fsName+'/폭10cm_300ppi_15장_'+stamp);
    if(output.exists||!output.create()){alert('새 결과 폴더 생성에 실패했습니다.');return;}
    var temporary=Folder(output.fsName+'/_processing');
    if(!temporary.create()){alert('임시 폴더 생성에 실패했습니다.');return;}
    var previousDialogs=app.displayDialogs,previousDocument=null;
    if(app.documents.length)previousDocument=app.activeDocument;
    var success=0,errors=[],rows=['원본파일\t결과파일\t폭(px)\t높이(px)\t해상도(ppi)\t폭(cm)\t높이(cm)\t상태'];
    function clean(s){return String(s).replace(/[\t\r\n]+/g,' ');}
    function saveCopy(doc,target,ext){
        var options;
        if(ext==='jpg'||ext==='jpeg'){
            options=new JPEGSaveOptions();options.quality=12;options.embedColorProfile=true;options.formatOptions=FormatOptions.STANDARDBASELINE;
        }else if(ext==='png'){
            options=new PNGSaveOptions();options.interlaced=false;
        }else if(ext==='tif'||ext==='tiff'){
            options=new TiffSaveOptions();options.imageCompression=TIFFEncoding.TIFFLZW;options.embedColorProfile=true;options.layers=true;
        }else{
            options=new PhotoshopSaveOptions();options.embedColorProfile=true;options.layers=true;
        }
        if(target.exists)throw Error('기존 결과 파일을 덮어쓰지 않습니다.');
        doc.saveAs(target,options,true,Extension.LOWERCASE);
        if(!target.exists)throw Error('결과 파일 저장을 확인하지 못했습니다.');
    }
    try{
        app.displayDialogs=DialogModes.NO;
        for(i=0;i<files.length;i++){
            var doc=null,check=null,temp=null,target=null;
            try{
                var original=files[i],filename=nameOf(original),ext=filename.match(/\.([^.]+)$/)[1].toLowerCase(),stem=filename.replace(/\.[^.]+$/,'');
                temp=File(temporary.fsName+'/source_'+pad(i+1)+'.'+ext);
                // 디스크 원본의 사본만 열어, 이미 열린 사용자 문서와 미저장 작업도 보존한다.
                if(!original.copy(temp.fsName))throw Error('처리용 원본 사본을 만들지 못했습니다.');
                doc=app.open(temp);
                var beforeWidth=doc.width.as('px'),beforeHeight=doc.height.as('px');
                doc.resizeImage(UnitValue(WIDTH_CM,'cm'),undefined,PPI,ResampleMethod.AUTOMATIC);
                target=File(output.fsName+'/'+stem+'_w10cm_300ppi.'+ext);
                saveCopy(doc,target,ext);
                doc.close(SaveOptions.DONOTSAVECHANGES);doc=null;
                // 저장 파일을 다시 열어 픽셀 크기·300ppi 메타데이터·비율을 확인한다.
                check=app.open(target);
                var width=check.width.as('px'),height=check.height.as('px'),resolution=check.resolution;
                var cm=width/resolution*2.54,heightCm=height/resolution*2.54;
                if(Math.abs(width-Math.round(WIDTH_CM/2.54*PPI))>1||Math.abs(resolution-PPI)>.01||Math.abs(cm-WIDTH_CM)>2.54/PPI+.0001)throw Error('저장 파일의 폭/300ppi 검사 실패');
                if(Math.abs(height-width*beforeHeight/beforeWidth)>1.1)throw Error('원본 비율 유지 검사 실패');
                rows.push(clean(filename)+'\t'+clean(target.name)+'\t'+width+'\t'+height+'\t'+resolution+'\t'+cm.toFixed(4)+'\t'+heightCm.toFixed(4)+'\tOK');
                check.close(SaveOptions.DONOTSAVECHANGES);check=null;success++;
            }catch(e){
                var msg=clean(nameOf(files[i]))+': '+clean(e);errors.push(msg);
                rows.push(clean(nameOf(files[i]))+'\t'+(target?clean(target.name):'')+'\t\t\t\t\t\tFAIL '+clean(e));
            }finally{
                if(check){try{check.close(SaveOptions.DONOTSAVECHANGES);}catch(ignore1){}}
                if(doc){try{doc.close(SaveOptions.DONOTSAVECHANGES);}catch(ignore2){}}
                if(temp&&temp.exists){try{temp.remove();}catch(ignore3){}}
            }
        }
        var report=File(output.fsName+'/결과검사.tsv');report.encoding='UTF-8';report.open('w');report.write('\uFEFF'+rows.join('\r\n'));report.close();
        var note=File(output.fsName+'/작업결과.txt');note.encoding='UTF-8';note.open('w');
        note.writeln('폭 10cm / 해상도 300픽셀/인치 / 높이 비율 유지 / 자동 리샘플링');
        note.writeln('성공 '+success+'/15, 실패 '+errors.length+'/15');
        note.writeln('원본 파일 및 기존 Photoshop 열린 문서는 변경하지 않았습니다.');
        note.writeln('출력은 입력과 같은 확장자. JPEG는 품질12로 별도 저장.');
        if(errors.length)note.writeln('\n실패 목록:\n'+errors.join('\n'));note.close();
    }finally{
        app.displayDialogs=previousDialogs;
        if(previousDocument){try{app.activeDocument=previousDocument;}catch(ignore4){}}
        try{temporary.remove();}catch(ignore5){}
    }
    alert('15장 중 '+success+'장 처리·검사 완료\n실패 '+errors.length+'장\n\n저장 위치:\n'+output.fsName+'\n\n원본은 보존했습니다. 결과검사.tsv에서 각 파일의 크기와 해상도를 확인할 수 있습니다.');
}());
