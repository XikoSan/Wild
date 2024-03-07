function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

function getStorageStatus(id, energy){
    //запрашиваем свежие данные склада
    $.ajax({
        type: "GET",
        url: "/status/" + String(id) + "/",
        dataType: "html",
        cache: false,
        success: function(data){
            result = JSON.parse(data);
            for (const [key, value] of Object.entries(result)) {
              total_stocks[String(id)][String(key)] = value;
            }
            actualize_lines(document.getElementById('storage').dataset.value, energy)
        }
    });
}

function actualize_lines(id, energy){
    var energy_dict = { 'energy': schemas[$('#good').val()]['energy'] },
    schema = Object.assign({}, energy_dict, schemas[$('#good').val()][$('#schema').val()])

    for (const [key, value] of Object.entries(schema)) {
      line = document.getElementById(String(key) + '_line')
      var max_value = 0;

      if (key=='energy'){
        max_value = Math.floor(energy/schema[key]) * schema[key]
      }
      else{
        max_value = Math.floor(total_stocks[id][key]/schema[key]) * schema[key]
      }

      $(line.getElementsByClassName("crude_amount")[0]).attr('max', max_value);
      $(line.getElementsByClassName("storage_stocks")[0]).html(numberWithSpaces(max_value));
      $(line.getElementsByClassName("crude_count")[0]).attr('max', max_value);

      if (max_value == 0){
          $(cloned_line.getElementsByClassName("crude_count")[0]).val(0);
          $(cloned_line.getElementsByClassName("crude_amount")[0]).val(0);
      }
    }
}

function setInputValue(val){
    count = val;
    setAnotherValues();
}

function setEnergyValue(child){

    if (Math.ceil( count / consignment ) * $(child.getElementsByClassName("crude_count")[0]).attr('step') > child.getElementsByClassName("crude_count")[0].max){
        child.getElementsByClassName("crude_count")[0].value = child.getElementsByClassName("crude_count")[0].max
    }
    else{
        child.getElementsByClassName("crude_count")[0].value = Math.ceil( count / consignment ) * $(child.getElementsByClassName("crude_count")[0]).attr('step');
    }
    child.getElementsByClassName("crude_amount")[0].value = Math.ceil( count / consignment ) * $(child.getElementsByClassName("crude_amount")[0]).attr('step');

}

function setAnotherValues(){

    document.getElementById('count').value = count;
    var elements = document.getElementById('storage_info_block').querySelectorAll('.cloned_line');

    for (var i = 0; i < elements.length; i++) {
        var tableChild = elements[i];

        if (tableChild.getElementsByClassName("energy_count").length){
            setEnergyValue(tableChild);
        }
        else{
            if (count * $(tableChild.getElementsByClassName("crude_count")[0]).attr('step') > tableChild.getElementsByClassName("crude_count")[0].max){
                tableChild.getElementsByClassName("crude_count")[0].value = tableChild.getElementsByClassName("crude_count")[0].max
            }
            else{
                tableChild.getElementsByClassName("crude_count")[0].value = count * $(tableChild.getElementsByClassName("crude_count")[0]).attr('step');
            }
            tableChild.getElementsByClassName("crude_amount")[0].value = count * $(tableChild.getElementsByClassName("crude_amount")[0]).attr('step');
        }
    }
}

function setAmountValue(line, target){
    line.getElementsByClassName("crude_amount")[0].value = target.value;

    if (target.classList.contains("energy_count")){
        count = target.value / $(target).attr('step') * consignment;
    }
    else{
        count = target.value / $(target).attr('step');
    }

    setAnotherValues();
}

function setCountValue(line, target){
    line.getElementsByClassName("crude_count")[0].value = target.value;

    if (target.classList.contains("energy_count")){
        count = target.value / $(target).attr('step') * consignment;
    }
    else{
        count = target.value / $(target).attr('step');
    }

    setAnotherValues();
}

