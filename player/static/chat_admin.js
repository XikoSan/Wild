//Блокировка чата
jQuery(document).ready(function ($) {
    $(".chat").on("click", ".message__ban", function(e){
        e.preventDefault();

        chatSocket.send(JSON.stringify({
            'message': 'ban_chat',
            'destination': $(this).parent().parent().data('sender')
        }));

    });
});