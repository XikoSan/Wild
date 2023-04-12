function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

//переименование партии
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
                    var element = document.getElementById("party-title-area");
                    var new_name = element.value;
                    $('#party_title').html(new_name);
                    closeModalByRemoveClass('#party-name-edit');
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

//сменить описание партии
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
                    var element = document.getElementById("party-desc-area");
                    var new_name = element.value;
                    $('#party_deskr').html(new_name);
                    closeModalByRemoveClass('#party-desc-edit');
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

//добавить новую должность
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

                    var cloned_line = document.getElementById('dummy_line').cloneNode(true);
                    cloned_line.id = String(data.id) + '_line';
                    cloned_line.className += '  position_line';

                    cloned_line.getElementsByClassName("j-t-one")[0].innerHTML = data.title;
                    if (data.party_sec == true){
                        cloned_line.getElementsByClassName("j-t-two")[0].innerHTML = '⭐';
                    }

                    cloned_line.getElementsByClassName("post_id")[0].value = data.id;

                    previous_line = document.getElementById(last_item);
                    insertAfter(cloned_line, previous_line);

                    last_item = cloned_line.id;

                    $('#' + String(data.id) + '_line').show();

                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

//удалить должность
jQuery(document).ready(function ($) {
    $("#roles_lines_placeholder").on("submit", ".rm_role_form", function(e){
        console.log('╨║╤А╤П');
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

                    loc_array[loc_array.length - 1]
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

//роспуск партии
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
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
                }
            }
        });
    });
});

