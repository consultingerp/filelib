$(function () {
    $.ajax({
        type: "POST",
        url: "/onlineshopuserinfo",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        cache: false,
        async: false,
        data: '{}',
        success: function (data) {
            $("#area_chooser").empty();
            var user_company = data.result.rest.user_company;
            $.each(data.result.rest.company, function (index, item) {
                var selected  = user_company==  item.id?"selected":"";
                $("#area_chooser").append("<option value='" + item.id + "' "+selected+">" + item.show_area_text + "</option>");
            })
        }
    });


    $("#area_chooser").change(function () {
        load_index_data($("#area_chooser ").val());
    });


});