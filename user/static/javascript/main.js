    //canvas: 显示标注结果的canvas
    // ani_canvas: 显示标注动画的canvas
    var canvas = document.getElementById('editor_canvas');
    var context = canvas.getContext('2d');
    var ani_canvas = document.getElementById('animation_canvas');
    var ani_context = ani_canvas.getContext('2d');
    var returned_backups = [];  // 识别结果返回的box,备份， 没有点保存的话不会更改它
    var added_backups = [];     // 手动添加的box,备份， 没有点保存的话不会更改它
    var deleted_backups = [];   // 手动删除的box,备份， 没有点保存的话不会更改它
    var returned = [];          // 识别结果返回的box
    var added = [];             // 手动添加的box
    var deleted = [];           // 手动删除的 box
    var action_array = [];      // 执行操作的 array.undo redo在此移动指针并且反向操作
    var box_category = 'table'; // 标注数据的类型
    var index = - 1;            // action_array的指针,undo往前，redo往后
    var point_pair = [];        // 标注时点击鼠标的坐标与松开鼠标的坐标
    var page;                   // 当前页码
    var total_page;             // 文档总页数
    var original_width=0;         // 当前页面（图片）的原始宽度（像素）
    var original_height=0;        // 当前页面（图片）的原始宽度（像素）
    var canvas_width = $(input_img).width(); // 显示在页面上的图片宽度
    var canvas_height = $(input_img).height(); //显示在页面上的图片的高度
    var ratio;


    function resize_editor_region(){
      var w = document.getElementById('editor-menu-container').clientWidth;
      $('#editor-container').css('width',parseInt(w)-10);
      }

      $(window).resize(function () {          //当浏览器大小变化时
       resize_editor_region();
    });
    //改变侧边栏按钮的颜色ps, as是tag的p 和 a, s表示复数。。
    // function change_button(b){
    //   var buttons = ['image_button','table_button','formula_button','erase_button'];
    //   var ps =['image_p','table_p','formula_p','erase_p'];
    //   var as =['image_a','table_a','formula_a','erase_a'];
    //   // j是 as,ps的index
    //   var j = -1;
      
    //   for(var i = 0; i < 4; i++){
    //     if(b == buttons[i]){
    //       j = i;
    //        $('#'+buttons[i]).css('background-color','#e0e0e0');
    //       $('#'+as[j]).css('background-color','#e0e0e0');    
    //       if(j==0){
    //         $('#'+ps[i]).css('color','#feae19');
    //       }
    //       if(j==1){
    //         $('#'+ps[i]).css('color','#32CD32');
    //       }
    //       if(j==2){
    //         $('#'+ps[i]).css('color','#F5270B');
    //       }          
    //       if(j==3){
    //         $('#'+ps[i]).css('color','#16A085');
    //       }
    //       console.log(b)
    //     }
    //   }
    //   for(var i = 0; i < 4; i++){
    //     if(j != i){
    //       $('#'+buttons[i]).css('background-color','');
    //       $('#'+as[i]).css('background-color','');
    //       $('#'+ps[i]).css('color','');
    //       console.log(b)
    //     }
    //   }
    // }
    
    //读取 file_uplod input中的file, 上传
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
            alert(res['message']);
            console.log('ojbk');
        },
        error: function(err){
          alert(err['message']);
        }
      });
    }
 
    //翻页，下一页
    function showNextPage(){
      var post_data = {'action':'next_page'}
      $.ajax({
        url:'/user/next_page/',
        type:'POST',
        data: post_data,
        processData: false,  // tell jquery not to process the data
        contentType: false, // tell jquery not to set contentType
        success:function(res){
          if(res['status'] =='success'){
            console.log('success, next_page')
            //把 图片的src 从 a/b/c/d/123.png 改成 a/b/c/d/122.png
            a = $('#input_img').attr('src');
            b = a.split('/');
            c = b.slice(0,-1).join('/') + '/';
            d = parseInt(b[b.length-1].split('.')[0]);
            e = b[b.length-1].split('.')[1];
            f = c + (d+1).toString()+'.'+e;
            $('#input_img').attr('src',f);
            original_width = res['image_width'];
            original_height = res['image_height'];
          }
          if(res['status'] == 'last_page'){
            alert('已到达尾页');
          }
          // window.location.reload();
          console.log(res);
          update_page_number(res['page']);
          resize_canvas_img();
          get_boxes();
        },
        error: function(err){
          alert(err);
        }
      });
    }
    //翻页，前一页
    function showPrevPage(){
      var post_data = {'action':'prev_page'}
      $.ajax({
        url:'/user/prev_page/',
        type:'POST',
        data: post_data,
        processData: false,  // tell jquery not to process the data
        contentType: false, // tell jquery not to set contentType
        success:function(res){
          if(res['status'] =='success'){
            console.log('success, prev_page');
            //把 图片的src 从 a/b/c/d/123.png 改成 a/b/c/d/124.png
            a = $('#input_img').attr('src');
            b = a.split('/');
            c = b.slice(0,-1).join('/') + '/';
            d = parseInt(b[b.length-1].split('.')[0]);
            e = b[b.length-1].split('.')[1];
            f = c + (d-1).toString()+'.'+e;
            $('#input_img').attr('src',f);
            original_width = res['image_width'];
            original_height = res['image_height'];
          }
          if(res['status'] == 'first_page'){
            alert('已到达第一页');
          }
          console.log('prevpage');
          console.log(original_width);
          console.log(res);
          update_page_number(res['page']);
          resize_canvas_img();
          get_boxes();
        },
        error: function(err){
          alert(err);
        }
      });
    }
    //翻页，第一页
    function showFirstPage(){
      var post_data = {'action':'first_page'}
      $.ajax({
        url:'/user/first_page/',
        type:'POST',
        data: post_data,
        processData: false,  // tell jquery not to process the data
        contentType: false, // tell jquery not to set contentType
        success:function(res){
          if(res['status'] =='success'){
            //把 图片的src 从 a/b/c/d/123.png 改成 a/b/c/d/124.pnga/b/c/d/1.png
            a = $('#input_img').attr('src');
            b = a.split('/');
            c = b.slice(0,-1).join('/') + '/';
            d = parseInt(b[b.length-1].split('.')[0]);
            e = b[b.length-1].split('.')[1];
            f = c + '1'+'.'+e;
            $('#input_img').attr('src',f);
            original_width = res['image_width'];
            original_height = res['image_height'];
          }
          if(res['status'] == 'first_page'){
            // alert('已到达第一页');
          }

          console.log('fitstPage');
          console.log(original_width);
          console.log(res);
          update_page_number(res['page']);
          resize_canvas_img();
          get_boxes();
        },
        error: function(err){
          alert('err');
        }
      });
    }
    // 翻页，末页
    function showLastPage(){
      var post_data = {'action':'first_page'}
      $.ajax({
        url:'/user/last_page/',
        type:'POST',
        data: post_data,
        processData: false,  // tell jquery not to process the data
        contentType: false, // tell jquery not to set contentType
        success:function(res){
          if(res['status'] =='success'){
            a = $('#input_img').attr('src');
            b = a.split('/');
            c = b.slice(0,-1).join('/') + '/';
            d = parseInt(b[b.length-1].split('.')[0]);
            e = b[b.length-1].split('.')[1];
            f = c + res['total_page'].toString()+'.'+e;
            $('#input_img').attr('src',f);
            original_width = res['image_width'];
            original_height = res['image_height'];
            console.log(total_page);
          }
          if(res['status'] == 'last_page'){
            // alert('已到达最后一页');
          }

          console.log('Lastpage');
          console.log(original_width);
          console.log(res);
          update_page_number(res['page']);
          resize_canvas_img();
          get_boxes();
        },
        error: function(err){
          alert('err');
        }
      });
    }

  function select_page() {
    var selected_page = parseInt($('#myNumber').val());
    var post_data = {'action':'select_page','selected_page':selected_page};
    console.log(post_data);
    $.ajax({
      url:'/user/select_page/',
      type:'POST',
      data:post_data,
      success:function(res){
        console.log(res);
        if(res['status'] == 'success'){
          console.log('select_page: '+ selected_page);
          a = $('#input_img').attr('src');
          b = a.split('/');
          c = b.slice(0,-1).join('/') + '/';
          d = parseInt(b[b.length-1].split('.')[0]);
          e = b[b.length-1].split('.')[1];
          f = c + res['page'].toString()+'.'+e;
          $('#input_img').attr('src',f);
          update_page_number(res['page']);
          original_width = res['image_width'];
          original_height = res['image_height'];
          console.log(c)
        }
        else{
          alert(res)
        }
        console.log('select_page: ' + res['page']);
        console.log(original_width);
        console.log(res);
        update_page_number(res['page']);
        resize_canvas_img();
        get_boxes();
      },
      error:function(err){
        alert(JSON.stringify(err))
      }
    })
  }

  function update_page_number(the_page){
    $('#myNumber').val(the_page);
    page = the_page;
  }

  //调整input_img,不可以在放大缩小的时候调用
  function resize_canvas_img(){
    var client_width = document.body.clientWidth;
    var client_height =document.body.clientHeight;
    // console.log(client_width + ' ' + client_height)
    // original_height = $(input_img).height();
    // original_width = $(input_img).width();
    console.log('aaaa');
    console.log(original_width);
    $('#input_img').attr('height', client_height-130);
    $('#editor_canvas').attr('height', $(input_img).height());
    $('#editor_canvas').attr('width', $(input_img).width());
    $('#animation_canvas').attr('height', $(input_img).height());
    $('#animation_canvas').attr('width', $(input_img).width());
    canvas_width = $(input_img).width();
    canvas_height = $(input_img).height();
    
  }
  // 自动调整图像以及画布的大小
  window.onload=resize_canvas_img();


    ////////////////////////////////////////////
    /*********************************************************
functions
各种方法
**********************************************************/

