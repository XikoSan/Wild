const roomName = JSON.parse(document.getElementById('room-name').textContent);
const playerId = JSON.parse(document.getElementById('player_id').textContent);

const chatSocket = new WebSocket(
    chat_conn_type + '://'
    + window.location.host
    + '/wss/dialogue/'
    + roomName
    + '/'
);


function mark_as_read() {
    // Задержка в 1 секунду
    setTimeout(function() {
        if (chatSocket.readyState === WebSocket.OPEN) {
            var elements = document.querySelectorAll('span.overview__chat-message--new');
            elements.forEach(function(element) {
                // находим сообщение - родителя
                var parent = element.closest(".overview__chat-message");
                // Выполняем нужные операции с найденным родителем
                if (parent) {
                    //  если не наше
                    if (parent.dataset.sender != playerId){
                        //      отправить в сокет сообщение, что мы его прочли
                        console.log(parent.dataset.counter);
                         chatSocket.send(JSON.stringify({
                            'message': 'was_read',
                            'counter': parent.dataset.counter
                        }));
                    }
                }
            });
        }
    }, 1000);
}


chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
//  увед о том, что сообщение прочитано
    if (data.message == 'was_read'){
        console.log('из сокета - прочитано')
        console.log(data.counter)
        var elements = document.querySelectorAll('div.overview__chat-message[data-counter="' + data.counter + '"]');
        elements.forEach(function(element) {
          console.log(element);
          console.log(element.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('span')[0]);
          element.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('span')[0].classList.remove('overview__chat-message--new');
        });
    }
//  любое другое сообщение
    else{
        var cloned_line = document.getElementById('message_blank').cloneNode(true);
        cloned_line.removeAttribute('id');
    //   если отправитель - мы
        if (data.id == playerId){
            cloned_line.classList.add("overview__chat-message--my");
        }
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
        cloned_line.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('span')[0].classList.add("overview__chat-message--new");
    //  сообщение
        cloned_line.getElementsByClassName('overview__chat-message-body')[0].getElementsByTagName('p')[0].innerHTML = data.message;

    //  вставить сообщение и показать
        document.getElementById('chat-log-' + roomName).appendChild(cloned_line);
        $(cloned_line).show();

        document.getElementById('chat-log-' + roomName).scrollTop = document.getElementById('chat-log-' + roomName).scrollHeight;

    //    если это не наше сообщение
        if (data.id != playerId){
            console.log(data.id)
            console.log(playerId)
    //      отправить в сокет сообщение, что мы его прочли
             chatSocket.send(JSON.stringify({
                'message': 'was_read',
                'counter': data.counter
            }));
        }

    }
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

$(".sticker_img").click(function () {
    chatSocket.send(JSON.stringify({
        'sticker': $(this).attr('id')
    }));
})

$(".overview__chat").on("click", ".overview__chat-message-header > h3", function(e){
    elem = $(this).closest('.overview__chat-wrapper').find(".overview__chat-controls-input")
    elem.val($(this).html() + ', ' + elem.val());
});