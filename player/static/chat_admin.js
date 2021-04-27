//Блокировка чата
jQuery(document).ready(function ($) {
    $(".chat").on("click", ".message", function(e){
        e.preventDefault();

        chatSocket.send(JSON.stringify({
            'message': 'disconnect',
            'destination': $(this).data('sender')
        }));

    });
});