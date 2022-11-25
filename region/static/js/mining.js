jQuery(document).ready(function ($) {
    $('.mining_form').submit(function(e){
        e.preventDefault();

        $(".btn-mining").each(function() {
            $(this).prop( "disabled", true );
        });

        var sending_data = $(this).serialize();

        $.ajax({
            type: "POST",
            url: "/do_mining",
            data:  sending_data,
            cache: false,
            success: function(data){

                if (data.response == 'ok'){
                    actualize();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }

                $(".btn-mining").each(function() {
                    $(this).prop( "disabled", false );
                });
            }
        });
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