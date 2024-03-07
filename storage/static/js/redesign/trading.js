function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

function fill_delivery(id, storage){
    // указываем стоимость доставки
    var delivery_sum = parseInt(offers_dict[id]['storages'][storage] * Math.ceil( $("#offer_count").val() * parseFloat(vol_map.get(offers_dict[id]['good_key']))));
    document.getElementById("offer_delivery").innerHTML = '$' + numberWithSpaces(delivery_sum);
    document.getElementById("offer_sum").innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * $("#offer_count").val());
    if (offers_dict[id]['type'] == 'sell'){
        document.getElementById("offer_total").innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * $("#offer_count").val() + delivery_sum);
    }
    else{
        document.getElementById("offer_total").innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * $("#offer_count").val() - delivery_sum);
    }
}

function fill_by_offers_dict(id){
    active_offer = id;
    // товар
    if (offers_dict[id]['type'] == 'sell'){
        document.getElementById("offer_header").innerHTML = offer_purchase_header;
        document.getElementById("offer_action").innerHTML = offer_purchase_button;
    }
    else{
        document.getElementById("offer_header").innerHTML = offer_sale_header;
        document.getElementById("offer_action").innerHTML = offer_sale_button;
    }
    // товар
    document.getElementById('offer_good').innerHTML = offers_dict[id]['good_key'];
    // владелец
    document.getElementById('offer_owner').innerHTML = offers_dict[id]['offer_own'];
    if (offers_dict[id]['owner_img'] !== null){
        document.getElementsByClassName("search-modal__withImg-pic")[0].src = offers_dict[id]['owner_img'];
        document.getElementsByClassName("search-modal__withImg-svg")[0].style.display = 'none';
        document.getElementsByClassName("search-modal__withImg-pic")[0].style.display = 'block';
    }
    else{
        document.getElementsByClassName("search-modal__withImg-svg")[0].style.display = 'block';
        document.getElementsByClassName("search-modal__withImg-pic")[0].style.display = 'none';
    }
    // цена
    document.getElementById('offer_price').innerHTML = '$' + numberWithSpaces(offers_dict[id]['price']);
    // регион
    document.getElementById('offer_region').innerHTML = offers_dict[id]['region'];
    // герб региона
    document.getElementById('region_img').src = offers_dict[id]['region_img'];
    // количество
    document.getElementById('offer_count').value = offers_dict[id]['count'];
    document.getElementById('offer_count').min = 1;
    document.getElementById('offer_count').max = offers_dict[id]['count'];
    // стоимость
    document.getElementById('offer_sum').innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * offers_dict[id]['count']);
    // склады
    for (storage in offers_dict[id]['storages']){
        if (document.getElementById("storage_" + storage).classList.contains('first_storage')){
            // возвращаем первый склад выбранным
            document.getElementById("storage_" + storage).click()
        }
    }
    // итого
    var delivery_sum = parseInt(offers_dict[id]['storages'][storage] * Math.ceil( offers_dict[id]['count'] * parseFloat(vol_map.get(offers_dict[id]['good_key']))));
    if (offers_dict[id]['type'] == 'sell'){
        document.getElementById('offer_total').innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * offers_dict[id]['count'] + delivery_sum);
    }
    else{
        document.getElementById('offer_total').innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * offers_dict[id]['count'] - delivery_sum);
    }
}

function confirm_offer(){
     var sending_data;
     sending_data += "&csrfmiddlewaretoken=" + csrftoken;
     sending_data += "&id=" + active_offer;
     sending_data += "&count=" + $("#offer_count").val();
     sending_data += "&storage=" + $("#offer_default_storage").attr('data-value');

     $.ajax({
        type: "POST",
        url: "/accept_offer/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                actualize();
                toggleActiveClass('search-buy');
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
//                    alert(data.response);
            }
        }
    });
}

function cancel_window(id){
    element = document.getElementsByClassName('modal__ok')[0]
    element.replaceWith(element.cloneNode(true));
    modalOk = document.querySelector('.modal__ok')

    if (modalOk) modalOk.addEventListener('click', () => modal.classList.remove('active'));
    modalOk.addEventListener('click', () => cancel_offer(id));

    display_modal('ask', offer_cancel_header, offer_cancel_text, offer_cancel_yes, offer_cancel_cancel)
}

