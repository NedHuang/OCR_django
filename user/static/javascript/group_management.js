function create_group() {
    var members = $('#group_userID').val();
    var name = $('#group_name').val();
    var post_data= {
      'action': 'create_group',
      'name': name,
      'members': members,
    };
    console.log(post_data);
    $.ajax({
      url: '/user/create_group/',
      type: 'POST',
      data: post_data,
      success: function (res) {
        if (res['error'] == 'duplicate') {
          alert('已存在同名群组，请更换名字');
        }
        if (res['correct_members'].length != 0) {
          alert('已成功创建群组' + name + '，并添加' + res['correct_members']);
        }
        if (res['wrong_input: '].length != 0) {
          alert('wrong input: ' + res['wrong_input']);
        }
        location.reload()
      },
      error: function (err) {
        alert('网络连接失败，请稍后重试', err);
      }
    })
  }