// $(function () {
//     $.ajax({
//         type: "POST",
//         url: "/onlineshopuserinfo",
//         contentType: "application/json; charset=utf-8",
//         dataType: "json",
//         cache: false,
//         async: false,
//         data: '{}',
//         success: function (data) {
//             $("#area_chooser").empty();
//             $("#area_chooser").append("<option value='-1'>所有地区</option>");
//             $.each(data.result.rest.company, function (index, item) {
//                 $("#area_chooser").append("<option value='" + item.id + "'>" + item.show_area_text + "</option>");
//                 $('#area_chooser').niceSelect('update');
//             })
//         }
//     });
//
//
// });