var link_stage = 0;

var linker_list = [];
var linker_pair = [];

// включаем режим редактирования связей
function start_edit(){

    poly_list.forEach(function(geojson) {
        geojson.off("click");
        geojson.on("click", function(e) {
            link_region(e.target.options.data.pk);
        });

    });
};

// выключаем режим редактирования связей
function finish_edit(){

    poly_list.forEach(function(geojson) {
        geojson.off("click");
        geojson.on("click", function(e) {
            get_district_info(e);
        });

    });
};

// выключаем режим редактирования связей
function link_region(reg_id){
    linker_pair.push(reg_id);
    console.log(linker_pair)

    if (link_stage == 0){
        link_stage = link_stage + 1;
    }
    else{
        linker_list.push(linker_pair);

        coords = [ center_dict[linker_pair[0]], center_dict[linker_pair[1]] ]
        addMarker(coords);

        linker_pair = [];
        link_stage = 0;
    }

};

// сохраняем связи
function save_links(){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&links=" + JSON.stringify(linker_list);

    $.ajax({
        beforeSend: function() {},
        type: "POST",
        url: "/save_links",
        data: sending_data,
        cache: false,
        success: function(result){
            if (result.response == 'ok'){
                display_modal('notify', 'связи регионов', 'успешно', null, 'збс');
            }
            else{
                display_modal('notify', result.header, result.response, null, result.grey_btn)
            }
        }
    });
};