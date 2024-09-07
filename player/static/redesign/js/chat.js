const roomName = JSON.parse(document.getElementById('room-name').textContent);
const playerId = JSON.parse(document.getElementById('player_id').textContent);

let attempts = 0;
const maxAttempts = 5;
const reconnectInterval = 5000; // 5 секунд

function connectWebSocket() {
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
        // Номер сообщения
        cloned_line.dataset.counter = data.counter;
        // Отправитель
        cloned_line.dataset.sender = data.id;
        // Ссылка на профиль
        cloned_line.getElementsByClassName('overview__chat-ava-link')[0].href = "/profile/" + data.id;
        // Аватар
        cloned_line.getElementsByClassName('overview__chat-ava-link')[0].getElementsByClassName('overview__chat-ava')[0].src = data.image;
        // Никнейм
        cloned_line.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('h3')[0].innerHTML = data.nickname;
        // Время
        cloned_line.getElementsByClassName('overview__chat-message-header')[0].getElementsByTagName('span')[0].innerHTML = data.time;
        // Сообщение
        cloned_line.getElementsByClassName('overview__chat-message-body')[0].getElementsByTagName('p')[0].innerHTML = data.message;

        // Вставить сообщение и показать
        document.getElementById('chat-log-' + roomName).appendChild(cloned_line);
        $(cloned_line).show();

        document.getElementById('chat-log-' + roomName).scrollTop = document.getElementById('chat-log-' + roomName).scrollHeight;
    };

    chatSocket.onclose = function(e) {
        if (!e.wasClean) {
            console.log('Chat socket closed unexpectedly');
            if (attempts < maxAttempts) {
                attempts++;
                console.log(`Reconnect attempt ${attempts}...`);
                setTimeout(connectWebSocket, reconnectInterval); // Повторная попытка через 10 секунд
            } else {
                display_modal('notify', 'Соединение прервалось', 'Перезагрузите страницу, чтобы переподключиться к чату', null, "Понятно");
            }
        }
    };

    chatSocket.onerror = function(error) {
        console.log('WebSocket error:', error);
        chatSocket.close();
    };

    chatSocket.onopen = function () {
        console.log('WebSocket connection established.');
        // Если соединение установлено, сбрасываем попытки
        attempts = 0;
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
        if (!(message == '') && message.replace(/\s/g, '').length) {
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
    });

    $(".overview__chat").on("click", ".overview__chat-message-header > h3", function(e){
        elem = $(this).closest('.overview__chat-wrapper').find(".overview__chat-controls-input")
        elem.val($(this).html() + ', ' + elem.val());
    });

    $(".overview__chat-messages").on("click", ".message__ban", function(e){
        chatSocket.send(JSON.stringify({
            'message': 'ban_chat',
            'destination': $(this).parent().parent().parent().parent().data('sender')
        }));

    });

    $(".overview__chat-messages").on("click", ".message__delete", function(e){
        chatSocket.send(JSON.stringify({
            'message': 'delete_message',
            'counter': $(this).parent().parent().parent().parent().data('counter')
        }));
        $(this).parent().parent().parent().parent().remove();
    });
}

// Запуск первой попытки подключения
connectWebSocket();
