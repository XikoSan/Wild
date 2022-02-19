//проголосовать за закон
function vote_bill(btype, id, mode) {

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken + '&bill_type=' + btype + '&pk=' + id + '&mode=' + mode;

    $.ajax({
        type:'POST',
        url:'/vote_bill/',
        data: sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    })
}

//отменить законопроект
function cancel_bill(btype, id) {

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken + '&bill_type=' + btype + '&pk=' + id;

    $.ajax({
        type:'POST',
        url:'/cancel_bill/',
        data: sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    })
}