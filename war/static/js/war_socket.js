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
        createDamageMessage('img/kub.png', data.damage, data.agr_side);

        document.getElementById('agr_dmg').innerHTML = numberWithSpaces(data.agr_dmg);
        document.getElementById('def_dmg').innerHTML = numberWithSpaces(data.def_dmg);
        document.getElementById('delta_dmg').innerHTML = numberWithSpaces(parseInt(data.def_dmg) - parseInt(data.agr_dmg));
    }
};

warSocket.onclose = function(e) {
    console.log('Chat socket closed unexpectedly');
    display_modal('notify', 'Соединение прервалось', 'перезагрузите страницу, чтобы переподключиться', null, "Понятно");
};

//document.querySelector('#chat-message-submit-' + roomName).onclick = function(e) {
//    const messageInputDom = document.querySelector('#chat-message-input-' + roomName);
//    const message = messageInputDom.value;
//    if( !(message == '') && message.replace(/\s/g, '').length ){
//        warSocket.send(JSON.stringify({
//            'message': message
//        }));
//        messageInputDom.value = '';
//    }
//};

$(".sticker_img").click(function () {
    warSocket.send(JSON.stringify({
        'sticker': $(this).attr('id')
    }));
})

$(".overview__chat").on("click", ".overview__chat-message-header > h3", function(e){
    elem = $(this).closest('.overview__chat-wrapper').find(".overview__chat-controls-input")
    elem.val($(this).html() + ', ' + elem.val());
});

function sendEvent() {

    var units = {};
    $('.unit_input').each(function(i, obj) {
        units[obj.id] = obj.value;
    });

    warSocket.send(JSON.stringify({
        'units': units,
        'storage': document.getElementById('default_storage').dataset.value,
        'side': 'agr',
    }));

}