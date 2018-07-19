var pdf;

var filename = localStorage.getItem('filename');
var username = localStorage.getItem('username');
var user_guid = localStorage.getItem('user_guid');
var page = localStorage.getItem('page');
var extenstion = localStorage.getItem('extension');
var file_directory = localStorage.getItem('file_directory');
var page_directory = localStorage.getItem('page_directory');
var completed_page_array = localStorage.getItem('completed_page_array');
var img_url = localStorage.getItem('img_url');
var imginfo= localStorage.getItem('imginfo');


var returned_boxes  = []
var added_boxes     = []
var deleted_boxes   = []

// var multipage_extension = new Array('gif','pdf','tif','tiff','pdf');
// var singlepage_extension = new Array('bmp','jpeg','jpg','png');


function get_info(){
  filename = localStorage.getItem('filename');
  username = localStorage.getItem('username');
  user_guid = localStorage.getItem('user_guid');
  page = localStorage.getItem('page');
  extenstion = localStorage.getItem('extension');
  file_directory = localStorage.getItem('file_directory');
  page_directory = localStorage.getItem('page_directory');
  completed_page_array = localStorage.getItem('completed_page_array');
  img_url = localStorage.getItem('img_url');
  imginfo= localStorage.getItem('imginfo');
}
function initialize(){
  showObjec(input_file_path,extension);
}


function showObject(path,extension){
  if(extension == 'pdf'){
    console.log('初始化...文件类型：pdf');
    $('#input_pdf_canvas').show();
    $('#input_img').hide();
    enable_page_menu();
    showPdf(input_file_path,page);
    recognition_request();
    load_boxes();
    draw_all();
    return;
  }
  if($.inArray(extension,singlepage_extension) != -1){
    console.log('初始化...文件类型：' + extension);
    $('#input_img').show();
    $('#input_pdf_canvas').hide();
    disable_page_menu();
    showImg(input_file_path);
    recognition_request();
    return;
  }
}




// 根据URL，页码，绘制pdf
function showPdf(url, page){
  console.log('show page '+page+' of file '+url+' on input_pdf_canvas.');
  PDFJS.workerurl = '../javascript/pdf.worker.js';//加载核心库
  // alert('showpdf: ' + url)
  PDFJS.getDocument(url).then(
    function getPdf(pdf){
    // 获取第一页数据
    total_page = pdf.numPages;
    //// alert(total_page);
    pdf.getPage(page).then(function getPage(page){
      var scale = 1 ;
      var viewport = page.getViewport(scale);

      // Prepare canvas using PDF page dimensions
      var canvas = document.getElementById('input_pdf_canvas');
      var context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      // Render PDF page into canvas context
      var renderContext = {
      canvasContext: context,
      viewport: viewport
      };
      page.render(renderContext);
    });
  });
  updatePageNumber();
}


// 如果上传的是图片的话，显示图片
function showImg(url,w,h){
  console.log('show img: '+ url + ' w: ' + w + ' h: '+h);
  $('#input_img').attr('src',url);
  // .css('max-width','1000px').css('margin','auto').css('width',);
  // 显示图片则disable掉 跳转页码的按钮

  // var w = $('#input_img')[0].naturalWidth;
  // var h = $('#input_img')[0].naturalHeight;
  // console.log('show img: '+ url + 'naturalWidth: ' + w +', naturalHeight: ' + h);
}

//修改显示的页码
function updatePageNumber(){
  $('#pages_indicator').empty();
  $('#pages_indicator').html('页数: ' + page + ' / ' + total_page);
  document.getElementById('myNumber').value = page;
  document.getElementById('myNumber').max = total_page+'';
}

// 改变页码，刷新页面，步骤1.检查页面是否合规，2.显示pdf,3.请求识别结果，4.刷新js中的box array, 5. 画出box, 6.更新页码
function select_page() {
  var selected_page = document.getElementById('myNumber').value;
  if(selected_page <=0 || selected_page > total_page){
    alert('请输入有效的页码');
  }
  page = Number(selected_page);
  showPdf(input_file_path,page);
  recognition_request();
  load_boxes();
  draw_all();
  updatePageNumber();
  console.log('jump to page: ' + page);
}


function showNextPage(){
  console.log('showNextPage');
  if(page < total_page){
    page = page +1;
    showPdf(input_file_path,page);
    recognition_request();
    load_boxes();
    draw_all();
    updatePageNumber();
  }else{
    alert('已到达最后一页');
    return;
  }
}

