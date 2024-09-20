$('#new_sending_form').submit(function(e){
    e.preventDefault();
    var data = $(this).serialize();

    $.ajax({
        type: "POST",
        url: "/create_admin_sending/",
        data: data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                display_modal('notify', 'Успешно', 'Рассылка запущена', null, 'ок');
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
   });
});