// энергетики
jQuery(document).ready(function ($) {
    var range = document.getElementById('energy_range');
    var field = document.getElementById('energy_field');

    field.value = range.value;
    if(range.value == 0 || range.value == ""){
        $('#gold_cost').html(0);
    }
    else if(range.value / 10 < 1){
        $('#gold_cost').html(1);
    }
    else{
        $('#gold_cost').html(numberWithSpaces(range.value / 10));
    }

    range.addEventListener('input', function (e) {
        field.value = e.target.value;

        if(e.target.value == 0 || e.target.value == ""){
            $('#gold_cost').html(0);
        }
        else if((e.target.value / 10) < 1){
            $('#gold_cost').html(1);
        }
        else{
            $('#gold_cost').html(numberWithSpaces(e.target.value / 10));
        }
        $('#gold_cost').html(numberWithSpaces(e.target.value / 10));
    });
    field.addEventListener('input', function (e) {
        range.value = e.target.value;

        if(e.target.value == 0 || e.target.value == ""){
            $('#gold_cost').html(0);
        }
        else if((e.target.value / 10) < 1){
            $('#gold_cost').html(1);
        }
        else{
            $('#gold_cost').html(numberWithSpaces(e.target.value / 10));
        }
    });

    $('#produce_energy_form').submit(function(e){
        e.preventDefault();
        var sending_data = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "/produce_energy/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    $('#bottles').html(numberWithSpaces(data.bottles));
                    $('#gold').html(numberWithSpaces(data.gold));

                    var gold = parseInt(data.gold);
                    var max_gold = gold * 10;
                    var min_gold = 0;

                    if(gold == 0){
                        min_gold = 0;
                    }
                    else{
                        min_gold = 10;
                    }

                    document.getElementById('energy_range').setAttribute("min", min_gold);
                    document.getElementById('energy_range').setAttribute("max", max_gold);
                    document.getElementById('energy_range').value = min_gold;

                    document.getElementById('energy_field').setAttribute("min", min_gold);
                    document.getElementById('energy_field').setAttribute("max", max_gold);
                    document.getElementById('energy_field').value = min_gold;

                    $('#energy_range_min').html(numberWithSpaces(min_gold));
                    $('#energy_range_max').html(numberWithSpaces(max_gold));
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
//                     alert(data.response);
                }
            }
        });
    });
});
//wild pass - проверка
function check_card(){
    $('#InfoModal').find(".modal-green").on( "click", use_card);

    display_modal('ask', move_header, move_text, move_yes, move_cancel)
};
//wild pass - использование
function use_card(){
    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    $.ajax({
        type: "POST",
        url: "/use_card/",
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