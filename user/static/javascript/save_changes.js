// function make_changes(returned_boxes,added_boxes,deleted_boxes){
// 	var object={
// 		page: 1,
//     returned:returned_boxes,
//     added:added_boxes,
//     deleted:deleted_boxes
//   };
//   $.ajax({
//       type : "POST",  //提交方式
//       url : "../php/savechange.php",
//       data : {
//           "obj" : object
//       },//数据，这里使用的是Json格式进行传输
//       success : function(res) {//返回数据根据结果进行相应的处理
//       		alert((res));
//           console.log(JSON.parse(res));
//       }
//   });
// }