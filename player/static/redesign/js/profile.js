jQuery(document).ready(function ($) {
    $('#gold_4_repost').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/reward_4_repost",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    //запрашиваем свежие данные состояния валют и энергии игрока
                    $.ajax({
                        type: "GET",
                        url: "/status/0/",
                        dataType: "html",
                        cache: false,
                        success: function(data){

                            result = JSON.parse(data);

                            $('#cash').html(numberWithSpaces(result.cash));
                            $('#gold').html(numberWithSpaces(result.gold));

                            $('#energy_status_text').html(numberWithSpaces(result.energy));
                        }
                    });
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn);
                }
            }
        });
    });

    $('#color_set').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/color_change",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    location.reload();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn);
                }
            }
        });
    });
//  переключение языка
    $('#lang_change').change(function(e){
        e.preventDefault();
        var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
        sending_data += "&lang=" + $(this).val();

        $.ajax({
            type: "POST",
            url: "/set_lang",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    location.reload();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
//  Смена оторбражения партийного аватара
    $('#ava_back_change').change(function() {
        var sending_data;
        sending_data += "&csrfmiddlewaretoken=" + csrftoken + "&show_party_back=" + this.checked;

        $.ajax({
            type: "POST",
            url: "/change_back_allow",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response != 'ok'){
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

function color_default(e){
    e.preventDefault();
    $('#color_back').val('#28353E');
    $('#color_block').val('#284E64');
    $('#color_text').val('#FFFFFF');
    $('#color_acct').val('#EB9929');
};

function open_bio(){

    $('#bio_edit').hide();

    $('#bio_cancel').show();
    $('#bio_send').show();

    $('#player_bio').show();
    $('#player_bio_view').hide();
};

function close_bio(){

    $('#bio_edit').show();

    $('#bio_cancel').hide();
    $('#bio_send').hide();

    $('#player_bio').hide();
    $('#player_bio_view').show();
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
                $('#player_bio_view').html($('#player_bio').val());
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

    $('#player_nickname_view').hide();
    $('#player_nickname').show();
};

function close_nickname(){

    $('#nickname_edit').show();

    $('#nickname_cancel').hide();
    $('#nickname_send').hide();

    $('#player_nickname_view').show();
    $('#player_nickname').hide();
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
                $('#player_nickname_view').html($('#player_nickname').val());
                close_nickname();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};

