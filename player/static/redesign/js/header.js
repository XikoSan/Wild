const modalNavButton = document.getElementById('burger');
const modalNav = document.getElementById('modal-nav');

modalNavButton.addEventListener('click', () => {
  if (modalNavButton.classList.contains('burgeractive')) {
    modalNavButton.classList.remove('burgeractive');
    modalNav.classList.remove('active');
  } else {
    modalNavButton.classList.add('burgeractive');
    modalNav.classList.add('active');
  }
})

// Tabs
function toggleTabs(tabOneClass, tabTwoClass, wrapperClass) {

  const tabOne = document.querySelector(`.${tabOneClass}`);
  const tabTwo = document.querySelector(`.${tabTwoClass}`);
  const wrapper = document.querySelector(`.${wrapperClass}`);

  tabOne.addEventListener('click', () => {
    if (tabOne.classList.contains('active')) return;
    tabOne.classList.add('active');
    if (tabTwo != null) tabTwo.classList.remove('active');
    wrapper.style.transform = 'translateX(0)'
  })

  if (tabTwo != null) {
    tabTwo.addEventListener('click', () => {
      if (tabTwo.classList.contains('active')) return;
      tabTwo.classList.add('active');
      tabOne.classList.remove('active');
      wrapper.style.transform = 'translateX(-100vw)';
    })
  }
}

if (document.querySelector('.profile__tabs-wrapper')) {
  toggleTabs(`profile__info`, `profile__repost`, `profile__tabs-wrapper`)
}

if (document.querySelector(`.store__wrapper`)) {
  toggleTabs(`ct__top-tab1`, `ct__top-tab2`, `store__wrapper`);
}

// Modal

const modal = document.querySelector('.modal');
const modalHeaderText = document.querySelector('.modal__header span')
const modalText = document.querySelector('.modal__text')
const modalOk = document.querySelector('.modal__ok')
const modalOkText = document.querySelector('.modal__ok span')
const modalCancel = document.querySelector('.modal__cancel')
const modalCancelText = document.querySelector('.modal__cancel span')

function display_modal(mode, headerText, bodyText, greenBtnText, greyBtnText) {
  modalOk.style.display = '';
  if (mode === 'notify') {
    modalOk.style.display = 'none';
  } else {
    modalOkText.textContent = greenBtnText;
  }
  modalHeaderText.textContent = headerText;
  modalText.textContent = bodyText;
  modalCancelText.textContent = greyBtnText;
  modal.classList.add('active');
}

modalOk.addEventListener('click', () => modal.classList.remove('active'))
modalCancel.addEventListener('click', () => modal.classList.remove('active'))

  // modal settings

  if (document.querySelector('.m-sett')) {
    const openMSettBtn = document.querySelector('.profile__settings')
    const closeMSettBtn = document.querySelector('.m-sett__close')
    const mSettWindow = document.querySelector('.m-sett')

    openMSettBtn.addEventListener('click', () => {
      mSettWindow.classList.add('active');
    })

    closeMSettBtn.addEventListener('click', () => {
      mSettWindow.classList.remove('active');
    })
  }