function showPrevPage(){
  console.log('showPrevPage');
  if(page >1){
    page = page -1;
    showPdf(input_file_path,page);
    recognition_request();
    load_boxes();
    draw_all();
    updatePageNumber();
  }else{
    alert('已到达第一页');
    return;
  }
}

function showFirstPage(){
  console.log('showFirstPage');
  page = 1;
  showPdf(input_file_path,page);
  recognition_request();
  load_boxes();
  draw_all();
  updatePageNumber();
}

function showLastPage(){
  console.log('showLastPage');
  page = total_page;
  showPdf(input_file_path,page);
  recognition_request();
  load_boxes();
  draw_all();
  updatePageNumber();
}



// ajax加载部分页面，后台传回3个boxes的array
function recognition_request(){
  console.log('recognition_request');
  //添加等待浮层，防止用户误操作
  $('#loading').show().css('display','block');
  var postParam = {
  'page':page,
  'input_file_path':input_file_path,
  'file_folder':file_folder,
};
  $.ajax({
    url:'../php/xml_generate.php',
    type:'post',
    data: postParam,
    // datatype: 'json',
    success:function(res){
      // 传回 xml文件的路径  xml_path= 'user/file/page/page.xml'
      console.log('generating xml file: success');
      console.log(res);
      var obj = JSON.parse(res);
      deleted_boxes = obj['deleted_boxes'];
      returned_boxes = obj['deleted_boxes'];
      added_boxes = obj['added_boxes'];

      // 记录所有的box到 localstorage
      localStorage.setItem('deleted_boxes',deleted_boxes);
      localStorage.setItem('returned_boxes',returned_boxes);
      localStorage.setItem('added_boxes',added_boxes);
      //至此画图完成,删除等待浮层
      $('#loading').hide().css('display','none');
    },
    error:function(err){
      $('#loading').hide().css('display','none');
       alert('网络连接失败,稍后重试',err);
    }
  })
}

// 禁用翻页按钮
function disable_page_menu(){
  $(".change_page_button").disabled = true;
}
//启用翻页按钮
function enable_page_menu(){
  $(".change_page_button").disabled = false;
}


// function resize_canvas(){
//   var img = $('#input_img');
//   // img.height(600);
//   var width = document.getElementById('input_img').width;
//   var height = document.getElementById('input_img').height;
//   var canvas = document.getElementById('editor_canvas');
//   console.log('height: ' + height + ', width: '+ width);
//   canvas.height = height;
//   canvas.width = width;
// }







/********************************************************************
分割线
********************************************************************/



// function showObject(path,extension,in_N_out){
//   console.log('show object, path: ' + path +', extension: '+ extension +', in_N_out: ' + in_N_out)
//   // alert('showObject');
//   if(in_N_out == 'input' && extension == 'pdf'){
//     console.log('input type is pdf');
//     $('#input-canvas-container').show().css('display','block');
//     $('#the-input-div').hide().css('display','none');
//     showPdf(path, page, 'the-input-canvas');
//     return;
//   }
//   if(in_N_out == 'input' && ($.inArray(extension,singlepage_extension) != -1)){
//     console.log('input type is img');
//     $('#input-canvas-container').hide().css('display','none');
//     $('#the-input-div').show().css('display','block');
//     showImg(path, 'the-input-div');
//   }

//   if(in_N_out == 'output' && extension == 'pdf'){
//     console.log('output type is pdf');
//     $('#output-canvas-container').show().css('display','block');
//     $('#the-output-div').hide().css('display','none');
//     showPdf(path, page, 'the-output-canvas');
//     return;
//   }
//   if(in_N_out == 'output' && ($.inArray(extension,singlepage_extension) != -1)){
//     console.log('output type is img');
//     $('#output-canvas-container').hide().css('display','none');
//     $('#the-output-div').show().css('display','block');
//     showImg(path, 'the-output-div');
//   }
// }


// // 根据URL，页码，以及输入/输出类型
// function showPdf(url, page, canvas_id){
//   console.log('url: ' + url +', page: '+ page + ', canvas_id: ' + canvas_id);
//   PDFJS.workerurl = '../javascript/pdf.worker.js';//加载核心库
//   // alert('showpdf: ' + url)
//   PDFJS.getDocument(url).then(
//     function getPdf(pdf){

//     // 获取第一页数据
//     total_page = pdf.numPages;
//     //// alert(total_page);
//     pdf.getPage(page).then(function getPage(page){
//       var scale = 1 ;
//       var viewport = page.getViewport(scale);

