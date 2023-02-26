//Назначение должности
jQuery(document).ready(function ($) {
    $("#all_members").on("change", ".set_role_form", function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        sending_data += ("&role_id=" + $(this).find("select").val());
        $.ajax({
            type: "POST",
            url: "/set_role/",
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

function set_role(member_id, role_id){
    var sending_data = '&member_id=' + member_id + '&role_id=' + role_id + "&csrfmiddlewaretoken=" + csrftoken;
    $.ajax({
        type: "POST",
        url: "/set_role/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response != 'ok'){
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
            else{
                document.getElementsByClassName("member_" + member_id + "_post")[0].innerHTML = posts[role_id];
            }
        }
    });
};

// выход из партии - вопрос
function leave_check(){
    $(".modal__ok").on( "click", leave_confirm);

    display_modal('ask', leave_header, leave_text, leave_yes, leave_cancel)
};

// выход из партии - окончательный
function leave_confirm(){
    var sending_data = '&party_id=' + $('#party_id').val() + "&csrfmiddlewaretoken=" + csrftoken;
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
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};