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

// Cropper

$(function () {

  var cropper;

  /* SCRIPT TO OPEN THE MODAL WITH THE PREVIEW */
  $("#id_image").change(function () {
    if (this.files && this.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $("#image").attr("src", e.target.result);
        document.getElementById('modalCrop').classList.add('active');

        let image = document.getElementById('image');
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
  var cropBoxData;
  var canvasData;

  $("#crop-close").click( function () {
    document.getElementById('modalCrop').classList.remove('active');
    cropBoxData = cropper.getCropBoxData();
    canvasData = cropper.getCanvasData();
    cropper.destroy();
    }
  );

  $(".back-crop-js").click( function () {
    document.getElementById('modalCrop').classList.remove('active');
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
      $("#id_x").val(cropData["x"]);
      $("#id_y").val(cropData["y"]);
      $("#id_height").val(cropData["height"]);
      $("#id_width").val(cropData["width"]);
      $("#formUpload").submit();
  });

  });