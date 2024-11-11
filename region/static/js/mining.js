function actualize_daily(){
    //запрашиваем свежие данные состояния валют и энергии игрока
    $.ajax({
        type: "GET",
        url: "/daily_status",
        dataType: "html",
        cache: false,
        success: function(data){

            result = JSON.parse(data);

            document.getElementById('energy_consumption').innerHTML = result.energy_consumption;
            document.getElementById('daily_energy_limit').innerHTML = result.daily_energy_limit;

            document.getElementById('energy_progressbar').style.width = result.daily_procent;

            document.getElementById('daily_current_sum').innerHTML = numberWithSpaces(result.daily_current_sum);
        }
    });
};



jQuery(document).ready(function ($) {
    $('.mining_form').submit(function(e){
        e.preventDefault();

        $(".btn-mining").each(function() {
            $(this).prop( "disabled", true );
        });

        var sending_data = $(this).serialize();

        ajaxSettings = {
            type: "POST",
            url: "/do_mining",
            data:  sending_data,
            cache: false,
            success: function(data){

                if (data.response == 'ok'){
                    actualize();
                    actualize_daily();
                }
                else{
                    if (data.response == 'captcha'){
                        captcha_checking(data);
                    }
                    else{
                        display_modal('notify', data.header, data.response, null, data.grey_btn)
                    }
                }

                $(".btn-mining").each(function() {
                    $(this).prop( "disabled", false );
                });
            }
        };

        captcha_action = function() {
            $.ajax(ajaxSettings);
        };

        $.ajax(ajaxSettings);

    });

    $('.cash_retrieve').submit(function(e){
        e.preventDefault();

//        $(this).find('.btn').html('<img src="/static/img/clock.png"; width=100%; height=100% />');
        btn = $(this).find('.btn')
        btn.find('.process').show();
        btn.find('.main').hide();

        $(".btn-mining").each(function() {
            $(this).prop( "disabled", true );
        });

        var sending_data = $(this).serialize();

        $.ajax({
            type: "POST",
            url: "/retrieve_cash",
            data:  sending_data,
            cache: false,
            success: function(data){

                if (data.response == 'ok'){
                    actualize();
                    btn.find('.main').find('.sum').html('$0');
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }

                $(".btn-mining").each(function() {
                    $(this).prop( "disabled", false );
                });
                btn.find('.process').hide();
                btn.find('.main').show();
            }
        });
    });

});