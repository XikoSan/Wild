$('#new_article_form').submit(function(e){
    e.preventDefault();
    var data = $(this).serialize();

    var txtfield = document.getElementById('id_text');
    if (!txtfield.value.length == 0){
        $.ajax({
            type: "POST",
            url: "/create_article/",
            data: data,
            cache: false,
            success: function(data){
                if (data.response == 'ok'){
                    //открываем страницу статьи с id из отвтета
                    window.location = '/article/' + data.id;
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn);
                }
            }
       });
   }
   else{
        display_modal('notify', 'Новая статья', 'Статья не может быть пустой', null, 'Хорошо');
   };
});