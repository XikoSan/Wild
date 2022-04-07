//Назначение должности
jQuery(document).ready(function ($) {
    $("#all_members").on("change", ".set_role_form", function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        sending_data += ("&role_id=" + $(this).find("select").val());
        $.ajax({
            type: "POST",
            url: "/set_role/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response != 'ok'){
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});


//Покинуть партию

jQuery(document).ready(function ($) {
    $('#leave_party_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/leave/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    window.location = '/party'
                }
                else{
                    alert(data.response);
                }
            }
        });
    });
});