function start_auto(e){
    e.preventDefault();

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&storage=" + document.getElementById('storage').dataset.value;
    sending_data += "&good=" + document.getElementById('good').value;
    sending_data += "&schema=" + document.getElementById('schema').value;

    $.ajax({
        type: "POST",
        url: "/start_auto_produce/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                document.getElementsByClassName("start_auto")[0].style.display = 'none';

                var currentdate = new Date();
                document.getElementsByClassName("cancel_auto")[0].querySelectorAll("span")[0].innerHTML = currentdate.getHours() + ":" + (currentdate.getMinutes()<10?'0':'') + currentdate.getMinutes();
                document.getElementsByClassName("cancel_auto")[0].style.display = 'flex';
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
        url: "/cancel_auto_produce/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                document.getElementsByClassName("start_auto")[0].style.display = 'flex';
                document.getElementsByClassName("cancel_auto")[0].style.display = 'none';
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};
