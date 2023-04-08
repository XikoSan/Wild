/* common func */

function openModalByAddClass(selector) {
  document.querySelector(selector).classList.add('active')
}
function closeModalByRemoveClass(selector) {
  document.querySelector(selector).classList.remove('active')
}

function select_cropper() {
  if(curr_cropper == 1){
    return cropper1;
  }
  else{
    return cropper2;
  }
}


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

if (modalOk) modalOk.addEventListener('click', () => modal.classList.remove('active'));
if (modalCancel) modalCancel.addEventListener('click', () => modal.classList.remove('active'));

// Cropper
var curr_cropper;
var cropper1;
var cropper2;

function initCropper(fileInputId, imgId) {

  $(function () {

    var cropper;
    /* SCRIPT TO OPEN THE MODAL WITH THE PREVIEW */
      document.getElementById(fileInputId).addEventListener('change', function () {
      if (this.files && this.files[0]) {
        var reader = new FileReader();
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

          if(fileInputId == 'id_image' || fileInputId == 'id_image1'){
            curr_cropper = 1;
            cropper1 = cropper;
          }
          else{
            curr_cropper = 2;
            cropper2 = cropper;
          }

          console.log(cropper);
  
          //document.querySelector('.js-pic-up').click();
        }
        reader.readAsDataURL(this.files[0]);
      }
    });
  
    /* SCRIPTS TO HANDLE THE CROPPER BOX */
    var cropBoxData;
    var canvasData;

    $("#crop-close").click( function () {
      document.getElementById('modalCrop').classList.remove('active');
      var cropper = select_cropper();
      cropBoxData = cropper.getCropBoxData();
      canvasData = cropper.getCanvasData();
      cropper.destroy();
      }
    );
  
    $(".back-crop-js").click( function () {
      document.getElementById('modalCrop').classList.remove('active');
      var cropper = select_cropper();
      cropBoxData = cropper.getCropBoxData();
      canvasData = cropper.getCanvasData();
      cropper.destroy();
      }
    );
  
    // Enable zoom in button
    $(".js-zoom-in").click(function () {
        var cropper = select_cropper();
      cropper.zoom(0.1);
    });
  
    // Enable zoom out button
    $(".js-zoom-out").click(function () {
    var cropper = select_cropper();
      cropper.zoom(-0.1);
    });
  
    // Enable move up button
    $(".js-pic-up").click(function () {
    var cropper = select_cropper();
      cropper.move(0, 10);
    });
  
    // Enable move down button
    $(".js-pic-down").click(function () {
    var cropper = select_cropper();
      cropper.move(0, -10);
    });
  
    /* SCRIPT TO COLLECT THE DATA AND POST TO THE SERVER */
    $(".js-crop-and-upload").click(function () {
    var cropper = select_cropper();
        var cropData = cropper.getData();
        $("#id_x" + curr_cropper).val(cropData["x"]);
        $("#id_y" + curr_cropper).val(cropData["y"]);
        $("#id_height" + curr_cropper).val(cropData["height"]);
        $("#id_width" + curr_cropper).val(cropData["width"]);
        $("#formUpload" + curr_cropper).submit();
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
