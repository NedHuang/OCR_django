// 一些通用的方法


//注销
function logout(){
 	window.location.href = '/user/logout/';
}
upload
var current_file_guid = '';
var current_filename='';
function edit(e){
  var file_management_main_container = $('#file_management_main_container');   
  var edit_menu = $('#edit_menu');
  var left_edge = 0;
  var top_edge = 0;
  if(file_management_main_container.width() - e.clientX > edit_menu.width()){
    left_edge = e.clientX +'px'; 
  }else{
    left_edge = e.clientX - edit_menu.width() +'px';
  }
  // pop below where you clicked
  if(file_management_main_container.height - e.clientY > edit_menu.height()){
    top_edge = e.clientY + 'px';
  }
  else{
    top_edge = e.clientY + 'px';
  }
  $('#edit_menu').show().css({'left':left_edge,'top':top_edge,'position':'absolute'});
  event.returnValue = false;
}

function select_file(element){
  current_file_guid = element.id;
  console.log(current_file_guid);
}


function reset(){
  console.log('reset');
  $('.menus').hide();
  // current_file_guid = '';
  // current_filename = '';
}

function delete_file(){
  var post_data = {
    'action':'delete_file',
    'file_guid': current_file_guid,
  }
  console.log(post_data);
  $.ajax({
    url:'/user/delete_file/'+current_file_guid,
    type:'POST',
    data:post_data,
    // processData: false,  // tell jquery not to process the data
    // contentType: false, // tell jquery not to set contentType
    success:function(res){
      if(res['message'] !='success'){
        alert(res['message']);
      }
      location.reload();
    },
    error:function(err){
       alert('网络连接失败,稍后重试',err);
    }
  })
}
function share(){
  var share_to_input = $('#share_to_user_id').val();
  // alert(current_file_guid)
  var post_data = {
    'co_editors' : share_to_input,
    'file_guid': current_file_guid,
  };
  console.log(post_data);

  $.ajax({
    url:'/user/share_file/',
    type:'POST',
    data:post_data,
    success:function(res){
      console.log(res);
      if(res['correct_co_editors'].length !=0){
        alert('分享给下列用户: '+ res['correct_co_editors']);
      }
      if(res['wrong_input'].length != 0){
        alert('未找到下列用户: '+res['wrong_input']);
      }
      if(res['already_shared'].length != 0){
        alert('重复分享: '+res['already_shared']);
      }
      if(res['error'] != ''){
        alert(res['error']);
      }
    },
    error:function(err){
      alert('网络连接失败,稍后重试',err);
    }
  })
}

function show_shared_file_with_me(){
  var post_data = {
    'action': 'show_shared_file_with_me()'
  }
  console.log('show_shared_file_with_me')
  $.ajax({
    url: '/user/show_shared_file_with_me/',
    type:'POST',
    data:post_data,
    success:function(res){
      alert(res['correct_co_editors']);
    },
    error:function(err){
      alert(err);
    }
  })
}

function edit_file(){
  console.log('edit');
  alert(current_file_guid)
  var post_data = {
    'file_guid': current_file_guid,
    'action':'edit_file'
  };
  // console.log(post_data);
  $.ajax({
    url:'/user/edit_file/',
    type:'POST',
    data:post_data,
    success:function(res){
      var u = '/user/load_file/?file_guid='+res['file_guid']
      console.log(u)
      window.location.href = u;
    },
    error:function(err){
      // alert('网络连接失败,稍后重试',err);
    }
  })

}

function FileUpload() {
  var file = $('#file_upload')[0].files[0]
  var form_data = new FormData()
  form_data.append('file', file)
    $.ajax({
        url:'/user/upload/',
        type:'POST',
        data: form_data,
        processData: false,  // tell jquery not to process the data
        contentType: false, // tell jquery not to set contentType
        success: function(res) {
            // alert(res['message']);
            console.log('ojbk');
            window.location.href = '/user/show_my_file/';
            
        },
        error: function(err){
          alert(err['message']);
        }
    });
  }

// share_file_to_group. 
function share_file_to_group() {
  var share_to = $('#share_groupID').val();
  var post_data = {
    'action' : 'share_file_to_group',
    'file_guid' : current_file_guid,
    'groupID' : share_to,
  };
  console.log(post_data);
  $.ajax({
    url: '/user/share_file_to_group/',
    type: 'POST',
    data: post_data,
    success: function (res) {
      console.log('ojbk');
      var msg = '';
      if (res['correct_group']!= null) {
        msg += '已分享到群组：' + res['correct_group'] + '\n';
      }
      if (res['duplicate']!= null) {
        msg += '重复分享给：' + res['duplicate'] + '\n';
      }
      if (res['wrong_input'] != null) {
        msg += '没有找到群组：' + res['wrong_input'] + ',请检查输入字段是否有误\n';
      }
      if (res['not_owner'] != null) {
        msg += '你不是下列群组的组长: ' + res['not_owner'] +'\n无法分享';
      }
      alert(msg)
    },
    error: function (err) {
      alert('网络连接失败,请稍后重试', err);
    }
  })
}


$("#edit_menu").mouseleave(function(){
    $(this).hide();
});