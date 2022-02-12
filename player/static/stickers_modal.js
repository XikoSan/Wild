var span = document.querySelectorAll('.stickers_bar');
console.log(span);
for (var i = span.length; i--;) {
    (function () {
        var t;
        span[i].onmouseover = function () {
            hideAll();
            clearTimeout(t);
            this.className = 'stickers_advice';
        };
        span[i].onmouseout = function () {
            var self = this;
            t = setTimeout(function () {
                self.className = 'stickers_bar';
            }, 300);
        };
    })();
}

function hideAll() {
    for (var i = span.length; i--;) {
        span[i].className = 'stickers_bar';
    }
};