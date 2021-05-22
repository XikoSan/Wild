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
                    document.getElementById('lines').style.display = 'none';

                    if (Object.keys(data.offers_list).length > 0){
                        var tbodyRef = document.getElementById('lines').getElementsByTagName('tbody')[0];
                        var new_tbody = document.createElement('tbody');

                        data.offers_list.forEach(function (line, index) {
                            var newRow = new_tbody.insertRow();
                            const attrs = ['good', 'owner', 'region', 'count', 'price', 'delivery', 'sum']
                            attrs.forEach(function (item, index) {
                                var newCell = newRow.insertCell();
                                if(item == 'count'){
                                    newCell.setAttribute('contenteditable', 'true');
                                    newCell.style.border = "thin solid black";
                                }
                                newCell.classList.add(item);

                                if(item == 'delivery'){
                                    var select = document.createElement('select');
                                    select.classList.add('destination');

                                    for (var [k, v] in line[item]){
                                        var option = document.createElement('option');

                                        option.setAttribute('value', k)
                                        console.log(line[item])
                                        console.log(k)
                                        option.dataset.delivery = line[item][k]['delivery'];

                                        option.innerHTML = line[item][k]['name'] + ': $' + numberWithSpaces(line[item][k]['delivery'])
                                        select.appendChild(option);
                                    }

                                    newCell.appendChild(select);
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

    $("#lines").on("input", ".count", function(e){
        if (!isNaN(parseInt(e.target.innerHTML))){
            droplist = e.currentTarget.parentElement.getElementsByClassName("delivery")[0].getElementsByClassName('destination')[0];
            $($(e.currentTarget).parent()).find(".sum").html( ( parseInt($($(e.currentTarget).parent()).find(".price").html()) * parseInt(e.target.innerHTML) ) + parseInt(droplist.selectedOptions[0].dataset.delivery) )
        }
    });

    $("#lines").on("input", ".destination", function(e){
        if (!isNaN(parseInt(e.target.parentElement.parentElement.getElementsByClassName("count")[0].innerHTML))){
            droplist = e.currentTarget;
            $($($(e.currentTarget).parent()).parent()).find(".sum").html( ( parseInt($($($(e.currentTarget).parent()).parent()).find(".price").html()) * parseInt(parseInt(e.target.parentElement.parentElement.getElementsByClassName("count")[0].innerHTML)) ) + parseInt(droplist.selectedOptions[0].dataset.delivery) )
        }
    });


});