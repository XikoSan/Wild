function numberWithSpaces(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// предобработка передачи со склада на склад
// показать только те склады, на которых не выбраны значения
function transfer_pre() {
    var selected_dest = null;
    storage_pos.forEach((value, key, map) => map.set(key, 0));
    // показываем все склады сначала
    $("#storage_options option").each(function()
    {
        $(this).show();
        if($(this).is(":selected")){
            selected_dest = $(this);
        }
    });
    // скрываем склады, в которых выбран товар
    // а также собираем данные об объёме
    var total_vol = 0;
    $('.good_input').each(function(i, obj) {
        if(obj.value){
           if(obj.value > 0){
                if($('#storage_' + obj.dataset.storage_id ).is(":selected")){
                    $('#storage_options').val('storage_none');
                        $("#storage_options option").each(function()
                        {
                            if($(this).is(":selected")){
                                selected_dest = $(this);
                            }
                        });
                }
                $('#storage_' + obj.dataset.storage_id ).hide();
           }
        }
        if(obj.dataset.good_name != 'station'){
            var places_vol = parseInt($('#' + obj.dataset.storage_id + '_' + obj.dataset.good_name + '_places').attr('data-text'));

            total_vol += places_vol;
            storage_pos.set(obj.dataset.storage_id, storage_pos.get(obj.dataset.storage_id) + ( places_vol * 1 ) );
        }
    });
    // считаем суммарный объем
    $('#total_vol').html(numberWithSpaces(total_vol));
    // считаем стоимость, как сумма произведений объемов складов на множитель до выбранного склада-цели
    var sum_vol = 0;
    sum_vol = 0;
    console.log('selected_dest.val() = ' + selected_dest.val());
    storage_pos.forEach((value, key, map) => {
            if( !( selected_dest.val() == 'storage_none') ){
                if( parseInt(key) != parseInt(selected_dest.val()) ){
                    sum_vol += map.get(key) * trans_mul[selected_dest.val()][key];

                }
            }
        }
    );
    console.log('sum_vol = ' + sum_vol);
    $('#total_sum').html(numberWithSpaces( sum_vol ));
}

jQuery(document).ready(function ($) {

    $(".tab-content").on("input", ".good_input", function(e){
        var count = 0;

        if(parseInt($(this).attr('max')) < e.target.value){
            count = parseInt($(this).attr('max'));
        }
        else if($(this).attr('min') > e.target.value){
            count = parseInt($(this).attr('min'));
        }
        else{
            count = e.target.value;
        }

        $('#' + e.target.name + '_places' ).html( Math.ceil(count * parseFloat(vol_map.get(e.target.dataset.good_name))) );
        $('#' + e.target.name + '_places' ).attr('data-text', Math.ceil(count * parseFloat(vol_map.get(e.target.dataset.good_name))) );


        transfer_pre();
    });

    $('#assets_actions').on('change', function (e) {
        // скрываем все управляющие блоки
        $("#assets_actions option").each(function()
        {
            $('#' + this.value + '_bloc').hide()
        });
        // запускаем функцию предобработки, если есть
        if (typeof window[this.value + '_pre'] === "function") {
            window[this.value + '_pre']();
        }

        $('#' + this.value + '_bloc').show();
        $('#accept_bloc').show();
    });

    $('#storage_options').on('change', function (e) {
        transfer_pre();
    });
});
