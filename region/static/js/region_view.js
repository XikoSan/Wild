// получаем прописку в этом регионе
function get_residency(region){
    var token = "&csrfmiddlewaretoken=" + csrftoken + "&region=" + region;
    $.ajax({
        beforeSend: function() {},
        type: "POST",
        url: "/get_residency/",
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