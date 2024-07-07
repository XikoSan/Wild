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

function callable_countdown() {
    if (document.getElementById("refill-countdown") != undefined){
        var elem = document.getElementById("refill-countdown");

        //получает строку
        var sec_string = $('#refill-countdown').attr('data-text');
        var sec = parseInt(sec_string);

        if (sec == 0) {
            elem.firstElementChild.innerHTML = refill_button_txt;
        } else {

            var h = sec/3600 ^ 0 ;
            var m = (sec-h*3600)/60 ^ 0 ;
            var s = sec-h*3600-m*60 ;
            elem.firstElementChild.innerHTML = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
            sec = --sec;
        }

        //запускаем функцию с повторением раз 1 секунду
        clearInterval(timer_id);
        timer_id = setInterval(frame, 1000);
        function frame() {
            if (sec == 0) {
                elem.firstElementChild.innerHTML = refill_button_txt;
                clearInterval(timer_id);
            } else {

                var h = sec/3600 ^ 0 ;
                var m = (sec-h*3600)/60 ^ 0 ;
                var s = sec-h*3600-m*60 ;
                elem.firstElementChild.innerHTML = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
                sec = --sec;
            }
        }
    }
}

var timer_id = 'timer';

jQuery(document).ready(function ($) {

    console.log('onload');

    if (document.getElementById("refill-countdown") != undefined){
        var elem = document.getElementById("refill-countdown");

        //получает строку
        var sec_string = $('#refill-countdown').attr('data-text');
        var sec = parseInt(sec_string);
        if (sec == 0) {
            elem.firstElementChild.innerHTML = refill_button_txt;
        } else {

            var h = sec/3600 ^ 0 ;
            var m = (sec-h*3600)/60 ^ 0 ;
            var s = sec-h*3600-m*60 ;
            elem.firstElementChild.innerHTML = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
            sec = --sec;
        }

        //запускаем функцию с повторением раз 1 секунду
        clearInterval(timer_id);
        timer_id = setInterval(frame, 1000);
        function frame() {
            if (sec == 0) {
                elem.firstElementChild.innerHTML = refill_button_txt;
                clearInterval(timer_id);
            } else {

                var h = sec/3600 ^ 0 ;
                var m = (sec-h*3600)/60 ^ 0 ;
                var s = sec-h*3600-m*60 ;
                elem.firstElementChild.innerHTML = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
                sec = --sec;
            }
        }
    }

    if (document.getElementById("increase-countdown") != undefined){
        var inc_elem = document.getElementById("increase-countdown");

        console.log('onload');

        //получает строку
        var inc_sec_string = $('#increase-countdown').attr('data-text');
        var inc_sec = parseInt(inc_sec_string);

        if (inc_sec == 0) {
            $('#increase_line').hide()
        } else {

            var inc_h = inc_sec/3600 ^ 0 ;
            var inc_m = (inc_sec-inc_h*3600)/60 ^ 0 ;
            var inc_s = inc_sec-inc_h*3600-inc_m*60 ;
            inc_elem.firstElementChild.innerHTML = (inc_m<10?"0"+inc_m:inc_m)+":"+(inc_s<10?"0"+inc_s:inc_s);
            inc_sec = --inc_sec;


            //запускаем функцию с повторением раз 1 секунду
            var inc_id = setInterval(increase_frame, 1000);
            function increase_frame() {
                if (inc_sec == 0) {
                    if (parseInt($('#energy').html()) + parseInt($('#increase_value').attr('data-value')) > 100){
                        $('#energy').html('100');
                    }
                    else{
                        $('#energy').html(parseInt($('#energy').html()) + parseInt($('#increase_value').attr('data-value')));
                    }
                    $('#increase_line').hide()
                    clearInterval(inc_id);
                } else {

                    var inc_h = inc_sec/3600 ^ 0 ;
                    var inc_m = (inc_sec-inc_h*3600)/60 ^ 0 ;
                    var inc_s = inc_sec-inc_h*3600-inc_m*60 ;
                    inc_elem.firstElementChild.innerHTML = (inc_m<10?"0"+inc_m:inc_m)+":"+(inc_s<10?"0"+inc_s:inc_s);
                    inc_sec = --inc_sec;
                }
            }
        }
    }
});

function actualize(){
    $.ajax({
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
                var client = new ClientJS();

                var token = "&csrfmiddlewaretoken=" + csrftoken + "&fprint=" + client.getFingerprint();
                $.ajax({
                    beforeSend: function() {},
                    type: "POST",
                    url: "/recharge/",
                    data: token,
                    cache: false,
                    success: function(result){
                        if (result.response == 'ok'){
                            $('#energy').html('100');
                            $('#refill-countdown').attr('data-text', 600);
                            callable_countdown();
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

//показ времени до окончания процесса
function countdown() {
    if (document.getElementsByClassName("time_back") != undefined){
         //запускаем функцию с повторением раз 1 секунду
        timer_id= setInterval(frame, 1000);

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