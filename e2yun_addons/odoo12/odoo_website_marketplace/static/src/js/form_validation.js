odoo.define('odoo_website_marketplace.form_validation', function(require){
    'use strict';

    $(document).ready(function(){
        $("#password3").focusout(function(ev){
            
            var $form = $(ev.currentTarget).parents('form');
            
            var fistInput = document.getElementById("password2").value;
            var secondInput = document.getElementById("password3").value;

            if (String(fistInput) != String(secondInput)) 
            {
                document.getElementById("password3").value = null;
                document.getElementById("password3").style.borderColor = "red";
                alert('Please Renter Password.');            
            }
            else{
                document.getElementById("password3").style.borderColor = null;
            }
        });


        $("#email").focusout(function(){

            var email = $("#email").val();

            if(email != 0)
            {
                if(!isValidEmailAddress(email))
                {
                    document.getElementById("email").value = null;
                    document.getElementById("email").style.borderColor = "red";
                    alert('Invalid Email Address.');
                } 
                else{
                    document.getElementById("email").style.borderColor = null;
                }
            } else {
                document.getElementById("email").style.borderColor = null;     
            }

        });

        function isValidEmailAddress(emailAddress) {
            var pattern = new RegExp(/^(("[\w-\s]+")|([\w-]+(?:\.[\w-]+)*)|("[\w-\s]+")([\w-]+(?:\.[\w-]+)*))(@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$)|(@\[?((25[0-5]\.|2[0-4][0-9]\.|1[0-9]{2}\.|[0-9]{1,2}\.))((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){2}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\]?$)/i);
            return pattern.test(emailAddress);
        }
    });


    $('#ratingForm').on('submit', function(event){
        event.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
        type : 'POST',
        url : 'saveRating.php',
        data : formData,
        success:function(response){
            $("#ratingForm")[0].reset();
            window.setTimeout(function(){window.location.reload()},1000)
            }
        });
    });
});