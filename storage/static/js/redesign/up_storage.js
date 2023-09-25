function up_storage(){
    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    $.ajax({
        type: "POST",
        url: "/upgrade_storage/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
};