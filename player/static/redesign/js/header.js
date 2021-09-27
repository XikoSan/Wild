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
        var elem = document.getElementById("refill-countdown").firstChild;

        //получает строку
        var sec_string = $('#refill-countdown').attr('data-text');
        var sec = parseInt(sec_string);

        var h = sec/3600 ^ 0 ;
        var m = (sec-h*3600)/60 ^ 0 ;
        var s = sec-h*3600-m*60 ;
        elem.textContent = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);

        if (sec == 0) {
        }
        else{
            sec = --sec;
        }

        //запускаем функцию с повторением раз 1 секунду
        var id = setInterval(frame, 1000);
        function frame() {
            if (sec == 0) {
                clearInterval(id);
            }

            var h = sec/3600 ^ 0 ;
            var m = (sec-h*3600)/60 ^ 0 ;
            var s = sec-h*3600-m*60 ;
            elem.textContent = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
            sec = --sec;
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

            $('#cash').html(numberWithSpaces(result.cash) );

            var cash = document.getElementById('cash');
            cash.dataset.title = locked_txt + numberWithSpaces(result.locked);

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
                var token = "&csrfmiddlewaretoken=" + csrftoken;
                $.ajax({
                    beforeSend: function() {},
                    type: "POST",
                    url: "/recharge/",
                    data: token,
                    cache: false,
                    success: function(result){
                        if (result.response == 'ok'){
                            $('#energy').html('100');
                            $('#refill-countdown').attr('data-text', 599);
                            callable_countdown();
                            actualize();
                        }
                        else{
                            alert(result.response)
                        }
                    }
                });
            }
            else{
                alert(result.response)
            }
        }
    });
}

