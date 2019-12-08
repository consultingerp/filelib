
function load_order(){

		var access_token = $("input[name='csrf_token']").val();
		$.post('/e2yun_online_shop_extends/get_order_done_info',{
			'access_token' : access_token,
			'csrf_token' : access_token
		},function(datas){
			var d = JSON.parse(datas);
			var total_price = d['total_price'];
			var order_code = d['order_code'];
			var order_id = d['order_id'];

			$('.amount').text('￥'+total_price);
			$("span[name='order_code']").text(order_code);
			$("a[name='ordercontact']").attr('href',"/ordercontact/"+order_id);
		});
	}

	$(document).ready(function() {
		$.post('/e2yun_online_shop_extends/get_token',{
		},function(datas) {
            var d = JSON.parse(datas);
            $('body').append("<input name='csrf_token' value="+d['csrf_token']+" type='hidden' />");

            load_order();
        });

		$("a[name='btn_back']").click(function(){
			window.location.href = '/hhjc_shop_order_list'
		})

	});

