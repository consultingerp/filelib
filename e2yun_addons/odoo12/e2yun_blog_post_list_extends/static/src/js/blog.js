odoo.define('e2yun_website_blog.website_blog', function (require) {
"use strict";
    $(document).ready(function() {
        $('.o_twitter, .o_facebook, .o_linkedin, .o_google, .o_twitter_complete, .o_facebook_complete, .o_linkedin_complete, .o_google_complete').hide();

        $('#o_click_good').on('click',function(){
            var rpc = require('web.rpc');
            var blog_id = $("input[name='blog_post_id']").val();
            rpc.query({
                model: 'blog.post',
                method: 'click_good',
                args:[{'blog_id':blog_id}]
            }).then(function(){
                var good_count = Number($('#good_count').html());
                $('#good_count').html(good_count+1);
                $('#o_click_good').attr("disabled",true).css("pointer-events","none");
            });
        })
    });

});
