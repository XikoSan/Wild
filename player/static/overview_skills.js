function up_skill(skill){
    var client = new ClientJS();
    var sending_data = "&csrfmiddlewaretoken=" + csrftoken + "&fprint=" + client.getFingerprint();
    sending_data += "&skill=" + skill;
    $.ajax({
        type: "POST",
        url: "/up_skill/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
//              в обучении не нужно обновлять страницу
                if (check_edu){
                    location.reload();
                }
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
};

function boost_skill(skill){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&skill=" + skill;
    $.ajax({
        type: "POST",
        url: "/boost_skill/",
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
};

// отменить изучение навыка
function skill_cancel(e, skill_pk) {
e.preventDefault();
cancel_skill_pk = skill_pk;

$(".modal__ok").on( "click", cancel_contunue);
$(".modal__cancel").on( "click", clear_modal);

display_modal('ask', cnl_header, cnl_text, cnl_yes, cnl_cancel)

}

function cancel_contunue() {

     var sending_data;
     sending_data += "&csrfmiddlewaretoken=" + csrftoken;
     sending_data += "&skill=" + cancel_skill_pk;
    $.ajax({
        type: "POST",
        url: "/skill_cancel/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                clear_modal()
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });

    $('#InfoModal').find(".modal-grey").click();
    clear_modal()
}

function clear_modal() {
    $('#InfoModal').find(".modal-green").prop("onclick", null).off("click");
    $('#InfoModal').find(".modal-grey").prop("onclick", null).off("click");
    cancel_skill_pk = null;
}