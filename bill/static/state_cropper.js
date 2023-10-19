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
//    профиль
      if (document.querySelector('#formUpload')) {
        $("#formUpload").submit();
      }
//    новый законопроект
      else if(document.querySelector('#new_bill')){

        var croppedImageDataURL = cropper.getCroppedCanvas().toDataURL();
        var imgPreview = document.getElementById('img_preview');
        imgPreview.src = croppedImageDataURL;

        document.getElementById('modalCrop').classList.remove('active');
        cropBoxData = cropper.getCropBoxData();
        canvasData = cropper.getCanvasData();
        cropper.destroy();
      }
//    создание
      else{
        document.getElementById('modalCrop').classList.remove('active');
        cropBoxData = cropper.getCropBoxData();
        canvasData = cropper.getCanvasData();
        cropper.destroy();
      }
  });

  });
