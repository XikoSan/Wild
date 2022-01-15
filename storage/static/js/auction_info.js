// Поднять ставку
jQuery(document).ready(function ($) {
    $("#all_lots").on("submit", ".set_bet_form", function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        sending_data += "&csrfmiddlewaretoken=" + csrftoken;
        $.ajax({
            type: "POST",
            url: "/set_bet/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response != 'ok'){
                    alert(data.response);
                }
                else{
                    location.reload();
                }
            }
        });
    });
});