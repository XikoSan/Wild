window.onload = function countdown() {
    if (document.getElementById("countdown") != undefined){
        var elem = document.getElementById("countdown");

        var elwidth = $('#countdown').attr('data-text');

        //получает строку
        var sec_string = $('#countdown').attr('data-text');
        var sec = parseInt(sec_string);

        if (sec == 0) {
            location.reload();
        } else {
            var h = sec/3600 ^ 0 ;
            var m = (sec-h*3600)/60 ^ 0 ;
            var s = sec-h*3600-m*60 ;
            elem.textContent = (h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
            sec = --sec;
        }

        //запускаем функцию с повторением раз 1 секунду
        var id = setInterval(frame, 1000);
        function frame() {
            if (sec == 0) {
                location.reload();
                clearTimeout(id);
            } else {

                var h = sec/3600 ^ 0 ;
                var m = (sec-h*3600)/60 ^ 0 ;
                var s = sec-h*3600-m*60 ;
                elem.textContent = (h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
                sec = --sec;
            }
        }
    }
}