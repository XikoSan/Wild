const roomName = JSON.parse(document.getElementById('room-name').textContent);
const playerId = JSON.parse(document.getElementById('player_id').textContent);

const chatSocket = new WebSocket(
    chat_conn_type + '://'
    + window.location.host
    + '/wss/chat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    var cloned_line = document.getElementById('message_blank').cloneNode(true);
    cloned_line.removeAttribute('id');
//   номер сообщ
    cloned_line.dataset.counter = data.counter;
//  отправитель
    cloned_line.dataset.sender = data.id;
//  ссылка на профиль
    cloned_line.getElementsByClassName('overview__chat-ava-link')[0].href="/profile/" + data.id;
//  аватар
    cloned_line.getElementsByClassName('overview__chat-ava-link')[0].getElementsByClassName('overview__chat-ava')[0].src = data.image;
//  никнейм
    cloned_line.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('h3')[0].innerHTML = data.nickname;
//  время
    cloned_line.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('span')[0].innerHTML = data.time;
//  сообщение
    cloned_line.getElementsByClassName('overview__chat-message-body')[0].getElementsByTagName('p')[0].innerHTML = data.message;

//  вставить сообщение и показать
    document.getElementById('chat-log-' + roomName).appendChild(cloned_line);
    $(cloned_line).show();

    document.getElementById('chat-log-' + roomName).scrollTop = document.getElementById('chat-log-' + roomName).scrollHeight;
};

chatSocket.onclose = function(e) {
    if (!e.wasClean) {
        console.log('Chat socket closed unexpectedly');
        display_modal('notify', 'Соединение прервалось', 'перезагрузите страницу, чтобы переподключиться к чату', null, "Понятно");
    }
};

document.querySelector('#chat-message-input-' + roomName).focus();
document.querySelector('#chat-message-input-' + roomName).onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit-' + roomName).click();
    }
};

document.querySelector('#chat-message-submit-' + roomName).onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input-' + roomName);
    const message = messageInputDom.value;
    if( !(message == '') && message.replace(/\s/g, '').length ){
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        messageInputDom.value = '';
    }
};

$(".sticker_img").click(function () {
    chatSocket.send(JSON.stringify({
        'sticker': $(this).attr('id')
    }));
})

$(".overview__chat").on("click", ".overview__chat-message-header > h3", function(e){
    elem = $(this).closest('.overview__chat-wrapper').find(".overview__chat-controls-input")
    elem.val($(this).html() + ', ' + elem.val());
});