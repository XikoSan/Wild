const warSocket = new WebSocket(
    chat_conn_type + '://'
    + window.location.host
    + '/wss/war/'
    + war_type
    + '/'
    + war_id
    + '/'
);

warSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if(data.payload == 'error'){
        display_modal('notify', data.header, data.response, null, data.grey_btn);

    }
    else{
        actualize();
        createDamageMessage(data.image_url, data.damage, data.agr_side);

        document.getElementById('agr_dmg').innerHTML = numberWithSpaces(data.agr_dmg);
        document.getElementById('def_dmg').innerHTML = numberWithSpaces(data.def_dmg);
        document.getElementById('delta_dmg').innerHTML = numberWithSpaces(parseInt(data.def_dmg) + defence_points - parseInt(data.agr_dmg));
    }
};

warSocket.onclose = function(e) {
    console.log('Chat socket closed unexpectedly');
    display_modal('notify', 'Соединение прервалось', 'перезагрузите страницу, чтобы переподключиться', null, "Понятно");
};

function sendEvent() {

    var units = {};
    $('.unit_input').each(function(i, obj) {
        units[obj.id] = obj.value;
    });

    warSocket.send(JSON.stringify({
        'units': units,
        'storage': document.getElementById('default_storage').dataset.value,
        'side': $('#war_side').val(),
    }));

}