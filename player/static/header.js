var RATE_LIMIT_IN_MS = 100;
var NUMBER_OF_REQUESTS_ALLOWED = 1;
var NUMBER_OF_REQUESTS = 0;


jQuery(document).ready(function ($) {
    setInterval(function()
    {
        NUMBER_OF_REQUESTS = 0;

    }, RATE_LIMIT_IN_MS);

    $.ajaxSetup ({
      beforeSend: function canSendAjaxRequest()
        {
            var can_send = NUMBER_OF_REQUESTS < NUMBER_OF_REQUESTS_ALLOWED;
            NUMBER_OF_REQUESTS++;
            return can_send;
        }
    });
});

function numberWithSpaces(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

window.onload = function countdown() {
    if (document.getElementById("refill-countdown") != undefined){
        var elem = document.getElementById("refill-countdown");

        //получает строку
        var sec_string = $('#refill-countdown').attr('data-text');
        var sec = parseInt(sec_string);

        //запускаем функцию с повторением раз 1 секунду
        var id = setInterval(frame, 1000);
        function frame() {
            if (sec == 0) {
                elem.textContent = '';
                clearInterval(id);
            } else {

                var h = sec/3600 ^ 0 ;
                var m = (sec-h*3600)/60 ^ 0 ;
                var s = sec-h*3600-m*60 ;
                elem.textContent = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
                sec = --sec;
            }
        }
    }
}

function actualize(){
    $.ajax({
        beforeSend: function() {},
        type: "GET",
        url: "/status/0/",
        dataType: "html",
        cache: false,
        success: function(data){

            result = JSON.parse(data);

            $('#cash').html('$' + numberWithSpaces(result.cash) );
            $('#cash').attr('title', locked_txt + numberWithSpaces(result.locked) ).tooltip('fixTitle');

            $('#gold').html(numberWithSpaces(result.gold));
            $('#energy').html(energy_txt + result.energy + '%');
        }
    });
}

function recharge(){
    //запрашиваем свежие данные состояния золота и энергетиков игрока
    $.ajax({
        type: "GET",
        url: "/status/recharge/",
        dataType: "html",
        cache: false,
        success: function(data){

            result = JSON.parse(data);
            //если у игрока хватает энергетиков для пополнения до ста
            if (result.response == 'ok'){
                var token = "&csrfmiddlewaretoken=" + csrftoken;
                $.ajax({
                    beforeSend: function() {},
                    type: "POST",
                    url: "/recharge/",
                    data: token,
                    cache: false,
                    success: function(result){
                        if (result.response == 'ok'){
                            $('#energy').html(energy_txt + '100%');
                        }
                        else{
                            display_modal('notify', result.header, result.response, null, result.grey_btn)
                        }
                    }
                });
            }
            else{
                display_modal('notify', result.header, result.response, null, result.grey_btn)
            }
        }
    });
}

// Отображение диалогового окна поверх игры
// mode          - режим:
// 1) notify  - заголовок, текст, список значений, кнопка "закрыть"
// 2) ask  - заголовок, текст, список значений, кнопки "закрыть" и "сохранить"
// header        - заголовок окна
// body          - текст окна
// green_btn_txt - текст на зеленой кнопке ("сохранить" или "подтвердить")
// grey_btn_txt  - текст на серой кнопке ("отмена" или "ок")
function display_modal(mode, header, body, green_btn_txt, grey_btn_txt){
    // предварительно обнуляем чекбокс
    $('#InfoModalDecision').attr("checked", null);
    // скрываем зеленую, если не нужна
    if (mode == 'notify'){
        $('#InfoModal').find(".modal-green").hide();
    }
    else{
        $('#InfoModal').find(".modal-green").show();
    }
    // заголовок
    $('#InfoModal').find("#InfoModalTitle").text(header);
    // текст
    $('#InfoModal').find(".modal-body").text(body);
    // текст зеленой кнопки (если передан)
    if (typeof green_btn_txt !== 'undefined'){
        $('#InfoModal').find(".modal-green").text(green_btn_txt);
    }
    // текст серой кнопки
    $('#InfoModal').find(".modal-grey").text(grey_btn_txt);
    // показать окно
    $('#InfoModal').modal('show')
}

//показ времени до окончания процесса
function countdown() {
    if (document.getElementsByClassName("time_back") != undefined){
         //запускаем функцию с повторением раз 1 секунду
        var id = setInterval(frame, 1000);

        unitblock = document.getElementsByClassName("time_back");
        function frame() {
             for (i = 0; i < unitblock.length; i++) {
                var sec_string = $(unitblock[i]).attr('data-text');
                //получает строку
                var sec = parseInt(sec_string);
                if (sec == 0) {
//                    страница не перезагружается.
                        unitblock[i].textContent = "00:00:00";
                } else {
                    var d = sec/86400 ^ 0;
                    var h = (sec-d*86400)/3600 ^ 0 ;
                    var m = ((sec-d*86400)-h*3600)/60 ^ 0 ;
                    var s = sec-d*86400-h*3600-m*60 ;
                    unitblock[i].textContent = (h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
                    sec = --sec;
                    $(unitblock[i]).attr('data-text', sec.toString());
                }
            }

        }
    }
}
window.addEventListener('load', countdown);