//显示图片
// function showImg(url){
//   console.log('show img: '+ url );
//   $('#input_img').attr('src',url);
// }

// //将保存在 localstorage 中的识别结果保存进 变量
// function load_boxes(){
//   returned = localStorage.getItem('returned_boxes');
//   added = localStorage.getItem('added_boxes');
//   deleted = localStorage.getItem('deleted_boxes');

//   returned_backups = localStorage.getItem('returned_boxes');
//   added_backups = localStorage.getItem('added_boxes');
//   deleted_backups = localStorage.getItem('deleted_boxes');
// }


/*********************************************************
监听事件.
**********************************************************/
// mousedown behavior while in edit mode，编辑模式下的mousedown事件
edit_mousedown = function(e) {
  //保存鼠标点击的坐标，并且画辅助线（定位十字）
  // a point is a array with two element, x-coordinate and y-coordinate,
  // add the point where user start to draw the box to point pair
  // draw_auxiliary_line(e.offsetX,e.offsetY);
  canvas.addEventListener('mousemove',edit_mousemove);
  point_start = [e.offsetX,e.offsetY];
  point_pair.push(point_start);
  console.log('point_start: '+point_start);
}

//编辑状态下mouseup动作
edit_mouseup = function(e){
  canvas.removeEventListener('mousemove',edit_mousemove);
  var point_end = [e.offsetX,e.offsetY];
  point_pair.push(point_end);
  var upper_left = new Array();
  var upper_right = new Array();
  var lower_left = new Array();
  var lower_right = new Array();

  var left = Math.min(point_pair[0][0],point_pair[1][0]);
  var right = Math.max(point_pair[0][0],point_pair[1][0]);
  var top = Math.min(point_pair[0][1],point_pair[1][1]);
  var bot = Math.max(point_pair[0][1],point_pair[1][1]);
  // coordinate是左右上下
  // var coor = [left, right, top, bot]
  canvas_width = $(input_img).width();
  // ratio = original_width / canvas_width;
  ratio = getratio();
  var coor = [left*ratio, right*ratio, top*ratio, bot*ratio];
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
  //  =========draw_all();
  // console.log('added length: ' + added.length + ', returned length: ' + returned.length + ', deleted.length: ' + deleted.length);
  clear_animation();
  console.log(added);
  // console.log(action_array);
}

