//Блокировка чата
jQuery(document).ready(function ($) {
    $(".chat").on("click", ".message", function(e){
        e.preventDefault();

        chatSocket.send(JSON.stringify({
            'message': 'ban_chat',
            'destination': $(this).data('sender')
        }));

    });
});