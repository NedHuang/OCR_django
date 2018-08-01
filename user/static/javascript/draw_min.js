/*****************************************************************************
created by Mingzhe Huang @ Founder IT Group, 06/2018

declare variables
1.  returned, added, deleted分别是 含有 服务器传回来的识别框，用户添加的识别框，服务器传回但是被删掉的识别框（false positive的例子) 的数组
2.  _backups后缀意为备份，想用户提供一键清除所有改动服务
3.  每一个识别框长以json形式存储，包含 category 和 vertexes属性，前者可以为table,formula, image, 后者为一个包含四个点坐标(x,y)[左,上，右,下]
4.  box_category 是全局变量，修改此变量以改变生成的识别框的种类
5.  action_array:记录用户的操作的数组，每一项是一个json, 下称为action, index 为此array的某元素的位置。未有操作时， index初始化为-1；
6.  action为json格式，包含act和obj 两个属性，act为string,记录其操作类型， obj为操作对象(识别框),例如
    action = {'act': 'add_new_box', 'obj':{'category': 'table','coordinates':[左,上,右,下]}}
7.  point_pair 含有两个点的坐标，记录鼠标按下与松开的位置（对角线的两个顶点生成矩形）
8.  对于任何操作，抛弃当前index以及之后的action, 把本操作加入action_array(undo 和 redo的规则)
9.  涉及到 delete的操作，清空canvas，调用 draw_all() 根据已经更新的数组重新绘制
******************************************************************************/

/******************************************************************************
set some dummy variables
******************************************************************************/


// var returned_backups = [{'category': 'image','coordinates':[10,10,100,100]}, {'category': 'table','coordinates':[50,50,140,140]}];
// var returned = [{'category': 'image','coordinates':[10,10,100,100]}, {'category': 'table','coordinates':[50,50,140,140]}];

/******************************************************************************
declare variables
声明变量
******************************************************************************/

r canvas = document.getElementById('editor_canvas');
var context = canvas.getContext('2d');
var returned_backups = [];
var added_backups = [];
var deleted_backups = [];
var returned = [];
var added = [];
var deleted = [];

var action_array = [];
var box_category = 'table';
var index = - 1;
var point_pair = [];
var page;
var total_page;






/*********************************************************
functions
各种方法
**********************************************************/

//显示图片
function showImg(url){
  console.log('show img: '+ url );
  $('#input_img').attr('src',url);
}

//将保存在 localstorage 中的识别结果保存进 变量
function load_boxes(){
  returned = localStorage.getItem('returned_boxes');
  added = localStorage.getItem('added_boxes');
  deleted = localStorage.getItem('deleted_boxes');

  returned_backups = localStorage.getItem('returned_boxes');
  added_backups = localStorage.getItem('added_boxes');
  deleted_backups = localStorage.getItem('deleted_boxes');
}


/*********************************************************
监听事件.
**********************************************************/
// mousedown behavior while in edit mode，编辑模式下的mousedown事件
edit_mousedown = function(e) {
  //保存鼠标点击的坐标，并且画辅助线（定位十字）
  // a point is a array with two element, x-coordinate and y-coordinate,
  // add the point where user start to draw the box to point pair
  draw_auxiliary_line(e.offsetX,e.offsetY);
  var point_start = [e.offsetX,e.offsetY];
  point_pair.push(point_start);
}

edit_mouseup = function(e){
  // make add the point where user release the left button of mouse to point pair
  var point_end = [e.offsetX,e.offsetY];
  point_pair.push(point_end);
  // the four coordinates for drawing a bounding box
  var upper_left = new Array();
  var upper_right = new Array();
  var lower_left = new Array();
  var lower_right = new Array();

  var left = Math.min(point_pair[0][0],point_pair[1][0]);
  var right = Math.max(point_pair[0][0],point_pair[1][0]);
  var top = Math.min(point_pair[0][1],point_pair[1][1]);
  var bot = Math.max(point_pair[0][1],point_pair[1][1]);
  var coor = [left, top, right, bot]
  console.log(coor);

  var new_box = {'category':box_category,'coordinates':coor};
  var new_action ={'act':'add_new_box', 'obj':new_box};

  added.push(new_box);
  // check if we need to abandon the modification(the rest of the action_array)
  if(index == action_array.length - 1){
    draw(new_box);
    action_array.push(new_action);
    index = index + 1;
  }
  else{
    // replace everything in the action_array after the index by this new_action
    draw(new_box);
    action_array.splice(index + 1,action_array.length - index , new_action);
    // action_array.push(new_action);
    // no need to update index, because splice replaces the everything starts from the index
    index = index + 1;
    console.log('abandon');

  }
  point_pair = [];
  draw_all();
  // console.log('added length: ' + added.length + ', returned length: ' + returned.length + ', deleted.length: ' + deleted.length);
}

