function vote_prims(item){
     var sending_data;
     sending_data += "&csrfmiddlewaretoken=" + csrftoken;

     sending_data += "&party_pk=" +  $(item).attr('data-party');
     sending_data += "&player_pk=" + $(item).attr('data-candidate');

     $.ajax({
        type: "POST",
        url: "/primaries/vote/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
//                    alert(data.response);
            }
        }
    });
}