// создать склад
jQuery(document).ready(function ($) {
    $('#new_storage_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/new_storage/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    location.reload();
                }
                else{
                      display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});