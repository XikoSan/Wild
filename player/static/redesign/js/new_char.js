jQuery(document).ready(function ($) {

    $('#post-form').submit(function(e){
        e.preventDefault();

        var sending_data = new FormData(this);

        console.log(sending_data);
        $.ajax({
            type: "POST",
            url: "/player/new/",
            data:  sending_data,
            processData: false,  // Сообщить jQuery не передавать эти данные
            contentType: false,   // Сообщить jQuery не передавать тип контента
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


});
