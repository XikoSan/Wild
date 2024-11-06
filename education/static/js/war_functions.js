function send_edu_troops() {
//    document.getElementById('agr_dmg').innerHTML = numberWithSpaces(data.agr_dmg);
    var dmgValue = 0;
    let dmgValue_txt = document.getElementById("def_dmg").getAttribute("data-dmg");

    if (dmgValue_txt === null) {
    } else if (dmgValue_txt === "") {
    } else {
        dmgValue = parseInt(dmgValue_txt, 10); // Преобразуем в число, если значение непустое
    }

    document.getElementById("def_dmg").setAttribute("data-dmg", sending_dmg + dmgValue);
    document.getElementById('def_dmg').innerHTML = numberWithSpaces(sending_dmg + dmgValue);


    var agr_dmgValue = 0;
    let agr_dmgValue_txt = document.getElementById("agr_dmg").getAttribute("data-dmg");

    if (agr_dmgValue_txt === null) {
    } else if (agr_dmgValue_txt === "") {
    } else {
        agr_dmgValue = parseInt(agr_dmgValue_txt, 10); // Преобразуем в число, если значение непустое
    }

    document.getElementById('delta_dmg').innerHTML = numberWithSpaces(sending_dmg + dmgValue - agr_dmgValue);

    let element = document.querySelector(".info__ava");
    let imgSrc = null;

    if (element) { // Проверяем, что элемент найден
        if (element.tagName.toLowerCase() === "img") {
            imgSrc = element.getAttribute("src");

        } else if (element.tagName.toLowerCase() === "svg") {
            imgSrc = '/static/img/nopic.svg'
        }
    }

    createDamageMessage(imgSrc, sending_dmg, false);
}

async function send_edu_enemies_1() {
    for (let i = 0; i < 5; i++) {
        let img = `/static/img/party_${Math.random() < 0.6 ? '2' : '3'}.webp`;
        let dmg_val = Math.floor(Math.random() * (2500 - 1700 + 1)) + 1700;

        let agr_dmgValue = 0;
        let agr_dmgValue_txt = document.getElementById("agr_dmg").getAttribute("data-dmg");

        if (agr_dmgValue_txt !== null && agr_dmgValue_txt !== "") {
            agr_dmgValue = parseInt(agr_dmgValue_txt, 10); // Преобразуем в число, если значение непустое
        }

        // Обновляем атрибут и содержимое элемента
        document.getElementById("agr_dmg").setAttribute("data-dmg", dmg_val + agr_dmgValue);
        document.getElementById('agr_dmg').innerHTML = numberWithSpaces(dmg_val + agr_dmgValue);

        // Создаем сообщение о повреждениях
        createDamageMessage(img, dmg_val, true);

        // Генерация случайной задержки от 300 до 800 миллисекунд
        let randomDelay = Math.random() * (800 - 300) + 300;

        var def_dmgValue = 0;
        let def_dmgValue_txt = document.getElementById("def_dmg").getAttribute("data-dmg");

        if (def_dmgValue_txt === null) {
        } else if (def_dmgValue_txt === "") {
        } else {
            def_dmgValue = parseInt(def_dmgValue_txt, 10); // Преобразуем в число, если значение непустое
        }

        document.getElementById('delta_dmg').innerHTML = numberWithSpaces(def_dmgValue - (dmg_val + agr_dmgValue));

        // Ожидаем перед следующей итерацией
        await delay(randomDelay);
    }
}

async function send_edu_enemies_2() {
    for (let i = 0; i < 10; i++) {
        let img = `/static/img/party_${Math.random() < 0.6 ? '2' : '3'}.webp`;
        let dmg_val = Math.floor(Math.random() * (3200 - 2100 + 1)) + 2100;

        let agr_dmgValue = 0;
        let agr_dmgValue_txt = document.getElementById("agr_dmg").getAttribute("data-dmg");

        if (agr_dmgValue_txt !== null && agr_dmgValue_txt !== "") {
            agr_dmgValue = parseInt(agr_dmgValue_txt, 10); // Преобразуем в число, если значение непустое
        }

        // Обновляем атрибут и содержимое элемента
        document.getElementById("agr_dmg").setAttribute("data-dmg", dmg_val + agr_dmgValue);
        document.getElementById('agr_dmg').innerHTML = numberWithSpaces(dmg_val + agr_dmgValue);

        // Создаем сообщение о повреждениях
        createDamageMessage(img, dmg_val, true);

        // Генерация случайной задержки от 300 до 800 миллисекунд
        let randomDelay = Math.random() * (800 - 300) + 300;

        var def_dmgValue = 0;
        let def_dmgValue_txt = document.getElementById("def_dmg").getAttribute("data-dmg");

        if (def_dmgValue_txt === null) {
        } else if (def_dmgValue_txt === "") {
        } else {
            def_dmgValue = parseInt(def_dmgValue_txt, 10); // Преобразуем в число, если значение непустое
        }

        document.getElementById('delta_dmg').innerHTML = numberWithSpaces(def_dmgValue - (dmg_val + agr_dmgValue));

        // Ожидаем перед следующей итерацией
        await delay(randomDelay);
    }
}

// Функция для задержки
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}