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
                    var tbodyRef = document.getElementById('lines').getElementsByTagName('tbody')[0];
                    var new_tbody = document.createElement('tbody');

                    data.offers_list.forEach(function (line, index) {
                        var newRow = new_tbody.insertRow();
                        const attrs = ['good', 'owner', 'region', 'count', 'price', 'delivery', 'sum']
                        attrs.forEach(function (item, index) {
                            var newCell = newRow.insertCell();
                            if(item == 'count'){
                                newCell.setAttribute('contenteditable', 'true');
                            }
                            var newText = document.createTextNode(line[item]);
                            newCell.appendChild(newText);
                        });
                    });
                    tbodyRef.parentNode.replaceChild(new_tbody, tbodyRef)
                    tbodyRef.remove()

                    var table = document.getElementById('lines');
                    var sort = new Tablesort(table);
                    table.style.display = 'block';
                    sort.refresh();

                    var help = document.getElementById('offers_help');
                    help.style.display = 'none';
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn)
//                    alert(data.response);
                }
            }
        });
    });
});