function set_component_line(schema, crude, last_crude_name){
    var cloned_line = document.getElementById('crude_line').cloneNode(true);
    cloned_line.id = crude + '_line';
    cloned_line.className += ' cloned_line';

    var crude_name = goods_names[crude];
    cloned_line.getElementsByClassName("crude_name")[0].innerHTML = crude_name;

    var max_value = 0;
    if (crude=='energy'){
        $.ajax({
            async: false,
            beforeSend: function() {},
            type: "GET",
            url: "/status/0/",
            dataType: "html",
            cache: false,
            success: function(data){

                result = JSON.parse(data);

                $('#cash').html(numberWithSpaces(result.cash));

                $('#gold').html(numberWithSpaces(result.gold));
                $('#energy').html(result.energy);
                max_value = Math.floor(result.energy/schema[crude]) * schema[crude]
            }
        });
    }
    else{
        max_value = Math.floor(total_stocks[document.getElementById('storage').dataset.value][crude]/schema[crude]) * schema[crude]
    }

    if(crude == 'energy'){
        cloned_line.getElementsByClassName("crude_count")[0].classList.add("energy_count");
        cloned_line.getElementsByClassName("crude_amount")[0].classList.add("energy_count");
    }

    $(cloned_line.getElementsByClassName("crude_count")[0]).attr('max', max_value);
    $(cloned_line.getElementsByClassName("crude_amount")[0]).attr('max', max_value);

    $(cloned_line.getElementsByClassName("storage_stocks")[0]).html(numberWithSpaces(max_value));

    $(cloned_line.getElementsByClassName("crude_count")[0]).attr('min', schema[crude]);
    $(cloned_line.getElementsByClassName("crude_amount")[0]).attr('min', schema[crude]);

    $(cloned_line.getElementsByClassName("crude_count")[0]).attr('step', schema[crude]);
    $(cloned_line.getElementsByClassName("crude_amount")[0]).attr('step', schema[crude]);

    $(cloned_line.getElementsByClassName("crude_price")[0]).html(price_text + ': ' + numberWithSpaces(schema[crude]));

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

    return last_crude_name;
}

jQuery(document).ready(function ($) {

      // Создаем новый экземпляр MutationObserver
      const observer = new MutationObserver(mutations => {

        mutations.forEach(mutation => {

          if (mutation.attributeName === 'data-value') {

            $('#group').val('default');
            $('#good').val('default');

            $('#schema').val('default');
            schema_select = document.getElementById('schema');
            $(schema_select).children(":not(#schema_default)").remove();

            $('#storage_info_block').children(".cloned_line").remove();

            $("#good").attr("disabled", true);
            $("#schema").attr("disabled", true);
            $(".factory__topCreate").attr("disabled", true);
            $("#count").attr("disabled", true);

          }

        });

      });

      // Начинаем отслеживать изменения атрибутов myDiv
      observer.observe(document.getElementById("storage"), { attributes: true });

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

//        document.getElementById('accept').disabled = true
        $(".factory__topCreate").attr("disabled", true);

        if($('#action').val() == 'sell'){
            $("#stocks_value").html('?');
        }

        var selected = $(e.target).val();
        for (let i = 0; i < groups_n_goods[selected].length; i++) {
            $('#good_' + groups_n_goods[selected][i] ).show();
        }
        // меняем размер пачки ресурсов при изменении группы
        if(consignment_dict[selected] !== undefined){
            consignment = consignment_dict[selected];
        }
        else{
            consignment = 1;
        }

        $("#good").attr("disabled", false);
    });

//  выводить информацию о схемах производства товара
    $('#good').change(function() {
        $(".factory__topCreate").attr("disabled", true);

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
                if(crude == 'Наличные' || crude == 'energy' ){
                    continue;
                }

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
//        document.getElementById('accept').disabled = false
        $(".factory__topCreate").attr("disabled", false);

        $("#count").attr("disabled", false);

        var energy_dict = { 'energy': schemas[$('#good').val()]['energy'] },
        schema = Object.assign({}, energy_dict, schemas[$('#good').val()][$('#schema').val()])

        var last_crude_name = 'crude_header';

        $('#storage_info_block').children(".cloned_line").remove();

        last_crude_name = set_component_line(schema, 'energy', last_crude_name);
        last_crude_name = set_component_line(schema, 'Наличные', last_crude_name);

        for (crude in schema){
            if(crude !== 'Наличные' && crude !== 'energy' ){
                last_crude_name = set_component_line(schema, crude, last_crude_name);
            }
        }

        count = document.getElementById('count').value;
        setAnotherValues();
    });


    $('#produce_form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();
         sending_data += "&csrfmiddlewaretoken=" + csrftoken + "&storage=" + document.getElementById('storage').dataset.value;

        ajaxSettings = {
            type: "POST",
            url: "/produce/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    // вместо actualize() чтобы передать текущее значение энергии в актуализацию строк
                    $.ajax({
                        async: false,
                        beforeSend: function() {},
                        type: "GET",
                        url: "/status/0/",
                        dataType: "html",
                        cache: false,
                        success: function(data){

                            result = JSON.parse(data);

                            $('#cash').html(numberWithSpaces(result.cash));

                            $('#gold').html(numberWithSpaces(result.gold));
                            $('#energy').html(result.energy);
                        }
                    });
                    getStorageStatus(document.getElementById('storage').dataset.value, result.energy);
                }
                else{
                    if (data.response == 'captcha'){
                        captcha_checking(data);
                    }
                    else{
                        display_modal('notify', data.header, data.response, null, data.grey_btn)
                    }
                }
            }
        };

        captcha_action = function() {
            $.ajax(ajaxSettings);
        };

        $.ajax(ajaxSettings);

    });

});