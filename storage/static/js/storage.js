jQuery(document).ready(function ($) {
  $("#trade_tab").on("input", "#cash_at_player", function(){
//  проверка что в форме передачи денег сменились значения
    if($('#cash_at_player').val() !== $('#cash_at_player').attr('value') || $('#cash_at_storage').val() !== $('#cash_at_storage').attr('value') ){
        $("#do_transfer").attr("disabled", false);
    }
    else{
        $("#do_transfer").attr("disabled", true);
    }
//    если в одном поле увеличилось значние, надо уменьшить в другом и наоборот
    $('#cash_at_storage').val(parseInt(document.getElementById('cash').dataset.text) + parseInt(document.getElementById('storage_cash').dataset.text) - $('#cash_at_player').val() );
  });

  $("#trade_tab").on("input", "#cash_at_storage", function(){
//  проверка что в форме передачи денег сменились значения
    if($('#cash_at_player').val() !== $('#cash_at_player').attr('value') || $('#cash_at_storage').val() !== $('#cash_at_storage').attr('value') ){
        $("#do_transfer").attr("disabled", false);
    }
    else{
        $("#do_transfer").attr("disabled", true);
    }
//    если в одном поле увеличилось значние, надо уменьшить в другом и наоборот
    $('#cash_at_player').val(parseInt(document.getElementById('cash').dataset.text) + parseInt(document.getElementById('storage_cash').dataset.text) - $('#cash_at_storage').val() );
  });

//  подсказка стоимости энергетиков в золоте
    $("#trade_tab").on("input", "#batteries_count", function(){
        document.getElementById('recharge_cost').innerHTML = "- " + Math.ceil(document.getElementById('batteries_count').value/10) + " G";
    });

//  при передаче денег
    $("#trade_tab").on("submit", "#money_transfer_frm", function(e){
        e.preventDefault();
        var data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/cash_transfer/",
            data: data,
            cache: false,
            success: function(data){
                if (data == 'ok'){
//                  меняем значение в ячейке на складе
                    $('#storage_cash').html(numberWithSpaces($('#cash_at_storage').val()));
                    $('#storage_cash').attr('data-text', $('#cash_at_storage').val());
//                   в строке передаче денег
                    $('#cash_at_player').attr('value', $('#cash_at_player').val())
                    $('#cash_at_storage').attr('value', $('#cash_at_storage').val())
                    $("#do_transfer").attr("disabled", true);
                }
                else{
                    alert(data);
                }
                //запрашиваем свежие данные состояния золота и энергетиков игрока
                $.ajax({
                    type: "GET",
                    url: "/status/0/",
                    dataType: "html",
                    cache: false,
                    success: function(data){

                        result = JSON.parse(data);

                        $('#cash').html('$' + numberWithSpaces(result.cash));
                        $('#cash').attr('data-text', result.cash);
                        $('#gold').html(numberWithSpaces(result.gold));
                    }
                });
            }
       });
    });

 //  при передаче денег
    $("#trade_tab").on("submit", ".replace_set", function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        sending_data += "&csrfmiddlewaretoken=" + csrftoken;
        $.ajax({
        type:'POST',
        url:'/storage_replace/',
        data: sending_data,
        dataType: "html",
        cache: false,
        success: function(data){
        result = JSON.parse(data);
            if (result.responce == 'ok'){
                location.reload();
            }
            else{
                alert(result.responce);
            }
        }
        })
    })

});


function open_trade_line(id){

    // Получаем и скрываем все строки производства
    production_lines = document.getElementsByClassName("tradeline");
    for (i = 0; i < production_lines.length; i++) {
        production_lines[i].style.display = "none";
    }
    //запрашиваем свежие данные состояния золота и энергетиков игрока
    var result = null;
    $.ajax({
        type: "GET",
        url: "/status/0/",
        dataType: "html",
        cache: false,
        success: function(data){

            result = JSON.parse(data);
            $('#cash').html('$' + numberWithSpaces(result.cash));
            $('#cash').attr('data-text', result.cash);
            $('#storage_cash').html(numberWithSpaces(result.storage_cash));
            $('#storage_cash').attr('data-text', result.storage_cash);
            $('#gold').html(numberWithSpaces(result.gold));
        }
    });

    if(document.getElementById(id + "_tradeline") != undefined){
        document.getElementById(id + "_tradeline").style.display = "block";
    }
    else{
        $.ajax({
            type: "GET",
            url: "storage/" + id + "/",
            dataType: "html",
            cache: false,
            success: function(data){
                var div = document.createElement('div');
                div.className = 'row tradeline';
                div.id = id + '_tradeline';

                div.innerHTML = data;
                if(production_lines.length == 0){
                    document.getElementById('trade_tab').innerHTML = '';
                }
                document.getElementById('trade_tab').appendChild(div);
            }
        });
    }
};