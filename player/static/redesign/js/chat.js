const roomName = JSON.parse(document.getElementById('room-name').textContent);
const playerId = JSON.parse(document.getElementById('player_id').textContent);

function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

//    var item_class = '';
//    var var_ban = '';
//
//    var div = document.createElement('div');
//    div.className = 'row';
//    div.innerHTML = "<div class='message" + item_class + "' data-sender='" + data.id + "'><time class='message__time'>" + data.time + var_ban + "</time><figure class='message__author-pic'><a href='/profile/" + data.id + "' target='_blank'><img src=" + data.image + " width='50px' height='50px'></a></figure><div class='message__text'><p>" + data.message + "</p></div></div>";

    var cloned_line = document.getElementById('message_line').cloneNode(true);
    cloned_line.removeAttribute('id');
    $(cloned_line.getElementsByClassName("author_link")[0]).attr('href', '/profile/' + data.id);
    $(cloned_line.getElementsByClassName("author_avatar")[0]).attr('src', data.image);
    $(cloned_line.getElementsByClassName("massage__name")[0]).attr('data-title', data.time);
    $(cloned_line.getElementsByClassName("massage__name")[0]).html(data.nickname);
    $(cloned_line.getElementsByClassName("massage__text")[0]).html(data.message);

    document.getElementById('chat-log-' + roomName).appendChild(cloned_line);
    $(cloned_line).show();

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