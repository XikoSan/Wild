//проголосовать за статью
function vote_article(id, mode) {

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken + '&pk=' + id + '&mode=' + mode;

    $.ajax({
        type:'POST',
        url:'/vote_article/',
        data: sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){

                if(mode == 'pro'){
                    document.getElementById("rating_down").style.opacity = 0.5
                    document.getElementById("rating_up").style.opacity = 1
                }
                else{
                    document.getElementById("rating_up").style.opacity = 0.5
                    document.getElementById("rating_down").style.opacity = 1
                }

                $.ajax({
                    type:'POST',
                    url:'/article_rating/',
                    data: sending_data,
                    cache: false,
                    success: function(data){
                        if (data.response == 'ok'){
                            if (data.rating > 0){
                                data.rating = '+' + data.rating
                            }
                            document.getElementById("rating").innerHTML = data.rating;
                        }
                        else{
                            display_modal('notify', data.header, data.response, null, data.grey_btn)
                        }
                    }
                })
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    })
}