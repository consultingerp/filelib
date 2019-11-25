var current_product_template_id = sessionStorage.getItem("current_product_detail_id");



function product_image_replace(){
    console.error('product_image_replace')
    $.get('/online_shop/get_product_image/' + current_product_template_id, {}, function(datas){
        var d = JSON.parse(datas);
        console.error(datas)
        /*big_image_replace*/
        /*small_image_replace */
        $('#big_image_replace').empty()
        $('#small_image_replace').empty()
        for(var i=0;i < d.length; i++){
            var image = d[i]
            console.error(image)
            var big_image_html =
            "<figure class='product-gallery__image zoom'>" +
            "<img src='" + image + "'  alt='Product'>" +
            "<div class='product-gallery__actions'>" +
            "<button class='action-btn btn-zoom-popup'><i class='la la-eye'></i></button>" +
            "</div>" +
            "</figure>";
            console.error(i)
            console.error(big_image_html)
            $('#big_image_replace').append(big_image_html);
            var small_image_html =
            "<figure class='product-gallery__nav-image--single'>" +
            "<img src='" + image + "'alt='Products'>" +
            "</figure>";
            console.error(small_image_html)
            $('#small_image_replace').append(small_image_html);
        }

        //恢复图片轮播
        var $html = $('html'),
            $body = $('body'),
            $document = $(document),
            $window = $(window),
            $pageUrl = window.location.href.substr(window.location.href.lastIndexOf("/") + 1),
            $header = $('.header'),
            $overlay = $('.global-overlay'),
            $headerPosition = ( $header.elExists() ) ? $header.offset().top : '',
            $mainHeaderHeight = ( $header.elExists() ) ? $header[0].getBoundingClientRect().height : 0,
            $headerTotalHeight = $headerPosition + $mainHeaderHeight,
            $fixedHeader = $('.header--fixed'),
            $fixedHeaderPosition = ( $fixedHeader.elExists() ) ? $fixedHeader.offset().top : '',
            $fixedHeaderHeight = ( $fixedHeader.elExists() ) ? $fixedHeader[0].getBoundingClientRect().height : 0,
            $dom = $('.wrapper').children(),
            $elementCarousel = $('.element-carousel'),
            $footer = $('.footer');
    	if($elementCarousel.elExists()){
            var slickInstances = [];

            /*For RTL*/
            if( $html.attr("dir") == "rtl" || $body.attr("dir") == "rtl" ){
                $elementCarousel.attr("dir", "rtl");
            }

            function customPagingNumb($pagingOptions){
                var i = ($pagingOptions.currentSlide ? $pagingOptions.currentSlide : 0) + 1;
                var $current = i.toString().padStart(2, '0');
                var $total = $pagingOptions.slick.slideCount.toString().padStart(2, '0');
                $pagingOptions.selector.html('<span class="current">'+$current+'</span>/<span class="total">'+$total+'</span>');
            }

            function addClassToItem($this){
                $this.find('.slick-slide.slick-active').first().addClass('first-active');
                $this.find('.slick-slide.slick-active').last().addClass('last-active');
            }

            function removeClassFromItem($this){
                $this.find('.slick-slide.slick-active').first().removeClass('first-active');
                $this.find('.slick-slide.slick-active').last().removeClass('last-active');
            }

            $elementCarousel.each(function(index, element){
                var $this = $(this);

                // Carousel Options
                var $parent = $(this).parent()[0];
                var $status = $($parent).find('.custom-paging');

                var $options = typeof $this.data('slick-options') !== 'undefined' ? $this.data('slick-options') : '';

                var $spaceBetween = $options.spaceBetween ? parseInt($options.spaceBetween, 10) : 0,
                    $spaceBetween_xl = $options.spaceBetween_xl ? parseInt($options.spaceBetween_xl, 10) : 0,
                    $rowSpace = $options.rowSpace ? parseInt($options.rowSpace, 10) : 0,
                    $customPaging = $options.customPaging ? $options.customPaging : false,
                    $vertical = $options.vertical ? $options.vertical : false,
                    $focusOnSelect = $options.focusOnSelect ? $options.focusOnSelect : false,
                    $asNavFor = $options.asNavFor ? $options.asNavFor : '',
                    $fade = $options.fade ? $options.fade : false,
                    $autoplay = $options.autoplay ? $options.autoplay : false,
                    $autoplaySpeed = $options.autoplaySpeed ? parseInt($options.autoplaySpeed, 10) : 5000,
                    $swipe = $options.swipe ? $options.swipe : true,
                    $swipeToSlide = $options.swipeToSlide ? $options.swipeToSlide : true,
                    $touchMove = $options.touchMove ? $options.touchMove : true,
                    $verticalSwiping = $options.verticalSwiping ? $options.verticalSwiping : true,
                    $draggable = $options.draggable ? $options.draggable : true,
                    $arrows = $options.arrows ? $options.arrows : false,
                    $dots = $options.dots ? $options.dots : false,
                    $adaptiveHeight = $options.adaptiveHeight ? $options.adaptiveHeight : true,
                    $infinite = $options.infinite ? $options.infinite : false,
                    $centerMode = $options.centerMode ? $options.centerMode : false,
                    $centerPadding = $options.centerPadding ? $options.centerPadding : '',
                    $variableWidth = $options.variableWidth ? $options.variableWidth : false,
                    $speed = $options.speed ? parseInt($options.speed, 10) : 500,
                    $appendArrows = $options.appendArrows ? $options.appendArrows : $this,
                    $prevArrow = $arrows === true ? ($options.prevArrow ? '<span class="'+ $options.prevArrow.buttonClass +'"><i class="'+ $options.prevArrow.iconClass +'"></i></span>' : '<button class="tty-slick-text-btn tty-slick-text-prev">previous</span>') : '',
                    $nextArrow = $arrows === true ? ($options.nextArrow ? '<span class="'+ $options.nextArrow.buttonClass +'"><i class="'+ $options.nextArrow.iconClass +'"></i></span>' : '<button class="tty-slick-text-btn tty-slick-text-next">next</span>') : '',
                    $rows = $options.rows ? parseInt($options.rows, 10) : 1,
                    $rtl = $options.rtl || $html.attr('dir="rtl"') || $body.attr('dir="rtl"') ? true : false,
                    $slidesToShow = $options.slidesToShow ? parseInt($options.slidesToShow, 10) : 1,
                    $slidesToScroll = $options.slidesToScroll ? parseInt($options.slidesToScroll, 10) : 1;

                /*Responsive Variable, Array & Loops*/
                var $responsiveSetting = typeof $this.data('slick-responsive') !== 'undefined' ? $this.data('slick-responsive') : '',
                    $responsiveSettingLength = $responsiveSetting.length,
                    $responsiveArray = [];
                    for (var i = 0; i < $responsiveSettingLength; i++) {
                        $responsiveArray[i] = $responsiveSetting[i];

                    }

                // Adding Class to instances
                $this.addClass('slick-carousel-'+index);
                $this.parent().find('.slick-dots').addClass('dots-'+index);
                $this.parent().find('.slick-btn').addClass('btn-'+index);

                if($spaceBetween != 0){
                    $this.addClass('slick-gutter-'+$spaceBetween);
                }
                var $slideCount = null;
                $this.on('init', function(event, slick){
                    addClassToItem($this);
                    $slideCount = slick.slideCount;
                    if($slideCount <= $slidesToShow){
                        $this.children('.slick-dots').hide();
                    }
                    if($customPaging == true){
                        var $current = '01';
                        var $total = $slideCount.toString().padStart(2, '0');
                        $status.html('<span class="current">'+$current+'</span>/<span class="total">'+$total+'</span>');
                    }
                    var $firstAnimatingElements = $('.slick-slide').find('[data-animation]');
                    doAnimations($firstAnimatingElements);
                });

                $this.slick({
                    slidesToShow: $slidesToShow,
                    slidesToScroll: $slidesToScroll,
                    asNavFor: $asNavFor,
                    autoplay: $autoplay,
                    autoplaySpeed: $autoplaySpeed,
                    speed: $speed,
                    infinite: $infinite,
                    arrows: $arrows,
                    dots: $dots,
                    adaptiveHeight: $adaptiveHeight,
                    vertical: $vertical,
                    focusOnSelect: $focusOnSelect,
                    centerMode: $centerMode,
                    centerPadding: $centerPadding,
                    variableWidth: $variableWidth,
                    swipe: $swipe,
                    swipeToSlide: $swipeToSlide,
                    touchMove: $touchMove,
                    draggable: $draggable,
                    fade: $fade,
                    appendArrows: $appendArrows,
                    prevArrow: $prevArrow,
                    nextArrow: $nextArrow,
                    rtl: $rtl,
                    responsive: $responsiveArray,
                });



                $this.on('beforeChange', function(e, slick, currentSlide, nextSlide) {
                    removeClassFromItem($this);
                    var $animatingElements = $('.slick-slide[data-slick-index="' + nextSlide + '"]').find('[data-animation]');
                    doAnimations($animatingElements);
                });
                function doAnimations(elements) {
                    var animationEndEvents = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
                    elements.each(function() {
                        var $el = $(this);
                        var $animationDelay = $el.data('delay');
                        var $animationDuration = $el.data('duration');
                        var $animationType = 'animated ' + $el.data('animation');
                        $el.css({
                            'animation-delay': $animationDelay,
                            'animation-duration': $animationDuration,
                        });
                        $el.addClass($animationType).one(animationEndEvents, function() {
                            $el.removeClass($animationType);
                        });
                    });
                }

                $this.on('afterChange', function(e, slick){
                    addClassToItem($this);
                });

                $this.on('init reInit afterChange', function (event, slick, currentSlide, nextSlide) {
                    var $pagingOptions = {
                        event: event,
                        slick: slick,
                        currentSlide: currentSlide,
                        nextSlide: nextSlide,
                        selector: $status
                    }
                    if($customPaging == true){
                        customPagingNumb($pagingOptions);
                    }
                });

                // Updating the sliders in tab
                $('body').on('shown.bs.tab', 'a[data-toggle="tab"], a[data-toggle="pill"]', function (e) {
                    $this.slick('setPosition');
                });
            });
	}


        // 恢复大图上的点击事件
        var productThumb = $(".product-gallery__image img"),
        imageSrcLength = productThumb.length,
        images = [],
        indexNumbArray = [];

        for (var i = 0; i < productThumb.length; i++) {
            images[i] = {"src": productThumb[i].src};
        }

        $('.btn-zoom-popup').on('click', function (e) {
            $(this).lightGallery({
                thumbnail: false,
                dynamic: true,
                autoplayControls: false,
                download: false,
                actualSize: false,
                share: false,
                hash: true,
                index: 0,
                dynamicEl: images
            });
        });

    });
}

$(document).ready(function(){
    console.error('ready')
    product_image_replace();
})

window.onload=function(){
    console.error('onload')
    var get_product_template_detail_xhr = new XMLHttpRequest();
    get_detail_url = "/online_shop/get_product_detail/" + current_product_template_id
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
}