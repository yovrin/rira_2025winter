let app = {}


//ダイアログを開く、閉じる
app.dialog= {};

//ダイアログを開く
app.dialog.open = function (dialogId){
    // $(dialogId).closest('.l-dialog').addClass('is-visible');
    $(dialogId).addClass('is-visible'); // 修正: closest を削除
    $('body').css('overflow-y', 'hidden'); // 本文の縦スクロールを無効
    $('body' ) .addClass('hidden')
};

//ダイアログを閉じる(引数が空ならすべてのダイアログを閉じる)
app.dialog.close = function (dialogId){
    if (typeof dialogId === 'undefined'){
    $('.l-dialog').removeClass('is-visible');
    } else {
        $(dialogId).closest('.l-dialog').removeClass('is-visible');
    }
    $('body').removeClass('hidden')
    $('body').css('overflow-y', 'auto'); // 本文の縦スクロールを有効' +
};
