alert('aaaaaa');
var groupID = '';
  function select_group(element) {
    groupID = element.id;
    console.log('groupID set to', groupID);
  }
  function delete_member() {
    var post_data = {
      'action': 'delete_member',
      'group': groupID,
      'to_delete': $('input[name=to_delete]:checked').map(function ()
      {
        return $(this).val();
      }).get(),
    };
    console.log(post_data);
    $.ajax({
      
      url: '/user/delete_member/',
      type: 'POST',
      data: post_data,
      success: function (res) {
        if (res['correct_members'].length != 0) {
          alert('已删除' + res['correct_members']);
          location.reload();
        }
        if (res['wrong_input'].length != 0) {
          alert('wrong input ' + res['wrong_input']);
        }
      },
      error: function (err) {
        alert('网络连接失败，请稍后重试', err);
      }
    })
  }

  function add_member() {
    var members = $('#group_userID').val();
    var post_data= {
      'action': 'add_member',
      'group': groupID,
      'members': members,
    };
    console.log(post_data);
    $.ajax({
      url: '/user/add_member/',
      type: 'POST',
      data: post_data,
      success: function (res) {
        if (res['correct_members'].length != 0) {
          alert('已添加' + res['correct_members']);
          location.reload();
        }
        if (res['wrong_input'].length != 0) {
          alert('wrong input' + res['wrong_input']);
        }
      },
      error: function (err) {
        alert('网络连接失败，请稍后重试', err);
      }
    })
  }
  function delete_group() {
    var post_data= {
      'action': 'delete_group',
      'group': groupID,
    };
    console.log(post_data);
    $.ajax({
      url: '/user/delete_group/',
      type: 'POST',
      data: post_data,
      success: function (res) {
        if (res['message'] != 'success') {
          alert(res['message']);
          window.location.href = '/user/group_management/';
        }

      },
      error: function (err) {
        alert('网络连接失败，请稍后重试', err);
      }
    })
  }