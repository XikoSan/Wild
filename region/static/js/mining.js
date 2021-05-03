jQuery(document).ready(function ($) {
    $('.mining_form').submit(function(e){
        e.preventDefault();

//        $(this).find('.btn').html('<img src="/static/img/clock.png"; width=100%; height=100% />');
        btn = $(this).find('.btn')
        btn.html(var_mining_process);

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
//                    todo: актуализация header
                    actualize();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }

                $(".btn-mining").each(function() {
                    $(this).prop( "disabled", false );
                });
                btn.html(var_mining_default);
            }
        });
    });

});