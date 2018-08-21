// alert('aaaa')
var fileID = '';
    function select_file_button(element) {
        fileID = element.id;
        console.log('fileID set to', fileID);
    }
    function remove_share_record() {
        var post_data = {
            'action': 'remove_share_record',
            'file': fileID,
            'group_to_remove': $('input[name=to_delete_group]:checked').map(function ()
            {
                return $(this).val();
            }).get(),
            'user_to_remove': $('input[name=to_delete_user]:checked').map(function ()
            {
                return $(this).val();
            }).get(),
        };
        console.log(post_data);
        $.ajax({
            url: '/user/remove_share_record/',
            type: 'POST',
            data: post_data,
            success: function (res) {
                var msg = '';
                if (res['deleted_user'].length != 0) {
                    msg += '已取消下列用户的分享权限：' + res['deleted_user'] + '\n';
                }
                if (res['deleted_group'].length != 0) {
                    msg += '已取消下列群组的分享权限：' + res['deleted_group'] + '\n';
                }
                if (res['error'].length != 0) {
                    msg += 'wrong input ' + res['error'];
                }
                alert(msg);
                location.reload();
            },
            error: function (err) {
                alert('网络连接失败，请稍后重试', err);
            }
        })
    }