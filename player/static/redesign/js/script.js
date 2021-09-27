function chk2() {

    let tab1 = document.getElementById("tab1");
    let tab2 = document.getElementById("tab2");

    let div_1 = document.getElementById("div_1");
    let div_2 = document.getElementById("div_2");


    if (tab2.hasAttribute("checked") === false && tab1.hasAttribute("checked") === true) {
        tab1.removeAttribute("checked");
        tab2.setAttribute("checked", "checked");
    }

    div_1.classList.remove("dpb");
    div_2.classList.add("dpb");

    scroll_chat();

}

function chk1() {

    let tab1 = document.getElementById("tab1");
    let tab2 = document.getElementById("tab2");

    let div_1 = document.getElementById("div_1");
    let div_2 = document.getElementById("div_2");


    if (tab1.hasAttribute("checked") === false && tab2.hasAttribute("checked") === true) {
        tab2.removeAttribute("checked");
        tab1.setAttribute("checked", "checked");
    }

    div_2.classList.remove("dpb");
    div_1.classList.add("dpb");
}

function chkPartBtn() {

    let partButtonId = document.getElementById("partButtonId");
    let eventButtonId = document.getElementById("eventButtonId");

    let partBoxId = document.getElementById("partBoxId");
    let eventBoxId = document.getElementById("eventBoxId");


    if (partButtonId.hasAttribute("checked") === false && eventButtonId.hasAttribute("checked") === true) {
        eventButtonId.removeAttribute("checked");
        partButtonId.setAttribute("checked", "checked");
    }

    partBoxId.classList.remove("panelHightNull");
    eventBoxId.classList.add("panelHightNull");

}

function chkEventBtn() {

    let partButtonId = document.getElementById("partButtonId");
    let eventButtonId = document.getElementById("eventButtonId");

    let partBoxId = document.getElementById("partBoxId");
    let eventBoxId = document.getElementById("eventBoxId");


    if (eventButtonId.hasAttribute("checked") === false && partButtonId.hasAttribute("checked") === true) {
        partButtonId.removeAttribute("checked");
        eventButtonId.setAttribute("checked", "checked");
    }

    eventBoxId.classList.remove("panelHightNull");
    partBoxId.classList.add("panelHightNull");

}


//скрипт для адаптивной высоты просматриваемой области
window.onload = function () {
    callable_countdown();
    start();
        window.onresize = start;

    function start() {
        let sizeWindow = document.documentElement.clientHeight;
        let elem = document.getElementById("wrapper");
        let px = "px";
        sizeWindow += px;
        elem.style.minHeight = sizeWindow;
    }

    // Скрипт для работы кнопки меню навигации
    let menu__button = document.querySelector("#buttonID");
    let navMenu__boxId = document.querySelector("#navMenu__boxId");
    let moveMenu = function () {
        navMenu__boxId.classList.toggle("moveBlock");
    }

    menu__button.addEventListener("click", function (e) {
        e.stopPropagation();
        moveMenu();
    });


    document.addEventListener("click", function (e) {
        let tag = e.target;
        let itIsMenu = tag == navMenu__boxId || navMenu__boxId.contains(tag);
        let itIsButton = tag == menu__button;
        let navMenu__boxId__active = navMenu__boxId.classList.contains("moveBlock");

        if (!itIsMenu && !itIsButton && navMenu__boxId__active) {
            moveMenu();
        }
    });

    
    let mainHeight = document.documentElement.clientHeight;
    let footer = document.querySelector(".footer");
    let footerHeight = footer.clientHeight;
    let tabBoxButton = document.querySelector(".tabBox__button");
    let tabBoxButtonHeight = tabBoxButton.clientHeight;
    let allHeight = (footerHeight + tabBoxButtonHeight) + footerHeight;
    let secondTabChatHeight = (mainHeight - allHeight) + "px";
    let secondTab__chat = document.querySelector(".secondTab__chat");
    secondTab__chat.style.height = secondTabChatHeight;



}

