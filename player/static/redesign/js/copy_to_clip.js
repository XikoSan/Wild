const profileTopWrapper = document.querySelector('.profile__top-wrapper');
const profileInfoTab = document.querySelector('.profile__info-tab');

function hideProfileTop() {
    if (window.innerWidth < 1200) {
        profileTopWrapper.classList.add('hidden');
        profileInfoTab.scrollTop(9999);
    }
}
function showProfileTop() {
    if (window.innerWidth < 1200) {
        profileTopWrapper.classList.remove('hidden');
    }
}

class IdCopy {
    constructor(text) {
        this.text = text;

        this.button = document.getElementById('profile__id');
        this.timerForActiveClass = null;
        this.isCopyBlocked = false;

        this.button.addEventListener('click', () => {
            if (this.isCopyBlocked) return;
            this.mainAction(this.text);
        })
    }

    mainAction(text) {
        const textArea = document.createElement("textarea");
        textArea.style.position = 'fixed';
        textArea.style.top = 0;
        textArea.style.left = 0;
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = 0;
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            var successful = document.execCommand('copy');
            this.isCopyBlocked = true;
            this.button.classList.add('active');
            this.timerForActiveClass = setTimeout(() => {
                this.isCopyBlocked = false;
                this.button.classList.remove('active')
            }, 1000);
        } catch (err) {
            console.log('Oops, unable to copy');
        }
        document.body.removeChild(textArea);
    }
}
