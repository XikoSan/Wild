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
                    document.getElementById("rating_up").style.opacity = 0.5
                    document.getElementById("rating_down").style.opacity = 1
                }
                else{
                    document.getElementById("rating_down").style.opacity = 0.5
                    document.getElementById("rating_up").style.opacity = 1
                }

                if (data.rating > 0){
                    data.rating = '+' + data.rating
                }
                document.getElementById("rating").innerHTML = data.rating;
                document.getElementById("rated_up").innerHTML = data.rated_up;
                document.getElementById("rated_down").innerHTML = data.rated_down;

                if(mode == 'pro'){
                    document.getElementById("rating").style.color = '#8DFF47';
                }
                else{
                    document.getElementById("rating").style.color = 'tomato';
                }

            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    })
}

// подписка на автора
function subscribe(id, mode) {

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken + '&pk=' + id;

    $.ajax({
        type:'POST',
        url:'/subscription/',
        data: sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                if(mode == 'sub'){
                    document.getElementById("subscription").innerHTML = text_unsubscribe;
                    sub_mode = 'unsub';
                }
                else{
                    document.getElementById("subscription").innerHTML = text_subscribe;
                    sub_mode = 'sub';
                }
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    })
}