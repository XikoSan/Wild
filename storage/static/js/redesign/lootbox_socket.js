let attempts = 0;
const maxAttempts = 5;
const reconnectInterval = 5000; // 5 секунд

function connectWebSocket() {
    const warSocket = new WebSocket(
        chat_conn_type + '://'
        + window.location.host
        + '/wss/lootboxes/'
    );

    warSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        console.log(data);

        if(data.type == 'win'){
            createDamageMessage('/static/img/nopic.svg', data.reward, false);

        }
        else if (data.type == 'purchase'){
            document.getElementById('jackpot_sum').innerHTML = numberWithSpaces(data.value);
        }
    };

    warSocket.onclose = function(e) {
        if (!e.wasClean) {
            console.log('Chat socket closed unexpectedly');
            if (attempts < maxAttempts) {
                attempts++;
                console.log(`Reconnect attempt ${attempts}...`);
                // После переподключения обновляем globWebSocket
                setTimeout(() => {
                    globWebSocket = connectWebSocket();
                }, reconnectInterval);
            } else {
                display_modal('notify', 'Соединение прервалось', 'Перезагрузите страницу, чтобы переподключиться', null, "Понятно");
            }
        }
    };

    warSocket.onerror = function(error) {
        console.log('WebSocket error:', error);
        warSocket.close();
    };

    warSocket.onopen = function () {
        console.log('WebSocket connection established.');
        // Если соединение установлено, сбрасываем попытки
        attempts = 0;
    };

    return warSocket;
}

// Запуск первой попытки подключения
let globWebSocket = connectWebSocket();
