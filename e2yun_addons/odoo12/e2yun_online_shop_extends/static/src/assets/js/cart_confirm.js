
function load_cart_confirm(){
		$('.product_list div').remove();

		var access_token = $("input[name='csrf_token']").val();
		$.post('/e2yun_online_shop_extends/get_cart_confirm_info',{
			'access_token' : access_token,
			'csrf_token' : access_token
		},function(datas){
			var d = JSON.parse(datas);
			var total_price = d['total_price'];
			var line = d['line'];
			var total_num = d['total_num'];
			var phone = d['phone'];
			var address = d['address'];

			$('#total_num').text(total_num);
			$('.amount').text('￥'+total_price);
			$("input[name='phone']").val(phone);
			$("input[name='address']").val(address);

			for(var i = 0;i<line.length;i++){
				var l = line[i];

				$('#product_list').append("<div class='aui-flex aui-flex-default aui-mar10'>\n" +
                    "                            <div class='aui-flex-goods'>\n" +
                    "                                <img src='/"+l.image_url+"' alt=''>\n" +
                    "                            </div>\n" +
                    "                            <div class='aui-flex-box'>\n" +
                    "                                <h2>"+l.product_name+"</h2>\n" +
                    "                                <div class='aui-flex aui-flex-clear'>\n" +
                    "                                    <div class='aui-flex-box'>￥"+l.price+"</div>\n" +
                    "                                    <div>x"+l.product_num+"</div>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>");
			}
		});
	}

	function confirm(){
		var phone = $("input[name='phone']").val();
		var address = $("input[name='address']").val();
		var access_token = $("input[name='csrf_token']").val();
		var coupon = $("select[name='coupon']").val();

		$.post('/e2yun_online_shop_extends/order_confirm',{
			'access_token' : access_token,
			'csrf_token' : access_token,
			'phone':phone,
			'address':address,
			'coupon':coupon
		},function(datas){
			var d = JSON.parse(datas);
				if(!d['success']){
					alert('确认订单异常');
				}else{
					window.location.href = '/e2yun_online_shop_extends/order_done_page'
				}

        });
	}

	function get_coupon(){
		var access_token = $("input[name='csrf_token']").val();
		$.post('/e2yun_online_shop_extends/get_coupon',{
			'access_token' : access_token,
			'csrf_token' : access_token
		},function(datas){
			var d = JSON.parse(datas);
			if(!d || d.length == 0){
				$("select[name='coupon']").append("<option value=''>无可用优惠券</option>");
			}else{
				$("select[name='coupon']").append("<option value=''>请选择优惠券</option>");
			}

			for(var i = 0;i<d.length;i++){
				var l = d[i];
				$("select[name='coupon']").append("<option value='"+l.coupo_code+"'>"+l.coupo_name+"</option>");
			}
		});
	}


	$(document).ready(function() {

		$.post('/e2yun_online_shop_extends/get_token',{
		},function(datas) {
            var d = JSON.parse(datas);
            $('body').append("<input name='csrf_token' value="+d['csrf_token']+" type='hidden' />");

            load_cart_confirm();
            get_coupon();
        });

		$("button[name='order_confirm']").click(function(){
			confirm();
		});

	});

