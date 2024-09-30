// Поднять ставку
jQuery(document).ready(function ($) {
    $("#all_lots").on("submit", ".set_bet_form", function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        sending_data += "&source=" + $(this).find(".auction_default_storage").data("value");
        sending_data += "&csrfmiddlewaretoken=" + csrftoken;
        $.ajax({
            type: "POST",
            url: "/set_bet/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response != 'ok'){
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
                else{
                    location.reload();
                }
            }
        });
    });
});