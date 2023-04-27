jQuery(document).ready(function ($) {

      // Создаем новый экземпляр MutationObserver
      const observer = new MutationObserver(mutations => {

        mutations.forEach(mutation => {

          if (mutation.attributeName === 'data-value') {
          
            //  при смене склада выводить запасы с него, если продажа
            if($('#action').val() == 'sell'){
                if($('#good').val() !== null){
                    $("#stocks_value").html( numberWithSpaces(total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()]) );
                    $('#count').attr("max", total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()]);
                }
                else{
                    $("#stocks_value").html('?');
                }
            }
          }
    
        });

      });

      observer.observe(document.getElementById("create_default_storage"), { attributes: true });

//  выводить строчку с блокированной суммой, если скупка
    $('#action').change(function(e) {
        var selected = $(e.target).val();
        if(selected == 'buy'){
            $("#buy_row").show();

            $("#stocks").hide();
            $('#count').attr("max", 2147483647);
        }
        else{
            $("#buy_row").hide();
            $("#stocks").show();

            if($('#good').val() !== null){
                $("#stocks_value").html( numberWithSpaces(total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()]) );
                $('#count').attr("max", total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()]);
            }
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
        $('#create_good_default').show();
        document.getElementById('accept').disabled = true

        if($('#action').val() == 'sell'){
            $("#stocks_value").html('?');
            $('#count').attr("max", 0);
        }

        var selected = $(e.target).val();
        for (good in groups_n_goods[selected]){
            $('#create_good_' + good ).show();

        }
        $("#good").attr("disabled", false);
    });

//  выводить информацию о запасах
    $('#good').change(function() {
        document.getElementById('accept').disabled = false

        if($('#action').val() == 'sell'){
            $("#stocks_value").html( numberWithSpaces(total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()]) );
            $('#count').attr("max", total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()]);
        }
    });

    $('#new_offer_form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();
         sending_data += "&storage=" + document.getElementById('create_default_storage').dataset.value;
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;
        $.ajax({
            type: "POST",
            url: "/create_offer/",
            data:  sending_data,
            cache: false,
            success: function(data){
                display_modal('notify', data.header, data.response, null, data.grey_btn);

                var selected = $('#action').val();

                free_offers -= 1;
                $("#free_offers").html(numberWithSpaces(free_offers));

                if(selected == 'sell'){
                    total_stocks[document.getElementById('create_default_storage').dataset.value][$('#good').val()] -= $('#count').val();
                    // заставляем пересчитать числа на экране, с учетом уменьшения запасов
                    const changeEvent = new Event('change');
                    // Получаем ссылку на элемент, для которого нужно вызвать событие
                    const inputElement = document.getElementById('good');
                    // Имитируем событие "change" для элемента
                    inputElement.dispatchEvent(changeEvent);
                }

             }
        });
    });

});