//       // Prepare canvas using PDF page dimensions
//       var canvas = document.getElementById(canvas_id);
//       var context = canvas.getContext('2d');
//       canvas.height = viewport.height;
//       canvas.width = viewport.width;

//       // Render PDF page into canvas context
//       var renderContext = {
//       canvasContext: context,
//       viewport: viewport
//       };
//       page.render(renderContext);
//     });
//   });
// }

// // 根据url以及显示图片的div_id来插入图片
// function showImg(url, div_id){
//   console.log('show img: '+ url + ' in div_id: ' + div_id);
//   $('#the-output-div-img').attr('src',url).css('max-width',$('#the-input-canvas').width()).css('margin','auto');
//    // style = 'max-width : 80%; margin-left : 10%; margin-top : 10%;'
// }

// //向服务器发起请求(输入文件名,输出文件url,以及页数)，根据返回的文件调用showImg或者showPdf
// function convert_request(input,page){
//   console.log('convert_request');
//   $('#loading').show().css('display','block');
//   var postParam = {'page':page,
//   'input_full_path':input,
//   'input_file_path':localStorage.getItem('input_file_path'),
//   'input_file_name':localStorage.getItem('input_file_name'),
// };
//   $.ajax({
//     url:'../php/convert_pdf_to_img.php',
//     type:'post',
//     data: postParam,
//     // datatype: 'json',
//     success:function(res){
//       console.log('convert_request success');
//       console.log(res);
//       var obj = JSON.parse(res);
//       // 取消以下五行的注释
//       var output_full_path = obj['output_full_path'];
//       //var input_full_path = obj['input_full_path'];
//       //var input_extension = obj['input_extension'];
//       var output_extension = obj['output_extension'];
//       showObject(localStorage.getItem('input_full_path'),input_extension,'input');
//       showObject(output_full_path,output_extension,'output');
//       $('#loading').hide().css('display','none');
//       showPageNumber();
//     },
//     error:function(err){
//        alert('网络连接失败,稍后重试',err);
//     }
//   })
// }


// function showNextPage(){
//   console.log('showNextPage');
//   if(page < total_page){
//     page = page +1;
//     convert_request(localStorage.getItem('input_full_path'),page);
//   }else{
//     // alert('已到达最后一页');
//     return;
//   }
// }

// function showPrevPage(){
//   // alert('showPrevPage');
//   console.log('showPrevPage');
//   if(page >1){
//     page = page -1;
//     convert_request(localStorage.getItem('input_full_path'),page);
//   }else{
//     // alert('已到达第一页');
//   }
//   // showObject(input_full_path,page,'input');
//   // showObject(output_full_path,page,'output');
// }

// function showFirstPage(){
//   // alert('showFirstPage');
//   console.log('showFirstPage');
//   page = 1;
//   convert_request(localStorage.getItem('input_full_path'),page);
// }

// function showLastPage(){
//   // alert('showLastPage');
//   console.log('showLastPage');
//   page = total_page;
//   convert_request(localStorage.getItem('input_full_path'),page);
// }

// function initialize_input(){
//   page = 1;
//   // alert('initialize_input');
//   console.log('initialize_input, ' +'input_full_path: '+localStorage.getItem('input_full_path')+
//     'input_extension: '+localStorage.getItem('input_extension') + ' ,in_N_out: ' +'input');
//   showObject(localStorage.getItem('input_full_path'),localStorage.getItem('input_extension'),'input');
//   convert_request(localStorage.getItem('input_full_path'),1);

// }


// function showPageNumber(){
//   $('#pages_indicator').empty();
//   $('#pages_indicator').html('页数: ' + page + ' / ' + total_page);
//   document.getElementById('myNumber').value = page;
//   document.getElementById('myNumber').max = total_page+'';

// }


// function select_page() {
//   var selected_page = document.getElementById('myNumber').value;
//   if(selected_page <=0 || selected_page > total_page){
//     alert('请输入有效的页码');
//   }
//   page = Number(selected_page);
//   convert_request(localStorage.getItem('input_full_path'),selected_page);
//   console.log('jump to page: ' + page);
// }


// function getExtention(filename){
//   var extension = filename.substr((filename.lastIndexOf('.') +1));
//   return extension;
// }


// function updateFilePath(){
//   var filepath = document.getElementById('pic').value;
//   var pos=filepath.lastIndexOf('\\');
//   var name= filepath.substring(pos+1);
//   document.getElementById('showFileName').innerHTML=name;
// }