function cancel_offer(id){
     var sending_data;
     sending_data += "&csrfmiddlewaretoken=" + csrftoken;
     sending_data += "&id=" + id;

     $.ajax({
        type: "POST",
        url: "/cancel_offer/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                document.getElementById(id + '_line').remove();
                actualize();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
}

jQuery(document).ready(function ($) {


    $('#trade_groups').change(function(e) {

        // скрываем все товары из вариантов
        $("#trade_goods option").each(function()
        {
            $(this).hide();
        });
        $('#good_default').show();
        $('#trade_goods').val('null');
        document.getElementById('trade_goods').dispatchEvent(new Event('change'));

        var selected = $(e.target).val();
        for (good in groups_n_goods[selected]){
            $('#good_' + good ).show();
        }

        if (selected != 'default' && selected != null){
            document.getElementById('searchBtn').removeAttribute("disabled");
        }
        else{
            document.getElementById('searchBtn').setAttribute("disabled", 'true');
        }
    });

//    $('#trade_goods').change(function(e) {
//        var selected = $(e.target).val();
//    });

    $('#trade_owner').change(function(e) {
        var selected = $(e.target).val();

        if (selected == 'mine'){
            document.getElementById('searchBtn').removeAttribute("disabled");
        }
        else{
            document.getElementById('searchBtn').setAttribute("disabled", 'true');
        }
    });

    $('#offers_search_form').submit(function(e){
        e.preventDefault();

         var sending_data;
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;
         sending_data += "&action=" + $('#trade_actions').val();
         sending_data += "&range=" + $('#trade_range').val();
         sending_data += "&owner=" + $('#trade_owner').val();
         sending_data += "&groups=" + $('#trade_groups').val();
         sending_data += "&good=" + $('#trade_goods').val();

         $.ajax({
            type: "POST",
            url: "/get_offers/",
            data:  sending_data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    last_item = 'offers_header';
                    document.getElementById('lines').style.display = 'none';
                    // удаляем старые строки
                    var elements = document.getElementsByClassName("offer_line")
                    while(elements.length > 0){
                        elements[0].parentNode.removeChild(elements[0]);
                    }

                    if (Object.keys(data.offers_list).length > 0){
                        offers_dict = {};
                        data.offers_list.forEach(function (line, index) {
                            offers_dict[line['id']] = {};
                            // тип: покупка или продажа
                            offers_dict[line['id']]['type'] = line['type'];
                            // склады
                            offers_dict[line['id']]['storages'] = {}
                            for (var key in line['delivery']){
                                offers_dict[line['id']]['storages'][key] = line['delivery'][key]['single'];

                            }


                            var cloned_line = document.getElementById('dummy_line').cloneNode(true);

                            // если это собственное предложение - другой обработчик
                            if (line['own_offer'] == true){
                                cloned_line.removeAttribute("onclick");
                                let num = String(line['id'])
                                cloned_line.addEventListener('click', () => cancel_window(parseInt(num)));
                            }

                            cloned_line.id = line['id'] + '_line';
                            cloned_line.className = 'offer_line';
                            // id оффера (что открывать в модалке?)
                            cloned_line.dataset.id = line['id'];
                            // товар
                            offers_dict[line['id']]['good'] = line['good'];
                            offers_dict[line['id']]['good_key'] = line['good_name'];
                            cloned_line.getElementsByClassName("j-t-one")[0].innerHTML = line['good_name'];
                            // герб региона
                            cloned_line.getElementsByClassName("offer_reg")[0].src = 'static/img/regions/' + line['region_img'] + '.png';
                            offers_dict[line['id']]['region_img'] = cloned_line.getElementsByClassName("offer_reg")[0].src;
                            // регион
                            offers_dict[line['id']]['region'] = line['region'];
                            // количество
                            offers_dict[line['id']]['count'] = line['count'];
                            cloned_line.getElementsByClassName("j-t-three")[0].innerHTML = line['count'];
                            // цена
                            cloned_line.getElementsByClassName("j-t-four")[0].innerHTML = line['price'];
                            offers_dict[line['id']]['price'] = line['price'];
                            // аватар владельца
                            if(line['owner_img'] == 'None'){
                                cloned_line.getElementsByClassName("offer_own")[0].style.display = 'none';
                                cloned_line.getElementsByClassName("offer_noimg")[0].style.display = 'inline-block';
                                offers_dict[line['id']]['owner_img'] = null;
                            }
                            else{
                                cloned_line.getElementsByClassName("offer_own")[0].src = line['owner_img'];
                                offers_dict[line['id']]['owner_img'] = line['owner_img'];
                            }
                            // владелец
                            cloned_line.getElementsByClassName("j-t-six")[0].innerHTML = line['owner'];
                            offers_dict[line['id']]['offer_own'] = line['owner'];
                            // id оффера (что открывать в модалке?)
//                            cloned_line.getElementsByClassName("j-t-five")[0].dataset.id = line['id'];

                            previous_line = document.getElementById(last_item);
                            insertAfter(cloned_line, previous_line);

                            last_item = cloned_line.id;

                            $('#' + last_item).show();
                        });

                        var table = document.getElementById('lines');
                        table.style.display = 'table';
                        document.getElementsByClassName("trading__actveFilters")[0].className += ' active';

                        document.getElementById('offers_help').style.display = 'none';
                        document.getElementById('offers_none').style.display = 'none';
                    }
                    else{
                        document.getElementById('offers_help').style.display = 'none';
                        document.getElementById('offers_none').style.display = 'block';
                    }
                    closeSearchSettingsModal();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
//                    alert(data.response);
                }
            }
        });
    });

    // ввод числа в торговле
    $("#offer_count").on('input', function (e) {
        id = active_offer;
        storage = $("#offer_default_storage").attr('data-value');

        var delivery_sum = parseInt(offers_dict[id]['storages'][storage] * Math.ceil( $("#offer_count").val() * parseFloat(vol_map.get(offers_dict[id]['good_key']))));
        document.getElementById("offer_delivery").innerHTML = '$' + numberWithSpaces(delivery_sum);
        document.getElementById("offer_sum").innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * $("#offer_count").val());
        if (offers_dict[id]['type'] == 'sell'){
            document.getElementById("offer_total").innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * $("#offer_count").val() + delivery_sum);
        }
        else{
            document.getElementById("offer_total").innerHTML = '$' + numberWithSpaces(offers_dict[id]['price'] * $("#offer_count").val() - delivery_sum);
        }
    });
});