glowDivs = [];
eduWindow = document.getElementById('eduWindow');
eduRewardImg = document.getElementById('eduRewardImg');
eduText = document.getElementById('eduText');

eduContent = document.getElementById('eduContent');
eduNextBtn = document.getElementById('eduNextBtn');
eduPrevBtn = document.getElementById('eduPrevBtn');
eduDont = document.getElementById('eduDont');

var typing = false;

function printText(text) {
    typing = true;

    let currentSymbol = 0;

    eduText.textContent = text;
    eduText.style.height = '0px';
    eduText.style.height = eduText.scrollHeight + 'px';

    eduText.textContent = text[currentSymbol];
    currentTextInterval = setInterval(() => { // эффект печати
      currentSymbol++;
      eduText.textContent += text[currentSymbol];
      if (currentSymbol === text.length - 1) {

        eduNextBtn.classList.add('active');
        eduPrevBtn.classList.add('active');
        eduDont.classList.add('active');
        eduNextBtn.disabled = false;
        eduPrevBtn.disabled = false;
        eduDont.remove() ;

        eduPrevBtn.classList.remove('active');
        eduPrevBtn.disabled = true;

        clearInterval(currentTextInterval);
        typing = false;
      };
    }, 1);
}

function showHelp(id) {
  eduRewardImg.src = '';
  eduText.style.textAlign = '';
  eduRewardImg.style.display = 'none';

  eduContent.style.opacity = '';
  eduContent.classList.add('active')

  eduNextBtn.addEventListener('click', () => {
      eduContent.style.opacity = '';
      eduContent.classList.remove('active')
  });

  var text = ((help_text[id] == null) ? help_text['no_data'] : help_text[id]);

  printText(text);
}

function clearGlowDivs() {
    if (glowDivs.length > 0) {
      glowDivs.forEach(item => item.remove());
      glowDivs = [];
    }
}

function createGlowDiv(width, height, left, top, el) {
    const glowDiv = document.createElement('div');
    glowDiv.classList.add('edu__glow');
    glowDiv.style.width = `${width}px`;
    glowDiv.style.height = `${height}px`;
    glowDiv.style.left = `${left}px`;
    glowDiv.style.top = `${top}px`;

    glowDiv.classList.add('click');
    glowDiv.addEventListener('click', () => {
        if (typing == false){
            showHelp(el.dataset.helpid);
        }
    })

    glowDivs.push(glowDiv);
    eduWindow.appendChild(glowDiv);
  }

function show_gui_help() {
    eduWindow.style.opacity = '';
    eduWindow.classList.add('active')

    document.getElementById('hide_gui_help').style.display = 'block';

    const awaitedDomElems = document.querySelectorAll(`.${'gui_help'}`);

      awaitedDomElems.forEach((el) => {
        const box = el.getBoundingClientRect();
        createGlowDiv(box.width, box.height, box.left, box.top, el);
      });
}

function hide_gui_help() {
    eduContent.style.opacity = '';
    eduContent.classList.remove('active')
    eduWindow.style.opacity = '';
    eduWindow.classList.remove('active')
}

function run_gui_help(){
    const modalNavButton = document.getElementById('burger');
    modalNavButton.classList.remove('burgeractive');

    const modalNav = document.getElementById('modal-nav');
    modalNav.classList.remove('active');

    show_gui_help();
}