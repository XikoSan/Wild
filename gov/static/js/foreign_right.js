// отклонить все заявки
function residency_reject_all(e){
    var sending_data;
    sending_data += "&csrfmiddlewaretoken=" + csrftoken;
    $.ajax({
        type: "POST",
        url: "/residency_reject_all/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                elem = document.getElementsByClassName('request');
                for (var i = 0; i < elem.length; i++) {
                    elem[i].remove();
                }
                $(e.target).remove();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
}

// принять заявку
function residency_accept(e, req_pk){
    var sending_data;
    sending_data += "&csrfmiddlewaretoken=" + csrftoken + "&req_pk=" + req_pk;
    $.ajax({
        type: "POST",
        url: "/residency_accept/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                $(e.target).closest('.request').remove();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
}

// отклонить заявку
function residency_reject(e, req_pk){
    var sending_data;
    sending_data += "&csrfmiddlewaretoken=" + csrftoken + "&req_pk=" + req_pk;
    $.ajax({
        type: "POST",
        url: "/residency_reject/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                $(e.target).closest('.request').remove();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
}