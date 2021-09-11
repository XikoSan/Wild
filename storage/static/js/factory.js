function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

function setAnotherValues(count){

    var elements = document.getElementById('storage_info_block').querySelectorAll('.cloned_line');

    for (var i = 0; i < elements.length; i++) {
        var tableChild = elements[i];

        if (count * $(tableChild.getElementsByClassName("crude_count")[0]).attr('step') > tableChild.getElementsByClassName("crude_count")[0].max){
            tableChild.getElementsByClassName("crude_count")[0].value = tableChild.getElementsByClassName("crude_count")[0].max
        }
        else{
            tableChild.getElementsByClassName("crude_count")[0].value = count * $(tableChild.getElementsByClassName("crude_count")[0]).attr('step');
        }
        tableChild.getElementsByClassName("crude_amount")[0].value = count * $(tableChild.getElementsByClassName("crude_amount")[0]).attr('step');
    }

    document.getElementById('count').value = count;
}

function setAmountValue(line, target){
    line.getElementsByClassName("crude_amount")[0].value = target.value;

    var count = target.value / $(target).attr('step');
    setAnotherValues(count);
}

function setCountValue(line, target){
    line.getElementsByClassName("crude_count")[0].value = target.value;

    var count = target.value / $(target).attr('step');
    setAnotherValues(count);
}

jQuery(document).ready(function ($) {

    $('#storage').change(function(e) {

        $('#group').val('default');
        $('#good').val('default');

        $('#schema').val('default');
        $(schema_select).children(":not(#schema_default)").remove();

        $('#storage_info_block').children(".cloned_line").remove();
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

        schema_select = document.getElementById('schema');
        $(schema_select).children(":not(#schema_default)").remove();

        $('#storage_info_block').children(".cloned_line").remove();
        $('#schema').val('default');

        document.getElementById('accept').disabled = true

        if($('#action').val() == 'sell'){
            $("#stocks_value").html('?');
        }

        var selected = $(e.target).val();
        for (good in groups_n_goods[selected]){
            $('#good_' + good ).show();

        }
        $("#good").attr("disabled", false);
    });

//  выводить информацию о схемах производства товара
    $('#good').change(function() {
        schema_select = document.getElementById('schema');
        $(schema_select).children(":not(#schema_default)").remove();

        $('#storage_info_block').children(".cloned_line").remove();

        for (schema in schemas[$('#good').val()]){
            if (schema == 'energy') {
                continue;
            }
            var opt = document.createElement('option');
            opt.value = schema;
            for (crude in schemas[$('#good').val()][schema]){
                var crude_name = goods_names[crude];
                if(opt.innerHTML != ''){
                    opt.innerHTML += ', ';
                    opt.innerHTML += crude_name;
                }
                else{
                    opt.innerHTML += crude_name;
                }
            }
            schema_select.appendChild(opt);
        }

        $('#schema').val('default');

        $("#schema").attr("disabled", false);
    });

//  выводить информацию о запасах в правой части
//  если выбрана схема
    $('#schema').change(function() {
        document.getElementById('accept').disabled = false

        schema = schemas[$('#good').val()][$('#schema').val()]

        energy = schemas[$('#good').val()]['energy']

        var last_crude_name = 'crude_header';

        $('#storage_info_block').children(".cloned_line").remove();

        for (crude in schema){
            var cloned_line = document.getElementById('crude_line').cloneNode(true);
            cloned_line.id = crude + '_line';
            cloned_line.className += ' cloned_line';

            var crude_name = goods_names[crude];
            cloned_line.getElementsByClassName("crude_name")[0].innerHTML = crude_name;

            var max_value = Math.floor(total_stocks[$('#storage').val()][crude]/schema[crude]) * schema[crude]
            $(cloned_line.getElementsByClassName("crude_count")[0]).attr('max', max_value);
            $(cloned_line.getElementsByClassName("crude_amount")[0]).attr('max', max_value);

            $(cloned_line.getElementsByClassName("crude_count")[0]).attr('min', schema[crude]);
            $(cloned_line.getElementsByClassName("crude_amount")[0]).attr('min', schema[crude]);

            $(cloned_line.getElementsByClassName("crude_count")[0]).attr('step', schema[crude]);
            $(cloned_line.getElementsByClassName("crude_amount")[0]).attr('step', schema[crude]);

            if (max_value == 0){
                $(cloned_line.getElementsByClassName("crude_count")[0]).val(0);
                $(cloned_line.getElementsByClassName("crude_amount")[0]).val(0);
            }
            else{
                $(cloned_line.getElementsByClassName("crude_count")[0]).val(schema[crude]);
                $(cloned_line.getElementsByClassName("crude_amount")[0]).val(schema[crude]);
            }

            cloned_line.getElementsByClassName("crude_count")[0].addEventListener('input', function (e) {
                setAmountValue(cloned_line, e.target)
            });
            cloned_line.getElementsByClassName("crude_amount")[0].addEventListener('input', function (e) {
                setCountValue(cloned_line, e.target)
            });

            previous_line = document.getElementById(last_crude_name);
            insertAfter(cloned_line, previous_line);

            last_crude_name = cloned_line.id;
            $('#' + crude + '_line').show();
        }

        setAnotherValues(document.getElementById('count').value)
    });


    $('#new_offer_form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;
//        $.ajax({
//            type: "POST",
//            url: "/create_offer/",
//            data:  sending_data,
//            cache: false,
//            success: function(data){
//                display_modal('notify', data.header, data.response, null, data.grey_btn)
//            }
//        });
    });

});