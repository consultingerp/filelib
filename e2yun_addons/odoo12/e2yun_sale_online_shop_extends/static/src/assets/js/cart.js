function list_btn_add_cart_click(e){
	var childrens = e.target.parentNode.children;
	var product_id = childrens[0].value;
	var product_template_id = childrens[1].value;
	var csrf_token = $('input[name="csrf_token"]').val();

	$.post('/e2yun_sale_online_shop_extends/add_cart',{
		'product_id':Number(product_id),
		'product_template_id':Number(product_template_id),
		'csrf_token':csrf_token,
		'add_qty':1
	},function(datas){
		var d = JSON.parse(datas);
		if(d.success){
			get_cart_qty();
			// $("a[href='#miniCart']").trigger("click");
		}
	});

}

function detail_add_cart(){
	var csrf_token = $('input[name="csrf_token"]').val();
	var product_id = $('input[name="inp_product_id"]').val();
	var product_template_id = $('input[name="inp_product_template_id"]').val();

	$.post('/e2yun_sale_online_shop_extends/add_cart',{
		'product_id':Number(product_id),
		'product_template_id':Number(product_template_id),
		'csrf_token':csrf_token,
		'add_qty':1
	},function(datas){
		var d = JSON.parse(datas);
		if(d.success){
			// $("a[href='#miniCart']").trigger("click");
			get_cart_qty();
		}
	});
}

function cart_update(product_id,product_template_id,add_qty,set_qty){

	if(set_qty == 0){
		set_qty = -1;
	}

	var csrf_token = $("input[name='csrf_token']").val();
	$.post('/e2yun_sale_online_shop_extends/add_cart',{
		'product_id':Number(product_id),
		'product_template_id':Number(product_template_id),
		'csrf_token':csrf_token,
		'add_qty':add_qty,
		'set_qty':set_qty
	},function(datas){
		var d = JSON.parse(datas);
		if(d.success){
			load_cart();
		}
	});
}

function load_cart(){
		$('.mini-cart__list li').remove();

		var access_token = $("input[name='csrf_token']").val();
		$.post('/e2yun_sale_online_shop_extends/get_cart_info',{
			'access_token' : access_token,
			'csrf_token' : access_token
		},function(datas){
			var d = JSON.parse(datas);
			var total_price = d['total_price'];
			var line = d['line'];

			var cart_qty = 0

			for(var i = 0;i<line.length;i++){
				var l = line[i];

				$('.mini-cart__list').append("<li class='mini-cart__product'>" +
						"                                <a href='#' class='mini-cart__product-remove' onclick='cart_update("+l.product_id+","+l.product_template_id+",0,-1)'>\n" +
						"                                    <i class='la la-remove'></i>\n" +
						"                                </a>\n" +
						"                                <div class='mini-cart__product-image'>\n" +
						"                                    <img id='image_cart_product_template_"+l.product_template_id+"' src='/"+l.image_url+"' alt='products'>\n" +
						"                                </div>\n" +
						"                                <div class='mini-cart__product-content'>\n" +
						"                                    <a id='list_image_cart_product_template_"+l.product_template_id+"' class='mini-cart__product-title' href='#'>"+l.product_name+"</a>\n" +
						"                                    <span class='mini-cart__product-quantity'>￥"+l.price+
						"										<a class='my_btn my_btn_minus' onclick='cart_update("+l.product_id+","+l.product_template_id+",1,"+(l.product_num-1)+")' title='减少'/><span style='float: right;'>&nbsp;&nbsp;"+l.product_num+"&nbsp;&nbsp;</span>" +
						"										<a class='my_btn my_btn_plus' onclick='cart_update("+l.product_id+","+l.product_template_id+",1,\"+(l.product_num+1)+\")' title='增加'/></span>\n" +
						"                                </div>\n" +
                    	"                            </li>");
					$('#list_image_cart_product_template_'+l.product_template_id).click(function(){

						var id_pre = this.id.slice(33);
						sessionStorage.setItem("current_product_detail_id", id_pre)
    					window.location.href="/hhjc_shop_product_details"
					});

					$('#image_cart_product_template_'+l.product_template_id).click(function(){

						var id_pre = this.id.slice(28);
						sessionStorage.setItem("current_product_detail_id", id_pre)
    					window.location.href="/hhjc_shop_product_details"
					});

					cart_qty = cart_qty + 1



					// $('.mini-cart__product-remove').click(function(e){
					// 	cart_update(l.product_id,l.product_template_id,);
					// });
			}

			$('.ammount').text('￥'+total_price);
			$('#cart_qty').text(cart_qty);

		});
	}


	$("a[href='#miniCart']").click(function(e){
		load_cart();
	});

// mui.ready(function(){
// 	alert('mui.ready');
//
// 	mui.plusReady(function(){
// 		alert('mui.plusReady');
// 		$("#startCan").bind('tap',function(){
//         // 扫描二维码
//         var barScan = new plus.barcode.Barcode("scanContainer");
//         barScan.onmarked = function(type,code,file){
//             var result = "type"+type+"<br/>code:"+code+"<br/>file:"+file;
//             $("#info").html(result);
//         };
//         //barScan.start(); 开始扫描
//         barScan.start({conserve:true,filename:"_doc/barcode/"});// 可以配置扫描后保存的路径
//     });
// 	})
// });

function get_cart_qty(){
	if($('#cart_qty')){
		var access_token = $("input[name='csrf_token']").val();
		$.post('/e2yun_sale_online_shop_extends/ger_cart_qty',{
			'csrf_token':access_token
		},function(qdatas){
			var qd = JSON.parse(qdatas);
			$('#cart_qty').text(qd['cart_qty']);
			var d2L=document.querySelector(".cart_img").offsetLeft;
			var d2T=document.querySelector(".cart_img").offsetTop;
			$("#cart_qty").css({
				 "position":"absolute",
				 "left":d2L+10,
				 "top":d2T-5,
				 "display": ''
			 })
		});
	}
}

function contact(){
	// alert('功能完善中');
}

$(document).ready(function() {

	$.post('/e2yun_sale_online_shop_extends/get_token',{
	},function(datas) {
		var d = JSON.parse(datas);
		$('body').append("<input name='csrf_token' value="+d['csrf_token']+" type='hidden' />");
		get_cart_qty();

	});
});
