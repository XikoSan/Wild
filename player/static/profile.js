function open_bio(){

    $('#bio_edit').hide();

    $('#bio_cancel').show();
    $('#bio_send').show();

    $('#player_bio').attr("disabled", false);
};

function close_bio(){

    $('#bio_edit').show();

    $('#bio_cancel').hide();
    $('#bio_send').hide();

    $('#player_bio').attr("disabled", true);
};

function send_bio(){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&bio=" + $('#player_bio').val();
    $.ajax({
        type: "POST",
        url: "/change_bio/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                close_bio();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};

// Никнейм

function open_nickname(){

    $('#nickname_edit').hide();

    $('#nickname_cancel').show();
    $('#nickname_send').show();

    $('#player_nickname').attr("disabled", false);
};

function close_nickname(){

    $('#nickname_edit').show();

    $('#nickname_cancel').hide();
    $('#nickname_send').hide();

    $('#player_nickname').attr("disabled", true);
};

function send_nickname(){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&nickname=" + $('#player_nickname').val();
    $.ajax({
        type: "POST",
        url: "/change_nickname/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                actualize();
                $('#nickname').html($('#player_nickname').val());
                close_nickname();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};

