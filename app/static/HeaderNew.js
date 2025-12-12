//お知らせ表示処理
function executeNotice(modalID){
    $.get({
        ur1: '/Notice',
        type:'GET'
    }).done(function(response) {
        if (response.type == 'autherror') {
            window.location.href = '/logout';
        } else if (response.type == 'error') {
            openAlertDialog('お知らせ', response.msg);
        } else if (response.MaintenanceFlag == true) {
            $(modalID).find('#maintenanceLabel').show();
        } else {
            if (response.IsChecked == false) {
                $(modalID).find('#checkTimestamp').val(response.CheckTimestamp);
                $(modalID).find('#checkBtn').show();
            }
            let noticeList = response.NoticeList;
            for (let i = 0; i < noticeList.length; i++) {
                let notice = noticeList[i];
                let noticeRowHtml = noticeNewRowHtml;
                noticeRowHtml = noticeRowHtml.replace('{ from }', notice['From']);
                if (notice['Prioriority'] == 1) {
                    noticeRowHtml = noticeRowHtml.replace(' rate }', 'rate-1');
                } else if (notice['Prioriority'] == 2) {
                    noticeRowHtml = noticeRowHtml.replace(' rate }', 'rate-2');
                } else if (notice['Prioriority'] == 3) {
                    noticeRowHtml = noticeRowHtml.replace(' rate }', 'rate-3');
                } else if (notice['Prioriority'] == 4) {
                    noticeRowHtml = noticeRowHtml.replace(' rate }', 'rate-4');
                }
                noticeRowHtml = noticeRowHtml.replace('{ isPriority1 }', judgeRate(1, notice['Priority']));
                noticeRowHtml = noticeRowHtml.replace('{ isPriority2 }', judgeRate(2, notice['Priority']));
                noticeRowHtml = noticeRowHtml.replace('{ isPriority3 }', judgeRate(3, notice['Priority']));
                noticeRowHtml = noticeRowHtml.replace('{ isPriority4 }', judgeRate(4, notice['Priority']));
                let groupMessage = "";
                if ('CompanyNamenyName' in notice && 'SubGroupDisplayName' in notice) {
                    groupMessage = "[" + notice['CompanyName'] + "- " + notice['SubGroupDisplayName'] + "の皆様向け］";
                }
                noticeRowHtml = noticeRowHtml.replace('{ groupMessage }', groupMessage);
                noticeRowHtml = noticeRowHtml.replace('{ title }', notice['Title']);
                noticeRowHtml = noticeRowHtml.replace('{ content }', notice['Content'].replace(/\n/g, '<br>'));
                $(noticeRowHtml).appendTo($(modalID).find('.dialog-tab-content-list'));
            }
            app.dialog.open(modalID);
        }
        $('.l-loading').hide();
    }).fail(function(){
        let msg = 'エラーが発生しました。';
        openAlertDialog('お知らせ',msg);
        $('.l-loading').hide();
    });
}

