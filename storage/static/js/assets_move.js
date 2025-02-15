// переместить склад в регион местонаходждения
function move_storage(e, storage_pk) {
e.preventDefault();
move_storage_pk = storage_pk;

$(".modal__ok").on( "click", move_contunue);
$(".modal__cancel").on( "click", clear_modal);

display_modal('ask', move_header, move_text, move_yes, move_cancel)

}

function move_contunue() {

     var sending_data;
     sending_data += "&csrfmiddlewaretoken=" + csrftoken;
     sending_data += "&storage=" + move_storage_pk;
    $.ajax({
        type: "POST",
        url: "/storage_move/",
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

    $('#InfoModal').find(".modal-grey").click();
    clear_modal()
}

function clear_modal() {
    $('#InfoModal').find(".modal-green").prop("onclick", null).off("click");
    $('#InfoModal').find(".modal-grey").prop("onclick", null).off("click");
    move_storage_pk = null;
}