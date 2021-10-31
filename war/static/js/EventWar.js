jQuery(document).ready(function ($) {

    $(".unit_select_list").on("input", ".unit_input", function(e){
        $('#energy_count' ).html( e.target.value * 1 );
        $('#units_count' ).html( e.target.value );
        $('#damage_count' ).html( e.target.value * 6 );
    });
});

function send_squads(){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;

    $('.unit_input').each(function(i, obj) {
        sending_data += "&" + obj.id + "=" + obj.value;
    });

    sending_data += "&war_id=" + war_id;
    sending_data += "&war_type=" + war_type;
    sending_data += "&side=" + $('#war_side').val();

    console.log(sending_data)

    $.ajax({
        type: "POST",
        url: "/send_squads/",
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
