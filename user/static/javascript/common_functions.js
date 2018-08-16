// 一些通用的方法
function logout(){
	// post_data = {'logout':'logout'}
	// $.ajax({
 //    url:'/user/logout/',
 //    data:post_data,
 //    // processData: false,  // tell jquery not to process the data
 //    // contentType: false, // tell jquery not to set contentType
 //    success:function(res){
 //      if(res['message'] !='success'){
 //        alert(res['message']);
 //      }
 //    },
 //    error:function(err){
 //       alert('网络连接失败,稍后重试',err);
 //    }
 //  })
 	window.location.href = '/user/logout/';
}