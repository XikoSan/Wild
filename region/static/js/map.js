// получаем прописку в этом регионе
function to_fly(){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&region=" + this.parentElement.getElementsByClassName("region_id")[0].value;

    $.ajax({
        beforeSend: function() {},
        type: "POST",
        url: "/map",
        data: sending_data,
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
};