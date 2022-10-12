function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

function insertChild(newNode, parentNode) {
    parentNode.appendChild(newNode);
}

function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(args) {
    var r = parseInt(args[0])
    var g = parseInt(args[1])
    var b = parseInt(args[2])
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

jQuery(document).ready(function ($) {
    // событие выделения прав министра
    $('#minister_rights').change(function(){
        if(selected_minister !== null){

            for (i = 0; i < ministers[selected_minister]['rights'].length; i++){
                points = points + i * 2;
            }

            ministers[selected_minister]['rights'] = [];

            for (i = 0; i < $(this).val().length; i++){
                ministers[selected_minister]['rights'].push($(this).val()[i]);
                points = points - i * 2;
            }

            document.getElementById("points").innerHTML = points;
        }
    });
    // событие ввода должности
    $('#post_name').on('input', function(){
        if(selected_minister !== null){
            ministers[selected_minister]['post_name'] = $('#post_name').val();
            // отображаем в списке министров
            element = document.getElementById('minister_' + selected_minister);
            $(element).find('.post_name').html($('#post_name').val());
        }
    })
});
// сохранить список министров
function save_ministers(){
    var sending_data;
    sending_data += "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&ministers=" + JSON.stringify(ministers);
    $.ajax({
        type: "POST",
        url: "/set_ministers/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn)
            }
        }
    });
}
// назначить выбранного депутата министром
function set_minister(){
    if(selected_deputate !== null){
        var cloned_line = document.getElementById('blank_minister_line').cloneNode(true);
        cloned_line.id = 'minister_' + selected_deputate;
        cloned_line.dataset.player = selected_deputate;

        element = document.getElementById('deputate_' + selected_deputate);

        src = $(element).find('img').attr("src")
        $(cloned_line).find('img').attr("src", src);

        nickname = $(element).find('.nickname').html()
        $(cloned_line).find('.nickname').html(nickname);

        if (document.getElementById('ministers_list').lastElementChild == null){
            cloned_line.style.backgroundColor = "#f1f3f4"
        }
        else{

            color = document.getElementById('ministers_list').lastElementChild.style.backgroundColor
            rgb = color.substring(4, color.length-1)
             .replace(/ /g, '')
             .split(',');
            hex = rgbToHex(rgb)

            if (hex == "#f1f3f4"){
                cloned_line.style.backgroundColor = "#FFFFFF"
            }
            else{
                cloned_line.style.backgroundColor = "#f1f3f4"
            }
        }

        ministers[selected_deputate] = {};
        ministers[selected_deputate]['nickname'] = nickname;
        ministers[selected_deputate]['post_name'] = '';
        ministers[selected_deputate]['rights'] = [];

        points = points - 1;
        document.getElementById("points").innerHTML = points;

        cloned_line.onclick = function() {
            view_minister(event, selected_deputate);
        }

        element.remove();

        if (document.getElementById('ministers_list').lastElementChild == null){
            insertChild(cloned_line, document.getElementById('ministers_list'))
        }
        else{
            insertAfter(cloned_line, document.getElementById('ministers_list').lastElementChild);
        }
        $(cloned_line).show();
    }
}
// разжаловать выбранного министра
function unset_minister(){
    if(selected_minister !== null){
        var cloned_line = document.getElementById('blank_deputate_line').cloneNode(true);
        cloned_line.id = 'deputate_' + selected_minister;
        cloned_line.dataset.player = selected_minister;

        element = document.getElementById('minister_' + selected_minister);

        src = $(element).find('img').attr("src")
        $(cloned_line).find('img').attr("src", src);

        nickname = $(element).find('.nickname').html()
        $(cloned_line).find('.nickname').html(nickname);

        if (document.getElementById('parliament_list').lastElementChild == null){
            cloned_line.style.backgroundColor = "#f1f3f4"
        }
        else{

            color = document.getElementById('parliament_list').lastElementChild.style.backgroundColor
            rgb = color.substring(4, color.length-1)
             .replace(/ /g, '')
             .split(',');
            hex = rgbToHex(rgb)

            if (hex == "#f1f3f4"){
                cloned_line.style.backgroundColor = "#FFFFFF"
            }
            else{
                cloned_line.style.backgroundColor = "#f1f3f4"
            }
        }

        for (i = 0; i < ministers[selected_minister]['rights'].length; i++){
            points = points + i * 2;
        }

        delete ministers[selected_minister];

        points = points + 1;
        document.getElementById("points").innerHTML = points;

        cloned_line.onclick = function() {
            select_deputate(event, selected_minister);
        }

        element.remove();

        if (document.getElementById('parliament_list').lastElementChild == null){
            insertChild(cloned_line, document.getElementById('parliament_list'))
        }
        else{
            insertAfter(cloned_line, document.getElementById('parliament_list').lastElementChild);
        }
        $(cloned_line).show();
    }
}
// нажатие на депутата в списке
function select_deputate(e, deputate){

    color = e.target.style.backgroundColor
    rgb = color.substring(4, color.length-1)
     .replace(/ /g, '')
     .split(',');
    hex = rgbToHex(rgb)

    if (!(hex == "#00aa00" || e.target.dataset.player == selected_deputate )){

        unselect_row('deputate')
        selected_deputate = e.target.dataset.player
        e.target.style.backgroundColor = "#00AA00"
    }
};
// нажатие на министра в списке
function view_minister(e, minister){

    color = e.target.style.backgroundColor
    rgb = color.substring(4, color.length-1)
     .replace(/ /g, '')
     .split(',');
    hex = rgbToHex(rgb)

    if (!(hex == "#00aa00" || e.target.dataset.player == selected_minister )){

        unselect_row('minister')
        selected_minister = e.target.dataset.player
        e.target.style.backgroundColor = "#00AA00"

        unselect_rights()

        ministers[e.target.dataset.player]['rights'].forEach(function(right){
            element = document.getElementById(right);
            if (element !== null){
                element.selected = true;
            }
        });

        element = document.getElementById('post_name');
        element.value = ministers[e.target.dataset.player]['post_name']

    }
};
// удалить права у министра
function clear_rights(){
    if(selected_minister !== null){

        for (i = 0; i < ministers[selected_minister]['rights'].length; i++){
            points = points + i * 2;
        }
        ministers[selected_minister]['rights'] = [];
        document.getElementById("points").innerHTML = points;

        unselect_rights()
    }
};
// визуально очистить права перед показом новых
function unselect_rights(){
    var elements = document.getElementById("minister_rights").options;

    for(var i = 0; i < elements.length; i++){
      elements[i].selected = false;
    }
};
// снять визуальное выделение с игрока определенного списка
// mode:
// minister - центральный список
// deputate - левый список
function unselect_row(mode){

    if(mode=='minister'){
        element = document.getElementById(mode + '_' + selected_minister);
    }
    else{
        element = document.getElementById(mode + '_' + selected_deputate);
    }

    if (element !== null){

        if (element.previousElementSibling == null){
            element.style.backgroundColor = "#f1f3f4"
        }
        else{

            color = element.previousElementSibling.style.backgroundColor
            rgb = color.substring(4, color.length-1)
             .replace(/ /g, '')
             .split(',');
            hex = rgbToHex(rgb)

            if (hex == "#f1f3f4"){
                element.style.backgroundColor = "#FFFFFF"
            }
            else{
                element.style.backgroundColor = "#f1f3f4"
            }
        }

    }
};