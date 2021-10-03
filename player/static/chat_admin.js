//Блокировка чата
jQuery(document).ready(function ($) {
    $(".chat").on("click", ".message__ban", function(e){
        e.preventDefault();

        chatSocket.send(JSON.stringify({
            'message': 'ban_chat',
            'destination': $(this).parent().parent().data('sender')
        }));

    });
    $(".chat").on("click", ".message__delete", function(e){
        e.preventDefault();

        chatSocket.send(JSON.stringify({
            'message': 'delete_message',
            'counter': $(this).parent().parent().data('counter')
        }));
        $(this).parent().parent().parent().remove();
    });
});