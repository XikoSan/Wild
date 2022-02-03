jQuery(document).ready(function ($) {
// отправить законопроект на рассмотрение
    $('.new_bill').submit(function(e){
        e.preventDefault();

        var sending_data = new FormData(this);

        $.ajax({
              url: "/new_bill/",
              type: "POST",
              data: sending_data,
              processData: false,  // Сообщить jQuery не передавать эти данные
              contentType: false,   // Сообщить jQuery не передавать тип контента
              success: function(result){
                  if (result.response == 'ok'){
                      location.reload();
                  }
                  else{
                      display_modal('notify', result.header, result.response, null, result.grey_btn)
                  }
            }
        });
    });

//  выводить только поля выбранного типа законопроекта

    $('#bill_type').change(function(e) {
        // скрываем поля всех типов ЗП
        $('.draft_row').each(function()
        {
            $(this).hide();
        });
        //  показываем нужный
        $('#'+$(e.target).val()).show();
    });
});