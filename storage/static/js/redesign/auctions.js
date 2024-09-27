jQuery(document).ready(function ($) {

    $('#offers_search_form').submit(function(e){
        e.preventDefault();

         var sending_data;
         sending_data += "&csrfmiddlewaretoken=" + csrftoken;
         sending_data += "&groups=" + $('#trade_groups').val();
         sending_data += "&good=" + $('#trade_goods').val();

         $.ajax({
            type: "POST",
            url: "/get_auctions/",
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

                        data.offers_list.forEach(function (line, index) {

                            var cloned_line = document.getElementById('dummy_line').cloneNode(true);

                            cloned_line.id = line['id'] + '_line';
                            cloned_line.className = 'offer_line';

                            cloned_line.onclick = function() {
                                window.location.href = '/auction/' + line['id'].toString();
                            };

                            // id оффера (что открывать в модалке?)
                            cloned_line.dataset.id = line['id'];

                            // товар
                            cloned_line.getElementsByClassName("j-t-one")[0].innerHTML = goods_names.get(line['good_name'].toString());

                            // дата создания
                            cloned_line.getElementsByClassName("j-t-two")[0].innerHTML = line['time'];

                            // герб госа
                            if(line['owner_img'] == 'None'){
                                cloned_line.getElementsByClassName("offer_gos")[0].style.display = 'none';
                                cloned_line.getElementsByClassName("offer_noimg")[0].style.display = 'inline-block';
                            }
                            else{
                                cloned_line.getElementsByClassName("offer_gos")[0].src = line['owner_img'];
                            }

                            // государство
                            cloned_line.getElementsByClassName("j-t-four")[0].innerHTML = line['owner'];

                            // количество
                            cloned_line.getElementsByClassName("j-t-five")[0].innerHTML = line['count'];

                            // цена начальная
                            cloned_line.getElementsByClassName("j-t-six")[0].innerHTML = line['price'];

                            // число лотов
                            cloned_line.getElementsByClassName("j-t-seven")[0].innerHTML = line['lot_cnt'];

                            // ставка мин
                            cloned_line.getElementsByClassName("j-t-eight")[0].innerHTML = line['price_min'];

                            // ставка макс
                            cloned_line.getElementsByClassName("j-t-nine")[0].innerHTML = line['price_max'];

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

});