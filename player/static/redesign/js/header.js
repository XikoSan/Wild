/* common func */

function openModalByAddClass(selector) {
  document.querySelector(selector).classList.add('active')
}
function closeModalByRemoveClass(selector) {
  document.querySelector(selector).classList.remove('active')
}

function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}


const modalNavButton = document.getElementById('burger');
const modalNav = document.getElementById('modal-nav');

modalNavButton.addEventListener('click', () => {
  if (modalNavButton.classList.contains('burgeractive')) {
    modalNavButton.classList.remove('burgeractive');
    modalNav.classList.remove('active');
    const wrp = document.querySelector('.overview__wrapper');
    if (wrp) {
      wrp.style.display = 'none';
      setTimeout(() => wrp.style.display = '', 10);
    }
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
var modalOk = document.querySelector('.modal__ok')
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

if (modalOk) modalOk.addEventListener('click', () => modal.classList.remove('active'));
if (modalCancel) modalCancel.addEventListener('click', () => modal.classList.remove('active'));

// Cropper
var cropper;

function initCropper(fileInputId, imgId) {

  $(function () {

    /* SCRIPT TO OPEN THE MODAL WITH THE PREVIEW */
      document.getElementById(fileInputId).addEventListener('change', function () {
      if (this.files && this.files[0]) {
        let reader = new FileReader();
        reader.onload = function (e) {
          document.getElementById(imgId).setAttribute("src", e.target.result);
          document.getElementById('modalCrop').classList.add('active');

          let image = document.getElementById(imgId);
          cropper = new Cropper(image, {
            aspectRatio: 1,
            cropBoxResizable: false,
            minContainerHeight: 200,
            minCanvasHeight: 200,
            minCropBoxWidth: 200,
            minCropBoxHeight: 200,
            crop(event) {
              console.log(event.detail.x);
              console.log(event.detail.y);
              console.log(event.detail.width);
              console.log(event.detail.height);
              console.log(event.detail.rotate);
              console.log(event.detail.scaleX);
              console.log(event.detail.scaleY);
            },
          });
          console.log(cropper);

          //document.querySelector('.js-pic-up').click();
        }
        reader.readAsDataURL(this.files[0]);
      }
    });

    /* SCRIPTS TO HANDLE THE CROPPER BOX */
    let cropBoxData;
    let canvasData;

    $("#crop-close").click( function () {
      document.getElementById('modalCrop').classList.remove('active');
      cropBoxData = cropper.getCropBoxData();
      canvasData = cropper.getCanvasData();
      cropper.destroy();
      }
    );

    $(".back-crop-js").click( () => {
      document.getElementById('modalCrop').classList.remove('active');
      console.log(cropper, 'CROPPER');
      cropBoxData = cropper.getCropBoxData();
      canvasData = cropper.getCanvasData();
      cropper.destroy();
      }
    );

    // Enable zoom in button
    $(".js-zoom-in").click(function () {
      cropper.zoom(0.1);
    });

    // Enable zoom out button
    $(".js-zoom-out").click(function () {
      cropper.zoom(-0.1);
    });

    // Enable move up button
    $(".js-pic-up").click(function () {
      cropper.move(0, 10);
    });

    // Enable move down button
    $(".js-pic-down").click(function () {
      cropper.move(0, -10);
    });

    /* SCRIPT TO COLLECT THE DATA AND POST TO THE SERVER */
    $(".js-crop-and-upload").click(function () {
        var cropData = cropper.getData();
        $("#id_x" + img_mode).val(cropData["x"]);
        $("#id_y" + img_mode).val(cropData["y"]);
        $("#id_height" + img_mode).val(cropData["height"]);
        $("#id_width" + img_mode).val(cropData["width"]);
        $("#formUpload" + img_mode).submit();
    });

  });

}

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

  class ModalOpenClose {
    constructor(data) {
      this.domNodes = data;
      this.domNodes.openModalBtn.addEventListener('click', () => {this.openModal()})
      this.domNodes.closeModalBtn.addEventListener('click', () => {this.closeModal()})
    }

    openModal() {
      this.domNodes.main.classList.add('active');
    }
    closeModal() {
      this.domNodes.main.classList.remove('active');
    }
  }

  // mobile refresh page

  if (window.innerWidth < 600) {

    document.body.insertAdjacentHTML('afterbegin', `
    <svg class="svg-reload" fill="var(--c10two)" clip-rule="evenodd" fill-rule="evenodd" stroke-linejoin="round" stroke-miterlimit="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="m11.998 2.001c5.517 0 9.997 4.48 9.997 9.997 0 5.518-4.48 9.998-9.997 9.998-5.518 0-9.998-4.48-9.998-9.998 0-5.517 4.48-9.997 9.998-9.997zm-4.496 6.028-.002-.825c0-.414-.336-.75-.75-.75s-.75.336-.75.75v3.048c0 .414.336.75.75.75h3.022c.414 0 .75-.336.75-.75s-.336-.756-.75-.756h-1.512c.808-1.205 2.182-1.998 3.74-1.998 2.483 0 4.5 2.016 4.5 4.5 0 2.483-2.017 4.5-4.5 4.5-1.956 0-3.623-1.251-4.242-2.997-.106-.299-.389-.499-.707-.499-.518 0-.88.513-.707 1.001.825 2.327 3.048 3.995 5.656 3.995 3.312 0 6-2.689 6-6 0-3.312-2.688-6-6-6-1.79 0-3.399.786-4.498 2.031z" fill-rule="nonzero"/>
    </svg>
    `)

    const refreshSvg = document.querySelector('.svg-reload');

    const TOUCHMOVE_PATH_LENGTH = 150;
    const MAX_Y_FROM_SCREEN_TOP= 75;
    const MAX_SVG_MOVE_PATH = 400;
    const SVG_SIZE = 50;

    document.addEventListener('touchstart', (evt) => {

      if (evt.touches[0].clientY > MAX_Y_FROM_SCREEN_TOP) return;

      let startY = evt.touches[0].clientY;
      let isRefreshAvailable = false;

      function touchMoveHandler(evt) {
        const currentY = evt.touches[0].clientY;
        let yDiff = currentY - startY;
        if (yDiff > TOUCHMOVE_PATH_LENGTH) {
          isRefreshAvailable = true;
          if (yDiff > MAX_SVG_MOVE_PATH) yDiff = MAX_SVG_MOVE_PATH;
          refreshSvg.style.transform = `translateY(${yDiff - TOUCHMOVE_PATH_LENGTH/2 - SVG_SIZE}rem) rotate(${yDiff - TOUCHMOVE_PATH_LENGTH}deg) scaleX(-1)`;
          refreshSvg.style.filter = 'grayscale(0)';
        } else {
          isRefreshAvailable = false;
          refreshSvg.style.transform = `translateY(${yDiff - TOUCHMOVE_PATH_LENGTH/2 - SVG_SIZE}rem) rotate(${yDiff - TOUCHMOVE_PATH_LENGTH}deg) scaleX(-1)`;
          refreshSvg.style.filter = 'grayscale(1)';
        }
      }

      function touchEndHandler(evt) {
        if (isRefreshAvailable) document.location.reload();
        else { refreshSvg.style.transform = `translateY(${-SVG_SIZE}rem) rotate(0deg) scaleX(-1)`;}
        document.removeEventListener('touchmove', touchMoveHandler)
        document.removeEventListener('touchend', touchEndHandler)
      }

      document.addEventListener('touchmove', touchMoveHandler);
      document.addEventListener('touchend', touchEndHandler);

    })

  }

/*! SelectWithImage */
class SelectWithImage {
  constructor(domElement) {
    this._selectWithImage = domElement;
    this._items = this._selectWithImage.querySelectorAll(".ct__selectWithImage-content div");
    this._selectedItem = this._selectWithImage.querySelector(".ct__selectWithImage-selected");
    if ( this._selectedItem !== null ){
        this.setEventListeners();
    }
  }

  setEventListeners() {
    this._items.forEach((item) => {
      // Добавляем обработчики событий для каждого элемента списка
      item.addEventListener("click", () => {
        // Получаем значение выбранного элемента и записываем его в выбранный элемент
        const value = item.getAttribute("data-value");
        this._selectedItem.querySelector("span").textContent = item.textContent;

        if ( item.querySelector("img") !== null ){
            this._selectedItem.querySelector("img").setAttribute("src", item.querySelector("img").getAttribute("src"));
            if ( this._selectedItem.querySelector("svg:not(.ct__selectWithImage-arrow)") !== null ){
                this._selectedItem.querySelector("svg:not(.ct__selectWithImage-arrow)").remove();
            }
            this._selectedItem.querySelector("img").style.display = 'block';
        }
        else{
            this._selectedItem.querySelector("img").style.display = 'none';
            if ( this._selectedItem.querySelector("svg:not(.ct__selectWithImage-arrow)") !== null ){
                this._selectedItem.querySelector("svg:not(.ct__selectWithImage-arrow)").remove();
            }
            var cloned_line = item.querySelector("svg").cloneNode(true);
            insertAfter(cloned_line, this._selectedItem.querySelector("img"));
        }

        this._selectedItem.setAttribute("data-value", value);

        // если выбор этого элемента должен что-то вызывать
        if ( item.getAttribute("data-func") !== null ){
            // Функция существует
            if (typeof window[item.getAttribute("data-func")] === 'function') {
                window[item.getAttribute("data-func")]();
            }
        }

        // Скрываем выпадающий список
        this._selectWithImage.classList.remove("active");
      });
    });

    // Добавляем обработчик события для открытия/закрытия выпадающего списка
    this._selectedItem.addEventListener("click", () => {
      this._selectWithImage.classList.toggle("active");
    });
  }
}

if (document.querySelector('.ct__selectWithImage')) {
  const drops = document.querySelectorAll('.ct__selectWithImage');
  drops.forEach((drop) => new SelectWithImage(drop));
}

var ajaxSettings;

function clear_modal_header() {
    $(".modal__ok").prop("onclick", null).off("click");
    $(".modal__cancel").prop("onclick", null).off("click");
}

var captcha_action = function() {
};

function captcha_answer(event){
    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&answer=" + parseInt(event.data.answer);

    $.ajax({
        type: "POST",
        url: "/answer_captcha/",
        data:  sending_data,
        cache: false,
        success: function(data){
            clear_modal_header();

            if (data.response == 'ok'){
                captcha_action();
            }
            else{
                display_modal('notify', data.header, data.response, null, data.grey_btn);
            }
        }
    });
}

function captcha_checking(data){
    clear_modal_header();

    $(".modal__ok").on( "click", {answer: data.white_btn}, captcha_answer);
    $(".modal__cancel").on( "click", {answer: data.grey_btn}, captcha_answer);

    display_modal('ask', data.header, data.text, data.white_btn, data.grey_btn)
}

function saveCssVariablesToLocalStorage() {
  const cssVariables = {
    '--c10one': getComputedStyle(document.documentElement).getPropertyValue('--c10one'),
    '--c10two': getComputedStyle(document.documentElement).getPropertyValue('--c10two'),
    '--c60': getComputedStyle(document.documentElement).getPropertyValue('--c60'),
    '--c30': getComputedStyle(document.documentElement).getPropertyValue('--c30'),
    '--nav': getComputedStyle(document.documentElement).getPropertyValue('--nav'),
  };

  localStorage.setItem('cssVariables', JSON.stringify(cssVariables));
}

saveCssVariablesToLocalStorage();




























