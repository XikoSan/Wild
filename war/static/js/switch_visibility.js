function switch_visibility(elem, war_type, pk, side) {

    var sending_data = '&war_type=' + war_type + '&pk=' + pk + '&side=' + side + "&csrfmiddlewaretoken=" + csrftoken;

    $.ajax({
        type: "POST",
        url: "/switch_war_visibility/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                const svg = elem.querySelector('svg');
                if (svg) {
                    if (svg.classList.contains('grayscale')) {
                        svg.classList.remove('grayscale');
                    } else {
                        svg.classList.add('grayscale');
                    }
                }
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
}