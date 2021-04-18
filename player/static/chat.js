const roomName = JSON.parse(document.getElementById('room-name').textContent);
const playerId = JSON.parse(document.getElementById('player_id').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    var item_class = '';
    if(data.id == playerId){
        item_class = ' chat__item--responder';
    }

    var div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = "<div class='chat__item" + item_class + "'><img src='" + data.image + "' width='50px' height='50px' class='chat__person-avatar'><div class='chat__messages'><div class='chat__message'><div class='chat__message-time'>" + data.time + "</div><div class='chat__message-content'>" + data.message + "</div></div></div></div>";
    document.getElementById('chat-log-' + roomName).appendChild(div);

    document.getElementById('chat-log-' + roomName).scrollTop = document.getElementById('chat-log-' + roomName).scrollHeight;
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
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