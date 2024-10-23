$('#new_article_form').submit(function(e){
    e.preventDefault();
    var data = $(this).serialize();

    var txtfield = document.getElementById('id_text');
    if (!txtfield.value.length == 0){
        $.ajax({
            type: "POST",
            url: "/edit_article/",
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
        display_modal('notify', header_text, body_text, null, ok_text);
   };
});