//鼠标按下显示定位十字,向上下左右各画15像素
function draw_auxiliary_line(x,y){
  console.log('draw_auxiliary_line');
  context.strokeStyle = '#000000';
  context.beginPath();
  context.moveTo(x,y);
  context.lineTo(x+15,y);
  context.stroke();
  context.moveTo(x,y);
  context.lineTo(x,y+15);
  context.stroke();
  context.moveTo(x,y);
  context.lineTo(x-15,y);
  context.stroke();
  context.moveTo(x,y);
  context.lineTo(x,y-15);
  context.stroke();
  context.closePath();
}


/*********************************************************
添加/删除 box
**********************************************************/
// this function generates an array of points and for each points, it calls delete_box()
//删除模式的事件，点击记录位置，删除box,鼠标抬起则重新绘制
erase_mousedown = function(e){
  eraser_path = [];
  x_start = e.offsetX;
  y_start = e.offsetY;
  console.log('click at: '+ x_start + ',' + y_start);
  delete_box(x_start,y_start);

}
// 哈密顿距离 大于 20像素，则点的坐标array(不用了)
erase_onmousemove = function (e) {}

erase_mouseup = function () {
  console.log('erase_mouseup');
  //delete_box(eraser_path);
  draw_all();
  canvas.onmousemove = null;
}

// call calculate_distance for each box and it returns true if the distance <= 10 pixel。
// if the box is in added array, just delete, otherwise, delete and append it into deleted array
// 遍历 returned以及added中的box, 计算x,y是否在矩形中，是则删除，并且记录操作
function delete_box(x,y){
  for(var j =0; j < added.length;j++){
    var left = added[j].coordinates[0];
    var top = added[j].coordinates[1];
    var right = added[j].coordinates[2];
    var bot = added[j].coordinates[3];
    if(calculate_diatance(x,y,left,top,right,bot)){
      var deleted_box = added[j];
      added.splice(j,1);
      var new_action = {'act':'delete_added_box', 'obj':deleted_box};
      // update the index when delete a box
      j = j - 1;
      if(index == action_array.length - 1){
        action_array.push(new_action);
        index = index + 1;
      }
      else{
        action_array.splice(index, action_array.length - index);
        action_array.push(new_action);
      }
    }
  }

  for(var j =0; j < returned.length;j++){
    var left = returned[j].coordinates[0];
    var top = returned[j].coordinates[1];
    var right = returned[j].coordinates[2];
    var bot = returned[j].coordinates[3];
    if(calculate_diatance(x,y,left,top,right,bot)){
      var deleted_box = returned[j];
      returned.splice(j,1);
      // record this false positive instance by pushing the box into 'deleted'array
      deleted.push(deleted_box);
      var new_action = {'act':'delete_returned_box', 'obj':deleted_box};
      // update the index
      j = j - 1;
      if(index == action_array.length - 1){
        action_array.push(new_action);
        index = index + 1;
      }
      else{
        action_array.splice(index, action_array.length - index);
        action_array.push(new_action);
      }
    }
  }
}

// if the sum of distance from the point to a pair of edges is smaller than the height/width + 20 pixel, return true;
// 计算。。点到到两边的坐标查一正一副，则在此范围内
function calculate_diatance(x,y,x_1,y_1,x_2,y_2){
  if ((x-x_1)*(x-x_2) <= 0  && (y-y_1)*(y-y_2) <= 0){
    console.log("delete box: " + parseInt(x_1) + ", " + parseInt(y_1) + ", " + parseInt(x_2) +', '+parseInt(y_2));
    return true;
  }
  return false;
}


/*********************************************************
画图
**********************************************************/

function draw(input_box){
  //根据 box的category属性选择不同的颜色
  var coordinates = input_box['coordinates'];
      context.strokeStyle = '#3232CD';
  if(input_box.category == 'image'){
    console.log('draw image');
    context.lineWidth = 2;
    context.strokeStyle = '#3232CD';
  }

  if(input_box.category == 'formula'){
    context.lineWidth = 2;
    context.strokeStyle = '#F5270B';
  }
  if(input_box.category == 'table'){
    context.lineWidth = 2;
    context.strokeStyle = '#32CD32';
  }
  // draw the box
  context.beginPath();
  //左，上，右，下
  context.moveTo(coordinates[0],coordinates[1]);//左上
  context.lineTo(coordinates[2],coordinates[1]); //右上
  context.stroke();
  context.moveTo(coordinates[2],coordinates[1]);//右上
  context.lineTo(coordinates[2],coordinates[3]); //右下
  context.stroke();
  context.moveTo(coordinates[2],coordinates[3]);//右下
  context.lineTo(coordinates[0],coordinates[3]);//左下
  context.stroke();
  context.moveTo(coordinates[0],coordinates[3]);//左下
  context.lineTo(coordinates[0],coordinates[1]);//左上
  context.stroke();

  //console.log('draw rectangle: ' + input_box);
  context.closePath();
}

