// создать склад
jQuery(document).ready(function ($) {

    $('.store__modal2-item-btns').on('click', ".up_plus", function (e) {
        if (upgrade_dict[$(this).data("good")] == 0){

            var counter = $(this).siblings(".up_count")

            if (window[counter.data("size") + '_upgrade_counter'] + 1 <= window[counter.data("size") + '_counter_limit']){

                upgrade_dict[$(this).data("good")] = upgrade_dict[$(this).data("good")] + 1
                counter.html(upgrade_dict[$(this).data("good")])

                window[counter.data("size") + '_upgrade_counter'] = window[counter.data("size") + '_upgrade_counter'] + 1;
                $('#' + counter.data("size") + '_upgrade_counter').html(window[counter.data("size") + '_upgrade_counter'])
            }
        }
    });

    $('.store__modal2-item-btns').on('click', ".up_minus", function (e) {
        if (upgrade_dict[$(this).data("good")] == 1){

            var counter = $(this).siblings(".up_count")

            if (window[counter.data("size") + '_upgrade_counter'] - 1 >= 0){

                upgrade_dict[$(this).data("good")] = upgrade_dict[$(this).data("good")] - 1
                counter.html(upgrade_dict[$(this).data("good")])

                window[counter.data("size") + '_upgrade_counter'] = window[counter.data("size") + '_upgrade_counter'] - 1;
                $('#' + counter.data("size") + '_upgrade_counter').html(window[counter.data("size") + '_upgrade_counter'])
            }

        }
    });
});

function up_storage(){
    var sending_data = "&csrfmiddlewaretoken=" + csrftoken + '&upgrades=' + JSON.stringify(upgrade_dict);
    $.ajax({
        type: "POST",
        url: "/upgrade_storage/",
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
};