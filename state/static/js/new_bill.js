jQuery(document).ready(function ($) {
// отправить законопроект на рассмотрение
    $('.new_bill').submit(function(e){
        e.preventDefault();

        var sending_data = $(this).serialize();

        $.ajax({
            type: "POST",
            url: "/new_bill/",
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