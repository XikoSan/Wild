function up_skill(skill){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&skill=" + skill;
    $.ajax({
        type: "POST",
        url: "/up_skill/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};