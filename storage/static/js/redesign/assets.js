function numberWithSpaces(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// предобработка уничтожения предметов на Складе
function destroy_pre(){
    document.getElementById('accept').disabled = true
}

// предобработка передачи со склада на склад
// показать только те склады, на которых не выбраны значения
function transfer_pre() {
    var selected_dest = null;
    storage_pos.forEach((value, key, map) => map.set(key, 0));
    document.getElementById('storage_options').disabled = false
    document.getElementById('accept').disabled = true
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
        var places_vol = parseInt($('#' + obj.name + '_places').attr('data-text'));

        total_vol += places_vol;
        storage_pos.set(obj.dataset.storage_id, storage_pos.get(obj.dataset.storage_id) + ( places_vol * 1 ) );
    });
    // считаем суммарный объем
    $('#total_vol').html(numberWithSpaces(total_vol));
    // считаем стоимость, как окр.вверх( сумма произведений объемов складов на множитель до выбранного склада-цели, минус бонус Инфраструктуры )
    var sum_vol = 0;
    sum_vol = 0;
    storage_pos.forEach((value, key, map) => {
            if( !( selected_dest.val() == 'storage_none') ){
                document.getElementById('accept').disabled = false
                if( parseInt(key) != parseInt(selected_dest.val()) ){
                    sum_vol += Math.ceil( ( map.get(key) * trans_mul[selected_dest.val()][key] ) * ( ( 100 - infr_mul[selected_dest.val()] - infr_mul[key] ) / 100 ) );

                }
            }
        }
    );
    $('#total_sum').html(numberWithSpaces( sum_vol ));
}

jQuery(document).ready(function ($) {

    $(".actives__table").on("input", ".good_input", function(e){
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

        $('#' + e.target.name + '_places' ).html(numberWithSpaces( Math.ceil(count * parseFloat(e.target.dataset.good_vol)) ));
        $('#' + e.target.name + '_places' ).attr('data-text', Math.ceil(count * parseFloat(e.target.dataset.good_vol)) );


        transfer_pre();
    });

    $('#assets_actions').on('change', function (e) {
        // скрываем все управляющие блоки
        $("#assets_actions option").each(function()
        {
            $('.' + this.value + '_bloc').each(function(i, obj) {
                console.log(obj)
                $(obj).hide();
            });
        });
        // запускаем функцию предобработки, если есть
        if (typeof window[this.value + '_pre'] === "function") {
            window[this.value + '_pre']();
        }

        $('.' + this.value + '_bloc').each(function(i, obj) {
            $(obj).show();
        });

//        $('#accept_bloc').show();
    });

    $('#storage_options').on('change', function (e) {
        transfer_pre();
    });

    $('#destroy_sure').change(function() {
        if(this.checked) {
            document.getElementById('accept').disabled = false
        }
        else{
            document.getElementById('accept').disabled = true
        }
    });

    $('#assets_actions_form').submit(function(e){
        e.preventDefault();

        for (var [key, storage] of Object.entries(send_storages_map)){
            for (var k in storage){
                delete send_storages_map[key][k];
            }
        }

        $('.good_input').each(function(i, obj) {
            if(obj.value){
               if(obj.value > 0){
                    send_storages_map[obj.dataset.storage_id][obj.dataset.stock_id] = obj.value;
              }
            }
        });

        var sending_data;

        if( $('#assets_actions').val() == 'transfer' ){

             sending_data += "&csrfmiddlewaretoken=" + csrftoken;
             sending_data += "&storages=" + JSON.stringify(send_storages_map);
             sending_data += "&dest_storage=" + $('#storage_options').val();
            $.ajax({
                type: "POST",
                url: "/assets_transfer/",
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
        }
        if( $('#assets_actions').val() == 'destroy' ){

             sending_data += "&csrfmiddlewaretoken=" + csrftoken;
             sending_data += "&storages=" + JSON.stringify(send_storages_map);
            $.ajax({
                type: "POST",
                url: "/assets_destroy/",
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
        }
    });

    $('#storages_tabs').on('change', function (e) {

        $('.actives__table').each(function(i, obj) {
            $(obj).hide();
        });

        var div = document.getElementById('table_' + this.value);

        if (div.childNodes.length === 3) {

             $.ajax({
               type: "GET",
               url: "info/assets/"+this.value,
               dataType: "html",
               cache: false,
               success: function(data){
                   div.innerHTML = data;
               }
             });

         }

        $('#table_' + this.value).show();
    });

});
