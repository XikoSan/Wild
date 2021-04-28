jQuery(document).ready(function ($) {
    $('.mining_form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();

        $.ajax({
            type: "POST",
            url: "/do_mining",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
//                    todo: актуализация header
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });

});