function edit_mousemove(e){
  var x = e.offsetX, y =e.offsetY;
  console.log('point_move: '+x +', ' + y);
  animation(point_start[0],point_start[1],x,y)
}
function animation(x1,y1,x2,y2){
  ani_context.clearRect(0, 0, ani_canvas.width, ani_canvas.height);
  ani_context.fillStyle = 'rgba(100,149,237,0.5)';
  var left = Math.min(x1,x2);
  var right = Math.max(x1,x2);
  var top = Math.min(y1,y2);
  var bottom = Math.max(y1,y2);
  ani_context.fillRect(left,top,right-left,bottom-top);
}
function clear_animation(){
  ani_canvas = document.getElementById('animation_canvas');
  ani_context = ani_canvas.getContext('2d');
  ani_context.clearRect(0, 0, ani_canvas.width, ani_canvas.height);
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


// /*********************************************************
// 添加/删除 box
// **********************************************************/
// this function generates an array of points and for each points, it calls delete_box()
//删除模式的事件，点击记录位置，删除box,鼠标抬起则重新绘制
erase_mousedown = function(e){
  eraser_path = [];
  x_start = e.offsetX;
  y_start = e.offsetY;
  console.log('click at: '+ x_start + ',' + y_start);
  delete_box(x_start*ratio,y_start*ratio);


}
// 哈密顿距离 大于 20像素，则点的坐标array(不用了)
erase_onmousemove = function (e) {
  context.clearRect(0, 0, canvas.width, canvas.height);
}

erase_mouseup = function () {
  console.log('erase_mouseup');
  //delete_box(eraser_path);
  draw_all();
  canvas.onmousemove = null;
}



// // call calculate_distance for each box and it returns true if the distance <= 10 pixel。
// // if the box is in added array, just delete, otherwise, delete and append it into deleted array
// // 遍历 returned以及added中的box, 计算x,y是否在矩形中，是则删除，并且记录操作
function delete_box(x,y){
  console.log()
  for(var j =0; j < added.length;j++){
    var left = added[j].coordinates[0];
    var right = added[j].coordinates[1];
    var top = added[j].coordinates[2];
    var bot = added[j].coordinates[3];
    if(calculate_diatance(x,y,left,top,right,bot)){
      var deleted_box = added[j];
      console.log('deletedbox: ');
      console.log(deleted_box);
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
    var right = returned[j].coordinates[1];
    var top = returned[j].coordinates[2];
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


// /*********************************************************
// 画图
// **********************************************************/

function draw(input_box){
  //根据 box的category属性选择不同的颜色
  var coordinates = input_box['coordinates'];
      context.strokeStyle = '#feae19';
  if(input_box.category == 'figure'){
    console.log('draw image');
    console.log(coordinates);
    context.lineWidth = 2;
    context.strokeStyle = '#feae19';
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
  //左，右，上，下
  context.moveTo(coordinates[0]/ratio,coordinates[2]/ratio);//左上
  context.lineTo(coordinates[1]/ratio,coordinates[2]/ratio); //右上
  context.stroke();
  context.moveTo(coordinates[1]/ratio,coordinates[2]/ratio);//右上
  context.lineTo(coordinates[1]/ratio,coordinates[3]/ratio); //右下
  context.stroke();
  context.moveTo(coordinates[1]/ratio,coordinates[3]/ratio);//右下
  context.lineTo(coordinates[0]/ratio,coordinates[3]/ratio);//左下
  context.stroke();
  console.log(ratio)
  context.moveTo(coordinates[0]/ratio,coordinates[3]/ratio);//左下
  context.lineTo(coordinates[0]/ratio,coordinates[2]/ratio);//左上
  context.stroke();
  context.closePath();

}

//绘制所有的识别结果(added 和 returned中的 box对象)
function draw_all(){
  clear_all_canvas();
  console.log('draw_all')
  for (var i = 0; i < added.length; i++) {
    //console.log('added.length '+added.length);
    draw(added[i]);
  }
  for (var i = 0; i < returned.length; i++) {
    draw(returned[i]);
  }
}

// // 清除画布
// function reset_canvas(){
//   context.clearRect(0, 0, canvas.width, canvas.height);
// }
// /*********************************************************
// 操作+实现逻辑
// **********************************************************/
// // enter the edit mode and change the eventlistner
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
  
//   $('#editor_c').mousemove(function(e){
//   if(paint){//是不是按下了鼠标
//     addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
//     redraw();
//   }
// });
}


// // change the eventlistener
// //进入删除模式，改变画布的事件监听
function erase_mode(){
  var canvas = document.getElementById('editor_canvas');
  var context = canvas.getContext('2d');
  canvas.removeEventListener('mousedown', edit_mousedown);
  canvas.removeEventListener('mouseup',edit_mouseup);
  // canvas.addEventListener('onmousemove', edit_mousemove);
  context.lineWidth = 2;
  context.strokeStyle = '#000000';
  canvas.addEventListener('mousedown',erase_mousedown);
  canvas.addEventListener('onmousemove', erase_onmousemove);
  canvas.addEventListener('mouseup',erase_mouseup);
}


// // 撤销操作。根据移动action_array中的指针。并且执行相反的操作（不记录在action_array中，但是修改画布，更新 added, returned,和 deleted中的对象）
// // 其实用两个stack来做就好了: 3 这边一点也不elegant
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
    show_info();
  }
}

function show_info(){
  console.log('added: ' + JSON.stringify())
}

//改变添加的box的category属性，
function change_category_to_formula(){
  box_category = 'formula';
}

function change_category_to_image(){
  box_category = 'figure';
}

function change_category_to_table(){
  box_category = 'table';
}



// //保存修改，将参数存入 backups
// //backups数组允许用户保存修改但是暂时不上传到服务器(被枪毙的功能)
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
  // if(returned_backups.length == 0){returned_backups.push('');}
  // if(added_backups.length == 0){added_backups.push('');}
  // if(deleted_backups.length == 0){deleted_backups.push('');}
  save_change();
  var obj =
  {
    'canvas_height':canvas_height,
    'canvas_width':canvas_width,
    'original_height':original_height,
    'original_width':original_width,
    'added_backups':JSON.stringify(added_backups),
    'returned_backups':JSON.stringify(returned_backups),
    'deleted_backups':JSON.stringify(deleted_backups),
  }
  console.log('save_change_to_server');
  console.log(JSON.stringify(obj));
  $.ajax(
  {
    url: '/user/save_change_to_server/',
    type:'post',
    data: obj,
    // processData:false,
    // contentType:false,

    success:function(res){
      console.log(res);
    
      alert('您所做的修改已保存到服务器');
    },
    error:function(err){
      alert('网络链接失败');
    }
  })
}





// // 请求进行文档识别，并且传回txt文件内容，再绘制标识框
// function get_data(){
//   console.log('get_data');
//   var obj =
//   {
//     'operation': 'get_data',
//     'filename': localStorage.getItem('filename'),
//     'username': localStorage.getItem('username'),
//     'page' : localStorage.getItem('page'),
//     'extension': localStorage.getItem('extension'),
//     'file_directory':localStorage.getItem('file_directory'),
//   };
//   //显示浮层
//   loading();
//   $.ajax(
//   {
//     url: '../php/convert.php',
//     type:'post',
//     data: obj,
//     // processData:false,
//     // contentType:false,
//     success:function(res){
//       console.log(res);
//       obj = JSON.parse(res);
//       var box_array = [];
//       var imginfo = obj['imginfo'];
//       var cav_width = parseInt($('#editor_canvas').width());
//       var ratio = parseFloat(cav_width) / parseFloat(imginfo[0]);
//       var boxes = obj['returned_boxes'].split('\n');
//       for(var i = 0; i < boxes.length; i++){
//         var box = boxes[i].split(' ');
//         if( !(box[4] == "table" || box[4] == "formula" ||box[4] == "image") ){
//         }
//         else{
//           if(box[5] != 'deleted'){
//             // console.log(box);
//             var box_str = '{ "category" : ' +'"'+ box[4]+'"' +', "coordinates" : [' + parseFloat(box[0])*ratio +', '
//             +parseFloat(box[1])*ratio +', '+ parseFloat(box[2])*ratio +', ' +parseFloat(box[3])*ratio +']}';
//             // console.log('yes '+box_str);
//             var b = JSON.parse(box_str);
//             console.log(b);
//             box_array.push(b);
//           }
//         }
//       }
//       returned_backups = new Array().concat(box_array);
//       added_backups = new Array();
//       deleted_backups = new Array();
//       returned = returned_backups.concat();
//       added = added_backups.concat();
//       deleted = deleted_backups.concat();
//       draw_all();
//       //隐藏浮层
//       un_loading();
//     },
//     error:function(err){
//       //隐藏浮层
//       un_loading();
//       alert('网络链接失败');
//     }
//   })
// }







// //显示等待浮层，阻止用户误操作
// function loading(){
//   $('#loading').css('width','100%').css('height','100%');
//   $('#loading_flag').hide()
//   console.log('loading...' + $('#loading').width() + ' ' +$('#loading').height());
// }
// // 得到data后隐藏浮层 （其实用哪个hide(), show())就行。。嘛，，懒得换了

// function un_loading(){
//   $('#loading').css('width','0%').css('height','0%');
//   $('#loading_flag').show()
//   console.log('un_loading...' + $('#loading').width() + ' ' +$('#loading').height());
// }








// /*********************************************************
// 测试用 function
// **********************************************************/

// // print all retuened box to console
// function print_returned(){
//   console.log('returned_box:');
//   for(var i =0; i< returned.length; i++){
//     print_box(returned[i]);
//   }
// }

// // print all added box to console
// function print_added(){
//   console.log('added_box:');
//   for(var i=0;i<added.length; i++){
//     print_box(added[i]);
//   }
// }

// // print all deleted object to console
// function print_deleted(){
//   console.log('deleted_box:' + deleted.length);
//   for(var i =0; i< deleted.length; i++){
//     print_box(deleted[i]);
//   }
// }

// function print_box(box){
//   console.log('category: '+box.category+'; coordinates: '+parseInt(box.coordinates[0])+', '+parseInt(box.coordinates[1])+', '+parseInt(box.coordinates[2])+', '+parseInt(box.coordinates[3]));
// }
function getratio(){
  var canvas_width = $(input_img).width();
  ratio = original_width / canvas_width;
  console.log('original_width'+original_width)
  var canvas_height = $(input_img).height();
  console.log('ratio: ' +ratio);
  return ratio;
}
function zoom_in(){
    w = $('#input_img').width();
    h = $('#input_img').height();
    new_h = h + 100;
    new_w = w *(new_h/h);
    h = new_h;
    w = new_w;
    $('#input_img').width(new_w);
    $('#input_img').height(new_h);
    $('#editor_canvas').attr('height', $(input_img).height());
    $('#editor_canvas').attr('width', $(input_img).width());
    $('#animation_canvas').attr('height', $(input_img).height());
    $('#animation_canvas').attr('width', $(input_img).width());
    // q清空画布，重新计算缩放比例，重新绘制
    clear_all_canvas();
    ratio = getratio();
    draw_all();
    
}



function zoom_out(){
  // for(var i = 0; i < 10; i++){
    w = $('#input_img').width();
    h = $('#input_img').height();
    new_h = h - 100;
    new_w = w *(new_h/h);
    h = new_h;
    w = new_w;
    $('#input_img').width(new_w);
    $('#input_img').height(new_h);
    // 
    $('#editor_canvas').attr('height', $(input_img).height());
    $('#editor_canvas').attr('width', $(input_img).width());
    $('#animation_canvas').attr('height', $(input_img).height());
    $('#animation_canvas').attr('width', $(input_img).width());
    clear_all_canvas();
    ratio = getratio();
    draw_all();
}

// 清空画布并且重置
function clear_all_canvas(){
  console.log('clear_all_canvas');
  ani_context.clearRect(0, 0, ani_canvas.width, ani_canvas.height);
  context.clearRect(0, 0, canvas.width, canvas.height);
}

  // 请求别别结果并且绘制
  function get_boxes(){
    var post_data = {
      'action':'get_boxes'
    }
    $.ajax({
      url:'/user/return_OCR_results/',
      type:'GET',
      data: post_data,
      processData: false,  // tell jquery not to process the data
      contentType: false, // tell jquery not to set contentType
      success: function(res) {
        // console.log(res);
        //清空所有的array(因为到了新的一页)
        returned_backups = new Array();
        returned = new Array();
        added_backups = new Array();
        added = new Array();
        deleted_backups = new Array();
        deleted = new Array();
        ratio = getratio();
        returned = res;
        console.log('get_boxes')
        console.log(returned);
        console.log(added);
        draw_all();
      },
      error: function(err){
        alert(err['message']);
      }
    });
  }

  //导出我的标注
  // function get_my_data(){
  //   alert('get_my_data')
  //   var post_data = {
  //     'action':'get_my_data'
  //   }
  //   $.ajax({
  //     url:'/user/get_my_data/',
  //     type:'GET',
  //     data: post_data,
  //     processData: false,  // tell jquery not to process the data
  //     contentType: false, // tell jquery not to set contentType
  //     success: function(res) {
  //       console.log('success');
  //     },
  //     error: function(err){
  //       alert(err['message']);
  //     }
  //   });
  // }
    // 导出我的标注
    function get_my_data() {
        console.log('get_my_data');
        var url = '/user/get_my_data/';
        var fileName = "testAjaxDownload.txt";
        var form = $("<form></form>").attr("action", url).attr("method", "post");
        form.append($("<input></input>").attr("type", "hidden").attr("name", "fileName").attr("value", fileName));
        form.appendTo('body').submit().remove();
    }

    // 导出所有人的标注
    function get_group_data() {
      console.log('get_group_data');
      var url = '/user/get_group_data/';
      var fileName = "testAjaxDownload.txt";
      var form = $("<form></form>").attr("action", url).attr("method", "post");
      form.append($("<input></input>").attr("type", "hidden").attr("name", "fileName").attr("value", fileName));
      form.appendTo('body').submit().remove();
    }

    // 修改分辨率
    function change_resolution(){
      var resolution = parseInt($('#resolution').val());
      post_data = {'resolution' : resolution};
      console.log(post_data);
      $.ajax({
        url:'/user/change_resolution/',
        type:'POST',
        data: post_data,
        // processData: false,  // tell jquery not to process the data
        // contentType: false, // tell jquery not to set contentType
        success: function(res) {
          $('#the_resolution').html(res['resolution']);
          console.log(res['resolution']);
          alert('分辨率设置为: ' + res['resolution'] + '% 。')
        },
        error: function(err){
          alert(err['message']);
        }
      });
    }

    function group_management(){
      window.location.open('/user/group_management/') 
    }
    
// console.log('change_resolution');
      // var url = '/user/change_resolution/';
      // var form = $('<form></form>').attr('action', url).attr('method', 'post');
      // form.append($("<input></input>").attr('type', 'hidden').attr('name', 'resolution').attr('value', my_resolution));
      // form.appendTo('body').submit().remove();

  //根据 editor-menu-container (div)的宽度来调整 editor-menu-container的宽度
  window.onload = resize_editor_region();
  // window.onload = get_boxes();
  window.onload = select_page();
  