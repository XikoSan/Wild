let attempts = 0;
const maxAttempts = 5;
const reconnectInterval = 5000; // 5 секунд

function connectWebSocket() {
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
        else if (data.payload == 'captcha'){
            captcha_action = function() {
                sendEvent();
            };
            captcha_checking(data);
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
                display_modal('notify', 'Соединение прервалось', 'Перезагрузите страницу, чтобы переподключиться к бою', null, "Понятно");
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

function sendEvent() {
    var units = {};
    $('.unit_input').each(function(i, obj) {
        units[obj.id] = obj.value;
    });

    globWebSocket.send(JSON.stringify({
        'units': units,
        'storage': document.getElementById('default_storage').dataset.value,
        'side': $('#war_side').val(),
    }));
}
