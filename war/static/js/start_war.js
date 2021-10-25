jQuery(document).ready(function ($) {
    //пересчет парлов
    $('#start_war').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/start_war/",
            data:  sending_data,
            cache: false,
            success: function(data){
                alert(data.response);
            }
        });
    });

});