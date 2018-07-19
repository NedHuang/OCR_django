var page = 0;
var total_page =0;
var username = '';
var filename = '';
var multipage_extension = new Array('gif','pdf','tif','tiff');
var singlepage_extension = new Array('bmp','jpeg','jpg','png');



// 上传图像
function uploadDoc() {
  console.log('uploading...');
  var form = document.getElementById('upload');
  formData = new FormData(form);
//显示表示等待状态的浮层
  loading();
  $.ajax({
    url:'../php/upload_file.php',
    type:'post',
    data:formData,
    processData:false,
    contentType:false,
    xhr: function(){
      var xhr = new window.XMLHttpRequest();
      xhr.upload.addEventListener('progress', function(e){
        $('#upload-progress').show();
        if(e.lengthComputable){
          console.log('bytes loaded: ' + e.loaded);
          console.log('total size: ' + e.total);
          console.log('percentage uploaded: ' + (e.loaded /e.total)* 100 + '%');
          var percent = Math.round((e.loaded/e.total) *100);
          // 显示上传进度
          $('#progressbar').attr('aria-valuenow',percent).css('width', percent + '%').text(percent + '%');
        }
      });
      return xhr;
    },
   success:function(res){
      $('#upload-progress').hide();
      //alert(res);
      console.log(res);
      var obj = res;
      obj = JSON.parse(res);
      // var output = obj['output'];
      var current_filename = obj['filename'];
      var current_username = obj['username'];
      var current_user_guid = obj['user_guid'];
      var current_page = obj['page'];
      var total_page = obj['total_page'];
      var file_extension = obj['extension'];
      var file_directory = obj['file_directory'];
      var page_directory = obj['page_directory'];
      var img_url = obj['img_url'];
      var cmd1 = obj['cmd1'];
      //var completed_page_array = obj['completed_page_array'];
      var imginfo = obj['imginfo'];
      var errorcode = obj['errorcode'];

      // alert(obj['return_val']);
      localStorage.removeItem('filename');
      localStorage.removeItem('username');
      localStorage.removeItem('user_guid');
      localStorage.removeItem('page');
      localStorage.removeItem('total_page');
      localStorage.removeItem('extension');
      localStorage.removeItem('file_directory');
      localStorage.removeItem('page_directory');
      // localStorage.removeItem('completed_page_array');
      localStorage.removeItem('img_url');
      localStorage.removeItem('imginfo');

      localStorage.setItem('filename', current_filename);
      localStorage.setItem('username', current_username);
      localStorage.setItem('user_guid', current_user_guid);
      localStorage.setItem('page', current_page);
      localStorage.setItem('total_page', total_page);
      localStorage.setItem('extension:', file_extension);
      localStorage.setItem('file_directory', file_directory);
      localStorage.setItem('page_directory', page_directory);
      // localStorage.setItem('completed_page_array', completed_page_array);
      localStorage.setItem('img_url',img_url);
      localStorage.setItem('imginfo',imginfo);
      localStorage.setItem('original_width',parseInt(imginfo['0']));

      console.log('filename: ' + obj['filename']);
      console.log('username: ' + obj['username']);
      console.log('user_guid: ' + obj['user_guid']);
      console.log('page: ' + obj['page']);
      console.log('total_page: ' + parseInt(total_page));
      console.log('total_page',localStorage.getItem('total_page'));
      console.log('extension: ' + obj['extension']);
      console.log('file_directory: ' + obj['file_directory']);
      console.log('page_directory: ' + obj['page_directory']);
      console.log('errorcode: ' + obj['errorcode']);
      console.log('cmd1: ' + obj['cmd1']);
      console.log('return_val: ' + obj['return_val']);
      console.log('img_url: ',img_url);
      //console.log('completed_page_array: ' + obj['completed_page_array']);
      console.log('imginfo: ' + JSON.stringify(obj['imginfo']));
      // alert('finish');
      //resize(parseInt(imginfo['0']),parseInt(imginfo['1']));
      showImg(img_url);
      reset_canvas();
      resize_canvas_img(parseInt(imginfo['0']),parseInt(imginfo['1']));
      //隐藏表等待状态的浮层
      un_loading();
      get_data();
      draw_all();
      $('#total_page').html('总页数:' +total_page); 
      


    },
    error:function(err){
      alert('网络连接失败,稍后重试',err);
      //隐藏表等待状态的浮层
      un_loading();
    }
  })
 }



 //set width to 1000 for img and canvas
 function resize_canvas_img(w,h){
  console.log('w2: ' +w2);
    var w1 = w;
    var h1 = h;
    var w2 = parseInt($('#editor-container').width());
    var h2 = w2/w1*h1;
    $('#input_img').css('width',w2+'px').css('height',h2+'px');
    var c = document.getElementById('editor_canvas');
    c.setAttribute('width',w2+'');
    c.setAttribute('height',h2+'');

    localStorage.setItem('canvas_width',w2);
    localStorage.getItem('original_width',w1);

    console.log('resize to ' + w2 + 'px by ' + h2 +'px');

 }


function logout(){
  // alert('点击确定，在3秒后登出');
  setTimeout('loggedout()',3000);
  ;
}
function loggedout(){
  window.location.href='../php/logout.php';
}

function register(){
  window.location.href='../php/register.php';
}

function change(){
  window.location.href='../php/change.html';
}
function convert(){
  window.location.href='../php/convert.html';
}
