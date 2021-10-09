// основание государства
function state_foundation(){
    var token = "&csrfmiddlewaretoken=" + csrftoken;
    $.ajax({
        beforeSend: function() {},
        type: "POST",
        url: "/state_foundation/",
        data: token,
        cache: false,
        success: function(result){
            if (result.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', result.header, result.response, null, result.grey_btn)
            }
        }
    });
}