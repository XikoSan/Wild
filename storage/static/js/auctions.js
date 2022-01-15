jQuery(document).ready(function ($) {
    $('#trade_groups').change(function(e) {
        // скрываем все товары из вариантов
        $("#trade_goods option").each(function()
        {
            $(this).hide();
        });
        $('#trade_goods').val('default');

        var selected = $(e.target).val();
        for (var [k, v] in selected){
            for (good in groups_n_goods[selected[k]]){
                $('#good_' + good ).show();

            }
        }
    });

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
                    document.getElementById('lines').style.display = 'none';
                    if (Object.keys(data.offers_list).length > 0){
                        var tbodyRef = document.getElementById('lines').getElementsByTagName('tbody')[0];
                        var new_tbody = document.createElement('tbody');

                        data.offers_list.forEach(function (line, index) {

                            var newRow = new_tbody.insertRow();
//                            const attrs = ['good', 'owner', 'count', 'price', 'delivery', 'sum', 'type']
                            const attrs = ['good', 'time', 'owner', 'count', 'price', 'lot_cnt', 'price_min', 'price_max', 'id']
                            attrs.forEach(function (item, index) {
                                var newCell = newRow.insertCell();

                                if(item == 'good'){
                                    newCell.dataset.name = line['good_name'];
                                }

                                if(item == 'id'){
                                    var button = document.createElement("button");
                                    button.id = line[item];
                                    button.innerHTML = 'Перейти';

                                    newCell.appendChild(button);
                                    button.setAttribute("onclick", "location.href='/auction/" + line[item] + "'")
                                }
                                else if(item == 'count' || item == 'price_min' || item == 'price_max'){
                                    var newText = document.createTextNode(numberWithSpaces(line[item]));
                                    newCell.appendChild(newText);
                                }
                                else{
                                    var newText = document.createTextNode(line[item]);
                                    newCell.appendChild(newText);
                                }

                            });
                        });
                        tbodyRef.parentNode.replaceChild(new_tbody, tbodyRef)
                        tbodyRef.remove()

                        var table = document.getElementById('lines');
                        var sort = new Tablesort(table);
                        table.style.display = 'block';
                        sort.refresh();

                        document.getElementById('offers_help').style.display = 'none';
                        document.getElementById('offers_none').style.display = 'none';
                    }
                    else{
                        document.getElementById('offers_help').style.display = 'none';
                        document.getElementById('offers_none').style.display = 'block';
                    }

                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
//                    alert(data.response);
                }
            }
        });
    });

});