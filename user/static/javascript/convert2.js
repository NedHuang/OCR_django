var page = 1;
var url = "";
var total_page =0;
var pdf;
var filename;
var multipage_extension = new Array("gif","pdf","tif","tiff");
var singlepage_extension = new Array("bmp","jpeg","jpg","png");


function uploadDoc() {
      localStorage.removeItem("input_full_path", input_full_path);
      localStorage.removeItem("input_extension", input_extension);
      localStorage.removeItem("input_file_name", input_file_name);
      localStorage.removeItem("input_file_path", input_file_path);

  var form = document.getElementById('upload');
    formData = new FormData(form);
    // alert(formData);
  $.ajax({
    url:"../php/convert2.php",
    type:"post",
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
          $('#progressbar').attr('aria-valuenow',percent).css('width', percent + '%').text(percent + '%');
        }
      });
      
      return xhr;
    },
   success:function(res){
      $('#upload-progress').hide();
      // alert(res);
      console.log("this is returned to upload function");
      console.log(res);
      var obj = JSON.parse(res);
      // var output = obj["output"];
      var input_full_path = obj["input_full_path"];
      var input_extension =obj["input_extension"].toString().toLowerCase();
      var input_file_path = obj['input_file_path'];

      localStorage.removeItem("input_full_path", input_full_path);
      localStorage.removeItem("input_extension", input_extension);
      localStorage.removeItem("input_file_name", input_file_name);
      localStorage.removeItem("input_file_path", input_file_path);

      localStorage.setItem("input_full_path", input_full_path);
      localStorage.setItem("input_extension", input_extension);
      localStorage.setItem("input_file_name", input_file_name);
      localStorage.setItem("input_file_path", input_file_path);
      
      // var output_extension =obj["output_extension"].toString().toLowerCase();
      // showPdf(input_full_path, "pdf", 1, 'the-input-canvas');
      // showPdf(input_full_path, "pdf", 1, 'the-output-canvas');
      // alert(input_file_path);
      initialize_input();

    },
    error:function(err){
      // alert("网络连接失败,稍后重试",err);
    }
  })

 }

 /****************************************
 *显示PDF的function, input_file
 *****************************************/
// function showPdf(url, page,containerId){
//   //PDFJS.workerurl = '../javascript/pdf.worker.js';//加载核心库
//   PDFJS.getDocument(url).then(
//     function getPdfHelloWorld(pdf) {
//     //
//     // 获取第一页数据
//     //
//     total_page = pdf.numPages;
//     //// alert(total_page);
//     pdf.getPage(page).then(function getPageHelloWorld(page) {
//       var scale = 1;
//       var viewport = page.getViewport(scale);

//       //
//       // Prepare canvas using PDF page dimensions
//       //
//       var canvas = document.getElementById(containerId);
//       var context = canvas.getContext('2d');
//       canvas.height = viewport.height;
//       canvas.width = viewport.width;

//       //
//       // Render PDF page into canvas context
//       //
//       var renderContext = {
//       canvasContext: context,
//       viewport: viewport
//       };
//       page.render(renderContext);
//     });
//   });
// }

// function showNextpage(){
//   if(page < total_page){
//     page = page +1;
//   }else{
//     // alert("已到达最后一页");
//   }
//   showPdf(url, page,"the-input-canvas");
//   // showPdf(url, page,"the-output-canvas");

// }

// function showPrevpage(){
//   if(page >1){
//     page = page -1;
//   }else{
//     // alert("已到达第一页");
//   }
//   showPdf(url, page,"the-input-canvas");
//   // showPdf(url, page,"the-output-canvas");
// }

// function showFirstPage(){
//   page = 1;
//   showPdf(url, page,"the-input-canvas");
//   // showPdf(url, page,"the-output-canvas");
// }

// function showLastPage(){
//   page = total_page;
//   showPdf(url, page,"the-input-canvas");
//   // showPdf(url, page,"the-output-canvas");
// }
// function initializeInput(src){
//   url = src;
//   page = 1;
//   showPdf(url, page, "the-input-canvas");
// }

// function initializeOutput(src){
//   url = src;
//   page = 1;
//   showPdf(url, page, "the-output-canvas");
// }












function logout(){
  // alert("点击确定，在3秒后登出");
  setTimeout("loggedout()",3000);
  ;
}
function loggedout(){
  window.location.href="../php/logout.php";
}

function register(){
  window.location.href="../php/register.php";
}

function change(){
  window.location.href="../php/change.html";
}
function convert(){
  window.location.href="../php/convert.html";
}



