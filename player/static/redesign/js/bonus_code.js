jQuery(document).ready(function ($) {

    $('#post-form').submit(function(e){
        e.preventDefault();

         var sending_data = $(this).serialize();
         sending_data += "&code=" + document.getElementById('code').value;
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;

        console.log(sending_data);

        $.ajax({
            type: "POST",
            url: "/activate_code/",
            data:  sending_data,
            cache: false,
            success: (data) => {
                if (data.response == 'ok'){
                    display_modal('notify', data.header, data.text, null, data.grey_btn);
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn);
                }
                actualize();
            }
        });
    });

});
