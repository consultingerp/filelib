
function load_order_detail_data(){
		$('.aui-timeLine-content').empty();

		var access_token = $("input[name='csrf_token']").val();
		$.post('/e2yun_online_shop_extends/get_order_detail_data',{
			'access_token' : access_token,
			'csrf_token' : access_token
		},function(datas){
			var d = JSON.parse(datas);
			var order_name = d['order_name'];
			var line = d['line'];
			$('#order_name').text(order_name);

			for(var i = 0;i<line.length;i++){
				var l = line[i];
				$('.aui-timeLine-content').append("<li class='aui-timeLine-content-item'>\n" +
                    "                            <em class='aui-timeLine-content-icon'></em>\n" +
                    "                            <p>"+l['state']+"</p>\n" +
                    "                            <p style='margin-top: 10px;'>"+l['date']+"</p>\n" +
                    "                        </li>");
			}
		});
	}

	$(document).ready(function() {

		$.post('/e2yun_online_shop_extends/get_token',{
		},function(datas) {
            var d = JSON.parse(datas);
            $('body').append("<input name='csrf_token' value="+d['csrf_token']+" type='hidden' />");

            load_order_detail_data();
        });
	});

