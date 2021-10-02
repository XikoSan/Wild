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

    var item_class = '';
    var var_ban = '';
    if(data.id == playerId){
        item_class = ' message--user-2';
    }
    else{
        item_class = ' message--user-1';
        if(typeof ban_button !== 'undefined'){
            var_ban = ban_button;
        }
    }

    var div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = "<div class='message" + item_class + "' data-sender='" + data.id + "'><time class='message__time'>" + data.time + var_ban + "</time><figure class='message__author-pic'><a href='/profile/" + data.id + "' target='_blank'><img src=" + data.image + " width='50px' height='50px'></a></figure><div class='message__text'><p>" + data.message + "</p></div></div>";
    document.getElementById('chat-log-' + roomName).appendChild(div);

    document.getElementById('chat-log-' + roomName).scrollTop = document.getElementById('chat-log-' + roomName).scrollHeight;
};

chatSocket.onclose = function(e) {
    console.log('Chat socket closed unexpectedly');
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