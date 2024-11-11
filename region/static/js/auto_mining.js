function start_auto(e, resource){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&resource=" + resource;

    $.ajax({
        type: "POST",
        url: "/start_auto/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){

                var elements = document.getElementById('mining_main').querySelectorAll('.mining_form');

                for (var i = 0; i < elements.length; i++) {
                    var child = elements[i];

                    var startAuto = child.getElementsByClassName('start_auto')[0];
                    var cancelAuto = child.getElementsByClassName('cancel_auto')[0];

                    if (startAuto) {
                        startAuto.style.display = 'flex';
                    }

                    if (cancelAuto) {
                        cancelAuto.style.display = 'none';
                    }
                }

                e.target.closest(".mining_form").getElementsByClassName("start_auto")[0].style.display = 'none';

                var currentdate = new Date();
                e.target.closest(".mining_form").getElementsByClassName("cancel_auto")[0].querySelectorAll("span")[0].innerHTML = currentdate.getHours() + ":" + (currentdate.getMinutes()<10?'0':'') + currentdate.getMinutes();
                e.target.closest(".mining_form").getElementsByClassName("cancel_auto")[0].style.display = 'flex';
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};

function cancel_auto(e){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;

    $.ajax({
        type: "POST",
        url: "/cancel_auto/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                e.target.closest(".mining_form").getElementsByClassName("start_auto")[0].style.display = 'flex';
                e.target.closest(".mining_form").getElementsByClassName("cancel_auto")[0].style.display = 'none';
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};