//绘制所有的识别结果(added 和 returned中的 box对象)
function draw_all(){
  console.log('re-draw ' + added.length +'items in added and ' + returned.length + ' items in returned, in index ' + index);
  context.clearRect(0, 0, canvas.width, canvas.height);
  for (var i = 0; i < added.length; i++) {
    //console.log('added.length '+added.length);
    draw(added[i]);
  }
  for (var i = 0; i < returned.length; i++) {
    draw(returned[i]);
  }
}

// 清除画布
function reset_canvas(){
  context.clearRect(0, 0, canvas.width, canvas.height);
}
/*********************************************************
操作+实现逻辑
**********************************************************/
// enter the edit mode and change the eventlistner
//进入编辑（添加标注)模式，改变画布的事件监听
function edit_mode(){
  console.log('enter edit_mode');
  canvas = document.getElementById('editor_canvas');
  context = canvas.getContext('2d');
  canvas.removeEventListener('mousedown',erase_mousedown);
  canvas.removeEventListener('onmousemove', erase_onmousemove);
  canvas.removeEventListener('mouseup',erase_mouseup);
  canvas.addEventListener('mousedown', edit_mousedown);
  canvas.addEventListener('mouseup',edit_mouseup);
}


// change the eventlistener
//进入删除模式，改变画布的事件监听
function erase_mode(){
  var canvas = document.getElementById('editor_canvas');
  var context = canvas.getContext('2d');
  canvas.removeEventListener('mousedown', edit_mousedown);
  canvas.removeEventListener('mouseup',edit_mouseup);
  context.lineWidth = 2;
  context.strokeStyle = '#000000';
  canvas.addEventListener('mousedown',erase_mousedown);
  canvas.addEventListener('onmousemove', erase_onmousemove);
  canvas.addEventListener('mouseup',erase_mouseup);
}


// 撤销操作。根据移动action_array中的指针。并且执行相反的操作（不记录在action_array中，但是修改画布，更新 added, returned,和 deleted中的对象）
// 其实用两个stack来做就好了: 3 这边一点也不elegant
function undo(){
  //console.log('before undo, index is: ' + index +', length is: ' + action_array.length + ', added length is ' + added.length);
  if(index == -1){
    // nothing can be undone, disable the button
    alert('nothing can be undone');
  }
  else{
    var last_action = action_array[index];
    console.log(last_action.act);
    index = index - 1;
    if(last_action.act == 'add_new_box'){
      added.splice(added.length-1,1);
      console.log('2');
      draw_all();
      //console.log('undo adding box, after undo, index is: ' + index +', action length is: ' + action_array.length + ', added length is ' + added.length);
    }
    if(last_action.act == 'delete_added_box'){
      // alert('undo delete_added_box');
      added.push(last_action.obj);
      console.log('3');
      draw_all();
      //console.log('undo deleting added box, after undo, index is: ' + index +', action length is: ' + action_array.length + ', added length is ' + added.length);
    }
    if(last_action.act == 'delete_returned_box'){
      returned.push(last_action.obj);
      deleted.pop();
      console.log('4');
      // returned.push(deleted.pop());
      draw_all();
    }
  }
}

// 同上。更新指针位置，并且做新的操作。
function redo(){
  console.log('before redo index is: ' + index +', length is: ' + action_array.length + ', added length is ' + added.length);
  if(index >= action_array.length-1){
    alert('nothing can be redone');
  }else{
    index = index + 1;
    var action_to_be_revoked = action_array[index];
    if(action_to_be_revoked.act == 'add_new_box'){
      added.push(action_to_be_revoked.obj);
      console.log('5');
      draw_all();
      console.log('after redo index is: ' + index +', length is: ' + action_array.length + ', added length is ' + added.length);
    }
    if(action_to_be_revoked.act == 'delete_added_box'){
      added.pop(action_to_be_revoked.obj);
      console.log('6');
      draw_all();
    }
    if(action_to_be_revoked.act == 'delete_returned_box'){
      returned.pop();
      deleted.push(action_to_be_revoked.obj);
      // deleted.push(returned.pop());
      console.log('7');
      draw_all();
    }
  }
}

