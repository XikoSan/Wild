jQuery(document).ready(function ($) {

    $('#post-form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();
         sending_data += "&code=" + document.getElementById('code').value;
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;


        $.ajax({
            type: "POST",
            url: "/activate_invite/",
            data:  sending_data,
            cache: false,
            success: (data) => {
                if (data.response == 'ok'){
                    location.reload();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn);
                }
            }
        });
    });

});
