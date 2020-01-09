function get_timestamp() {
  var tmp = Date.parse( new Date() ).toString();
  tmp = tmp.substr(0,10);
  return tmp;
}

function load_index_data(area_id){
    $.get('/online_shop/get_index_data', {'area_id':area_id}, function(datas){
        var d = JSON.parse(datas);
        var recommend_datas = d['recommend_datas'];
        var sell_well_datas = d['sell_well_datas'];
        // var logo_partner_datas = d['logo_partner_datas'];
        $('.recommend_product').empty();
        for(var i = 0;i<recommend_datas.length;i++){
            var p = recommend_datas[i];

            var html = "<div class='item'>\n" +
            "          <div class='single-slide d-flex align-items-center bg-color' data-bg-color='#F0F0F0'>\n" +
            "             <div class='row align-items-center no-gutters w-100'>\n" +
            "                <div class='col-xl-7 col-md-6 mb-sm--50'>\n" +
            "                   <figure data-animation='fadeInUp' data-duration='.3s' data-delay='.3s' class='plr--15'>\n" +
            "                       <img src='"+p.product_image+"' alt='product image' class='mx-auto' style='height: 270px;'>\n" +
            "                    </figure>\n" +
            "                 </div>\n" +
            "                 <div class='col-md-6 col-lg-5 offset-lg-1 offset-xl-0'>\n" +
            "                    <div class='slider-content'>\n" +
            "                       <div class='slider-content__text mb--40 mb-md--30'>\n" +
            // "                          <p class='mb--15' data-animation='fadeInUp' data-duration='.3s' data-delay='.3s'>#介绍文字</p>\n" +
            "                          <p class='mb--20' data-animation='fadeInUp' data-duration='.3s' data-delay='.3s'>"+p.recommend_text+"</p>\n" +
            "                          <h2 class='heading__primary lh-1' data-animation='fadeInUp' data-duration='.3s' data-delay='.3s'>"+p.product_name+"</h2>\n" +
            "                        </div>\n" +
            "                        <div class='slider-content__btn'>\n" +
            "                           <a href='/online_shop/get_product_detail_page/"+p.product_id+"' class='btn btn-outline btn-brw-2' data-animation='fadeInUp' data-duration='.3s' data-delay='.6s'>现在购买</a>\n" +
            "                        </div>\n" +
            "                     </div>\n" +
            "                   </div>\n" +
            "                 </div>\n" +
            "               </div>\n" +
            "             </div>";

            $('.recommend_product').append(html);
        }

        $('.sell_well_datas').empty();
        for(var i = 0;i<sell_well_datas.length;i++) {
            var p = sell_well_datas[i];
            var html = "<div class='item'>\n"+
                "          <div class='ft-product bg-color align-items-center' data-bg-color='#F0F0F0'>\n" +
                "             <div class='product-inner'>\n" +
                "                <div class='product-image'>\n" +
                "                   <figure class='product-image--holder' style='padding-top:30px;'>\n" +
                "                       <img src='" + p.product_image + "' alt='Product' class='mx-auto' style='height: 270px;max-width: 80%'>\n" +
                "                   </figure>\n" +
                "                   <a href='/online_shop/get_product_detail_page/" + p.product_id + "' class='product-overlay'></a>\n" +
                "                  </div>\n" +
                "                  <div class='product-info plr--20'>\n" +
                "                     <h3 class='product-title'><a href='/online_shop/get_product_detail_page/" + p.product_id + "'>" + p.product_name + "</a></h3>\n" +
                "                     <div class='product-info-bottom'>\n" +
                // "                        <div class='product-price-wrapper'>\n" +
                // "                           <span class='money'>$150</span>\n" +
                // "                        </div>\n" +
                // "                        <a href='cart.html' class='add-to-cart'>\n" +
                // "                           <i class='la la-plus'></i>\n" +
                // "                           <span>Add To Cart</span>\n" +
                // "                        </a>\n" +
                "                      </div>\n" +
                "                   </div>\n" +
                "                </div>\n" +
                "             </div>\n" +
                "          </div>";

            $('.sell_well_datas').append(html);

        }

        var logo_data_xhr = new XMLHttpRequest();
        logo_data_xhr.open("GET", "/online_shop/get_index_logo_data", true);
        logo_data_xhr.send();

		logo_data_xhr.onreadystatechange = function(){
            if (logo_data_xhr.readyState  === 4 && logo_data_xhr.status === 200) {
                document.getElementById("logo_image").innerHTML = logo_data_xhr.responseText;
            }

        };

        setTimeout(function(){
            jQuery.getScript("/e2yun_online_shop_extends/static/src/assets/js/main.js?_="+ get_timestamp(),function(){
                $('.ft-preloader').removeClass("active");
            })
        },300)

    });
}

$(document).ready(function(){
    load_index_data();


    $('.searchform__submit').click(function(){
        var search_key = $('#popup-search').val()
        if(search_key){
            window.location.href="/hhjc_shop_search_product_list_page?search_key="+search_key+"&area_id="+$("#area_chooser ").val()
        }
    });
});
