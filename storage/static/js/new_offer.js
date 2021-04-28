jQuery(document).ready(function ($) {
//  выводить строчку с блокированной суммой, если скупка
    $('#action').change(function(e) {
        var selected = $(e.target).val();
        if(selected == 'buy'){
            $(".buy_row").each(function()
            {
                $(this).show();
            });
        }
        else{
            $(".buy_row").each(function()
            {
                $(this).hide();
            });
        }
    });

    $('#price').on('input', function (e) {
        $('#cash_to_lock').html('$' + numberWithSpaces($(e.target).val() * $('#count').val()));
    });
    $('#count').on('input', function (e) {
        $('#cash_to_lock').html('$' + numberWithSpaces($(e.target).val() * $('#price').val()));
    });

//  выводить ресурсы категории, когда она выбрана
    $('#group').change(function(e) {
        // скрываем все товары из вариантов
        $("#good option").each(function()
        {
            $(this).hide();
        });
        // ставим товар по умолчанию
        $('#good').val('default');
        $('#good_default').show();
        document.getElementById('accept').disabled = true

        var selected = $(e.target).val();
        for (good in groups_n_goods[selected]){
            $('#good_' + good ).show();

        }
        $("#good").attr("disabled", false);
    });

    $('#good').change(function() {
        document.getElementById('accept').disabled = false
    });

    $('#new_offer_form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;
        $.ajax({
            type: "POST",
            url: "/create_offer/",
            data:  sending_data,
            cache: false,
            success: function(data){
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        });
    });

});