//改变添加的box的category属性，
function change_category_to_formula(){
  box_category = 'formula';
}

function change_category_to_image(){
  box_category = 'image';
}

function change_category_to_table(){
  box_category = 'table';
}

//保存修改，将参数存入 backups
//backups数组允许用户保存修改但是暂时不上传到服务器(被枪毙的功能)
function save_change(){
  console.log('save_change');
  returned_backups = new Array();
  returned_backups = returned.concat();
  added_backups = new Array();
  added_backups = added.concat();
  deleted_backups = new Array();
  deleted_backups = deleted.concat();
}

//重置所有改动, abandon all changes， 所有数组设置为backups
function reset() {
  returned = new Array();
  returned = returned_backups.concat();
  added = new Array();
  added = added_backups.concat();
  deleted = new Array();
  deleted = deleted_backups.concat();
}





//将保存后的结果传回 server
function save_change_to_server(){
  // in case of error raised by PHP 5 to enpty array
  if(returned_backups.length == 0){returned_backups.push('');}
  if(added_backups.length == 0){added_backups.push('');}
  if(deleted_backups.length == 0){deleted_backups.push('');}
  save_change();
  var obj =
  {
    'operation': 'save_change',
    'filename': localStorage.getItem('filename'),
    'username': localStorage.getItem('username'),
    'page' : localStorage.getItem('page'),
    'extension': localStorage.getItem('extension'),
    'file_directory':localStorage.getItem('file_directory'),
    'returned_boxes': returned_backups,
    'added_boxes': added_backups,
    'deleted_boxes': deleted_backups,
    'canvas_width' : localStorage.getItem('canvas_width'),
    'original_width': localStorage.getItem('original_width'),
  }
  console.log('save_change_to_server');
  console.log(JSON.stringify(obj));
  // alert("operation: " + obj['operation']);
  $.ajax(
  {
    url: '../php/convert.php',
    type:'post',
    data: obj,
    // processData:false,
    // contentType:false,

    success:function(res){
      console.log(res);
      // alert(res);
      alert('您所做的修改已保存到服务器');
    },
    error:function(err){
      alert('网络链接失败');
    }
  })
}





// 请求进行文档识别，并且传回txt文件内容，再绘制标识框
function get_data(){
  console.log('get_data');
  var obj =
  {
    'operation': 'get_data',
    'filename': localStorage.getItem('filename'),
    'username': localStorage.getItem('username'),
    'page' : localStorage.getItem('page'),
    'extension': localStorage.getItem('extension'),
    'file_directory':localStorage.getItem('file_directory'),
  };
  //显示浮层
  loading();
  $.ajax(
  {
    url: '../php/convert.php',
    type:'post',
    data: obj,
    // processData:false,
    // contentType:false,
    success:function(res){
      console.log(res);
      obj = JSON.parse(res);
      var box_array = [];
      var imginfo = obj['imginfo'];
      var cav_width = parseInt($('#editor_canvas').width());
      var ratio = parseFloat(cav_width) / parseFloat(imginfo[0]);
      var boxes = obj['returned_boxes'].split('\n');
      for(var i = 0; i < boxes.length; i++){
        var box = boxes[i].split(' ');
        if( !(box[4] == "table" || box[4] == "formula" ||box[4] == "image") ){
        }
        else{
          if(box[5] != 'deleted'){
            // console.log(box);
            var box_str = '{ "category" : ' +'"'+ box[4]+'"' +', "coordinates" : [' + parseFloat(box[0])*ratio +', '
            +parseFloat(box[1])*ratio +', '+ parseFloat(box[2])*ratio +', ' +parseFloat(box[3])*ratio +']}';
            // console.log('yes '+box_str);
            var b = JSON.parse(box_str);
            console.log(b);
            box_array.push(b);
          }
        }
      }
      returned_backups = new Array().concat(box_array);
      added_backups = new Array();
      deleted_backups = new Array();
      returned = returned_backups.concat();
      added = added_backups.concat();
      deleted = deleted_backups.concat();
      draw_all();
      //隐藏浮层
      un_loading();
    },
    error:function(err){
      //隐藏浮层
      un_loading();
      alert('网络链接失败');
    }
  })
}


//请求服务器将PDF转换成png,然后执行get_data()

