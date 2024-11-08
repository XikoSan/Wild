function mine_edu_crude() {
    document.getElementById('energy').innerHTML = '0';

    document.getElementById('energy_consumption').innerHTML = '100';
    document.getElementById('daily_current_sum').innerHTML = '845';
    document.getElementById('energy_progressbar').style.width = '3.33%';
}

function mine_edu_financing() {
    const cashElement = document.getElementById("cash");
    cashElement.setAttribute("data-text", +cashElement.getAttribute("data-text") + 845);
    cashElement.innerHTML = numberWithSpaces(cashElement.getAttribute("data-text"));

    document.getElementById('energy_consumption').innerHTML = '0';
    document.getElementById('daily_current_sum').innerHTML = '0';
    document.getElementById('energy_progressbar').style.width = '0%';
}