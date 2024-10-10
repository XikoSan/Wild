
//сменить цвет государства
$('#color_set').submit(function(e){
    e.preventDefault();
    var sending_data = $(this).serialize();
    $.ajax({
        type: "POST",
        url: "/state_color_change/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
});

//сменить описание партии
jQuery(document).ready(function ($) {
    $('#deskr_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/switch_state_description/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    var element = document.getElementById("state-desc-area");
                    var new_name = element.value;
                    $('#state_deskr').html(new_name);
                    closeModalByRemoveClass('#state-desc-edit');
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

