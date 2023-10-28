class Educator {
  constructor(data) {
    this.data = data;
    this.currentPage = 0;

    this.eduWindow = document.getElementById('eduWindow');
    this.eduContent = document.getElementById('eduContent');
    this.eduRewardImg = document.getElementById('eduRewardImg');
    this.eduText = document.getElementById('eduText');
    this.eduNextBtn = document.getElementById('eduNextBtn');
    this.eduPrevBtn = document.getElementById('eduPrevBtn');
    this.eduDont = document.getElementById('eduDont');

    this.eduNextBtn.addEventListener('click', () => this.onNextClick());
    this.eduPrevBtn.addEventListener('click', () => this.onPrevClick());

    this.eduDont.addEventListener('click', () => {
      this.eduWindow.remove();
      data.onCloseEdu()
    });

    this.currentTextInterval = null;

    this.glowDivs = [];

    this.data.onEduStart();
    this.showPage(0);
  }

  showPage(num) {
    this.clearGlowDivs();
    this.showEduContent();
    
    if (!this.data.pages[num]) return;

    if (this.data.pages[num].rewardImgUrl) {
      this.eduText.style.textAlign = 'center';
      this.eduRewardImg.src = this.data.pages[num].rewardImgUrl;
      eduRewardImg.style.display = 'block';
    }
    else {
      this.eduRewardImg.src = '';
      this.eduText.style.textAlign = '';
      eduRewardImg.style.display = 'none';
    }

    this.currentPage = num;
    this.data.onEduPageChange(this.currentPage);
    this.hideBtns();
    this.printText(num, this.data.pages[num].text);
    this.showEduWindow();
  }

  showEduWindow() { this.eduWindow.style.opacity = ''; this.eduWindow.classList.add('active') };
  hideEduWindow() { this.eduWindow.style.opacity = ''; this.eduWindow.classList.remove('active') };

  hideEduContent() { this.eduContent.style.opacity = ''; this.eduContent.classList.remove('active') };
  showEduContent() { this.eduContent.style.opacity = ''; this.eduContent.classList.add('active') };

  showBtns() { this.eduNextBtn.classList.add('active'); this.eduPrevBtn.classList.add('active') }
  hideBtns() { this.eduNextBtn.classList.remove('active'); this.eduPrevBtn.classList.remove('active') }

  printText(num, text) {
    let currentSymbol = 0;
    
    this.eduText.textContent = text;
    this.eduText.style.height = '0px';
    this.eduText.style.height = this.eduText.scrollHeight + 'px';

    this.eduText.textContent = text[currentSymbol];
    this.currentTextInterval = setInterval(() => { // эффект печати
      currentSymbol++;
      this.eduText.textContent += text[currentSymbol];
      if (currentSymbol === text.length - 1) {
        this.showBtns();
        if (num === 0) this.eduPrevBtn.classList.remove('active');
        clearInterval(this.currentTextInterval);
      };
    }, 0);
  }

  createGlowDiv(width, height, left, top, isClick, el) {
    const glowDiv = document.createElement('div');
    glowDiv.classList.add('edu__glow');
    glowDiv.style.width = `${width}px`;
    glowDiv.style.height = `${height}px`;
    glowDiv.style.left = `${left}px`;
    glowDiv.style.top = `${top}px`;

    if (isClick) {
      glowDiv.classList.add('click');
      glowDiv.addEventListener('click', () => {
        this.showPage(this.currentPage + 1);
        this.clearGlowDivs();
        el.click();
      })
    }

    this.glowDivs.push(glowDiv);
    this.eduWindow.appendChild(glowDiv);
  }

  clearGlowDivs() {
    if (this.glowDivs.length > 0) {
      this.glowDivs.forEach(item => item.remove());
      this.glowDivs = [];
    }
  }

  onNextClick() {
    if (this.currentPage === this.data.pages.length - 1) { // окончание обучения
      this.data.onEduEnd();
      this.eduWindow.remove();
    }

    const awaitedElemClass = this.data.pages[this.currentPage].awaitedDomElemClass;
    const awaitedDomElems = document.querySelectorAll(`.${awaitedElemClass}`);
    const onlyGlowing = this.data.pages[this.currentPage].onlyGlowing;
    const onlyMobileInteractive = this.data.pages[this.currentPage].onlyMobileInteractive;

    if (awaitedDomElems.length > 0) { // если есть интерактивные элементы
      
      if (onlyGlowing) { //если только подсветить
        awaitedDomElems.forEach((el) => {
          const box = el.getBoundingClientRect();
          this.createGlowDiv(box.width, box.height, box.left, box.top, false );
        });
        this.hideEduContent();
        setTimeout(() => {
          this.showPage(this.currentPage + 1);
        }, 3500);
      } 
      
      else { //если ждём клика по элементам
        
        if (onlyMobileInteractive && window.screen.width > 999) {
          this.showPage(this.currentPage + 1);
        }
        
        else { //ecли только для мобилки
          awaitedDomElems.forEach((el) => {
            const box = el.getBoundingClientRect();
            this.createGlowDiv(box.width, box.height, box.left, box.top, true, el);
          });
          this.hideEduContent();
        }
      }
    } 
    
    else { // если нет интерактивного элемента
      this.showPage(this.currentPage + 1);
    }
  }

  onPrevClick() {
    if (this.currentPage === 0) return;
    this.showPage(this.currentPage - 1);
  }
}