function get_image(){
  console.log('get_image');
  loading();
  var obj =
  {
    'operation': 'get_image',
    'filename': localStorage.getItem('filename'),
    'username': localStorage.getItem('username'),
    'page' : localStorage.getItem('page'),
    'extension': localStorage.getItem('extension'),
    'file_directory':localStorage.getItem('file_directory'),
  };

  $.ajax(
  {
    url: '../php/convert.php',
    type:'post',
    data: obj,
    // processData:false,
    // contentType:false,
    success:function(res){
      console.log(res);
      obj = JSON.parse(res);
      var page_directory = obj['page_directory'];
      var img_url = obj['img_url'];
      var completed_page_array = obj['completed_page_array'];
      var imginfo = obj['imginfo'];
      var errorcode = obj['errorcode'];
      showImg(img_url);
      reset_canvas();
      resize_canvas_img(parseInt(imginfo['0']),parseInt(imginfo['1']));
      un_loading();
      get_data();
      
      console.log('set height to ')
    },
    error:function(err){
      un_loading();
     
      alert('网络链接失败');
    }
  })
}


//翻页操作。发起get_img() get_data()请求
// 切换到下一页
function showNextPage(){
  page = parseInt(localStorage.getItem('page'));
  console.log('page: ' +page);
  total_page = parseInt(localStorage.getItem('total_page'));
  console.log( + page + "out of" + total_page);
  if(page < total_page){
    page = parseInt(page) + 1;
    localStorage.setItem('page',page);
    document.getElementById('myNumber').value = page;
    console.log('showNextPage ' + page + "out of" + total_page);
    get_image();
  }else{
    alert("已到达最后一页");
  }
}

//切换到前一页
function showPrevPage(){
  page = parseInt(localStorage.getItem('page'));
  total_page = parseInt(localStorage.getItem('total_page'));
  console.log( + page + "out of" + total_page);
  if(page > 1){
    page = parseInt(page) - 1;
    localStorage.setItem('page',page);
    console.log('showPrevPage ' + page + "out of" + total_page);
    document.getElementById('myNumber').value = page;
    get_image();
  }else{
    alert("已到达一页");
  }
}


//切换到第一页
function showFirstPage(){
  page = parseInt(localStorage.getItem('page'));
  total_page = parseInt(localStorage.getItem('total_page'));
  console.log( + page + "out of" + total_page);
  page = 1;
  localStorage.setItem('page',page);
  document.getElementById('myNumber').value = page;
  get_image();
}

//切换到最后一页
function showLastPage(){
  page = parseInt(localStorage.getItem('page'));
  total_page = parseInt(localStorage.getItem('total_page'));
  console.log( + page + "out of" + total_page);
  page = total_page;
  localStorage.setItem('page',page);
  document.getElementById('myNumber').value = page;
  get_image();
}

//选择页码
function select_page() {
  var selected_page = document.getElementById("myNumber").value;
  total_page = localStorage.getItem('total_page');
  console.log('selected_page: '  + selected_page);
  total_page = parseInt(localStorage.getItem('total_page'));
  page = selected_page;
  localStorage.setItem('page',page);
  if(selected_page <=0 || selected_page > total_page){
    alert("请输入有效的页码");
  }
  page = Number(selected_page);
  get_image();
  console.log("jump to page: " + page);
  document.getElementById('myNumber').value = page;
}


//显示等待浮层，阻止用户误操作
function loading(){
  $('#loading').css('width','100%').css('height','100%');
  $('#loading_flag').hide()
  console.log('loading...' + $('#loading').width() + ' ' +$('#loading').height());
}
// 得到data后隐藏浮层 （其实用哪个hide(), show())就行。。嘛，，懒得换了

function un_loading(){
  $('#loading').css('width','0%').css('height','0%');
  $('#loading_flag').show()
  console.log('un_loading...' + $('#loading').width() + ' ' +$('#loading').height());
}








/*********************************************************
测试用 function
**********************************************************/

// print all retuened box to console
function print_returned(){
  console.log('returned_box:');
  for(var i =0; i< returned.length; i++){
    print_box(returned[i]);
  }
}

// print all added box to console
function print_added(){
  console.log('added_box:');
  for(var i=0;i<added.length; i++){
    print_box(added[i]);
  }
}

// print all deleted object to console
function print_deleted(){
  console.log('deleted_box:' + deleted.length);
  for(var i =0; i< deleted.length; i++){
    print_box(deleted[i]);
  }
}

function print_box(box){
  console.log('category: '+box.category+'; coordinates: '+parseInt(box.coordinates[0])+', '+parseInt(box.coordinates[1])+', '+parseInt(box.coordinates[2])+', '+parseInt(box.coordinates[3]));
}
va
