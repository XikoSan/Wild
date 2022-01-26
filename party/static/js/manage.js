//переименование партии

function open_rename(){

    $('#party_title').hide();

    $('#rename_form').show();

};

function close_rename(){

    $('#party_title').show();

    $('#rename_form').hide();
};


jQuery(document).ready(function ($) {
    $('#rename_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/rename_party/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data == 'ok'){
                    var element = document.getElementById("new_party_name");
                    var new_name = element.value;
                    $('#party_title').html(new_name);
                    close_rename();
                }
                else{
                    $('#new_party_name').val(data);
                }
            }
        });
    });
});

//изменение описания партии

function open_deskr(){

    $('#party_deskr').hide();

    $('#deskr_form').show();

};

function close_deskr(){

    $('#party_deskr').show();

    $('#deskr_form').hide();
};


jQuery(document).ready(function ($) {
    $('#deskr_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/switch_description/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data == 'ok'){
                    var element = document.getElementById("new_party_deskr");
                    var new_name = element.value;
                    $('#party_deskr').html(new_name);
                    close_deskr();
                }
                else{
                    $('#new_party_deskr').val(data);
                }
            }
        });
    });
});

//Добавление должности

jQuery(document).ready(function ($) {
    $('#new_role_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/new_role/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    var div = document.createElement('div');

                    div.className = 'row';
                    div.align = 'center';
                    div.style = 'margin-top: 20px; width: 99%; padding-top: 10px; border-top: 2px solid black;';
                    csrf_token = $('#csrf_form').find('input').val();
                    div.innerHTML = "<div class='col-xs-4 col-sm-4 col-md-4'><font color='black' size='3'><i>" + data.title + "</i></font></div><div class='col-xs-3 col-sm-3 col-md-3' id='" + data.title + '_lead' + "'></div><div class='col-xs-3 col-sm-3 col-md-3' id='" + data.title + '_sec' + "'></div><div class='col-xs-2 col-sm-2 col-md-2'><form class='rm_role_form' role='form'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf_token + "'><input type='hidden' name='post_id' id='post_id' value='" + data.id + "'><input type='image' src='static/img/party/trash-can.png' type='submit' width='20'></form></div>";

                    document.getElementById('roles_lines_placeholder').appendChild(div);

                    if (data.party_lead == true){
                        document.getElementById(data.title + "_lead").innerHTML = "<font color='black' size='3'><div class='glyphicon glyphicon-star'></div></font>";
                    }
                    if (data.party_sec == true){
                       document.getElementById(data.title + "_sec").innerHTML = "<font color='black' size='3'><div class='glyphicon glyphicon-star'></div></font>";
                    }
                    $('#roles_count').html(parseInt(document.getElementById('roles_count').innerHTML) + 1);
                    if (data.roles_count == 10){
                        $('#add_role').slideUp();
                    }
                }
                else{
                    alert(data.response);
                }
            }
        });
    });
});

//Удаление должности

jQuery(document).ready(function ($) {
    $("#roles_lines_placeholder").on("submit", ".rm_role_form", function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/remove_role/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    $($(e.currentTarget).parent()).parent().slideUp();
                    $('#roles_count').html(parseInt(document.getElementById('roles_count').innerHTML) - 1);
                    if (data.roles_count < 10){
                        $('#add_role').slideDown();
                    }
                }
                else{
                    alert(data.response);
                }
            }
        });
    });
});

//Покинуть партию

jQuery(document).ready(function ($) {
    $('#leave_party_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/leave/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    window.location = '/party'
                }
                else{
                    alert(data.response);
                }
            }
        });
    });
});

