var current_product_template_id = sessionStorage.getItem("current_product_detail_id");

function get_timestamp() {
  var tmp = Date.parse( new Date() ).toString();
  tmp = tmp.substr(0,10);
  return tmp;
}

function get_template_id(){
    $.get('/online_shop/get_template_id', {}, function(datas){
        var d = JSON.parse(datas);
        if(d['product_template_id']){
            current_product_template_id = d['product_template_id']
        }
        product_image_replace();

        var get_product_template_detail_xhr = new XMLHttpRequest();
        get_detail_url = "/online_shop/get_product_detail/" + current_product_template_id

        var area_id = sessionStorage.getItem('current_area_id')
        if(area_id){
            get_detail_url = get_detail_url + "?area_id="+area_id
        }

        get_product_template_detail_xhr.open("GET", get_detail_url, true);
        get_product_template_detail_xhr.send();

        var get_product_description_xhr = new XMLHttpRequest();
        get_product_description_url = "/online_shop/get_product_description/" + current_product_template_id
        get_product_description_xhr.open("GET", get_product_description_url, true)
        get_product_description_xhr.send();

        get_product_template_detail_xhr.onreadystatechange = function(){
            if (get_product_template_detail_xhr.readyState  === 4 && get_product_template_detail_xhr.status === 200) {
                document.getElementById("product_detail_replace").innerHTML = get_product_template_detail_xhr.responseText;
            }
        }

        get_product_description_xhr.onreadystatechange = function(){
            if (get_product_description_xhr.readyState  === 4 && get_product_description_xhr.status === 200) {
                document.getElementById("product_description_replace").innerHTML = get_product_description_xhr.responseText;
            }
        }

    })
}

function product_image_replace(){
    $.get('/online_shop/get_product_image/' + current_product_template_id, {}, function(datas){
        var d = JSON.parse(datas);
        /*big_image_replace*/
        /*small_image_replace */
        $('#big_image_replace').empty()
        $('#small_image_replace').empty()
        for(var i=0;i < d.length; i++){
            var image = d[i]
            var big_image_html =
            "<figure class='product-gallery__image zoom'>" +
            "   <img style='max-height: 320px; ' src='/" + image + "'  alt='Product'/>" +

                // "<img role='presentation' style='max-height: 500px;max-width: 800px;' alt='' src='/" + image + "' class='zoomImg' />" +
            "</figure>";

            $('#big_image_replace').append(big_image_html);

            var small_image_html =
            "<figure class='product-gallery__nav-image--single'>" +
            "<img style='max-height: 120px; ' src='/" + image + "'alt='Products'>" +
            "</figure>";
            $('#small_image_replace').append(small_image_html);

        }

        setTimeout(function(){
            jQuery.getScript("/e2yun_online_shop_extends/static/src/assets/js/main.js?_="+ get_timestamp(),function(){
            $('.ft-preloader').removeClass("active");
        })
        },300);


    });
}

$(document).ready(function(){
    get_template_id();
})

// window.onload=setTimeout(function(){
//     var get_product_template_detail_xhr = new XMLHttpRequest();
//     get_detail_url = "/online_shop/get_product_detail/" + current_product_template_id
//     get_product_template_detail_xhr.open("GET", get_detail_url, true);
//     get_product_template_detail_xhr.send();
//
//     var get_product_description_xhr = new XMLHttpRequest();
//     get_product_description_url = "/online_shop/get_product_description/" + current_product_template_id
//     get_product_description_xhr.open("GET", get_product_description_url, true)
//     get_product_description_xhr.send();
//
//     get_product_template_detail_xhr.onreadystatechange = function(){
//         if (get_product_template_detail_xhr.readyState  === 4 && get_product_template_detail_xhr.status === 200) {
//             document.getElementById("product_detail_replace").innerHTML = get_product_template_detail_xhr.responseText;
//         }
//     }
//
//     get_product_description_xhr.onreadystatechange = function(){
//         if (get_product_description_xhr.readyState  === 4 && get_product_description_xhr.status === 200) {
//             document.getElementById("product_description_replace").innerHTML = get_product_description_xhr.responseText;
//         }
//     }
// },100);