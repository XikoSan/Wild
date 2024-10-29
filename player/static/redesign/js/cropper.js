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
            viewMode: 1, // Установить режим просмотра внутри изображения
            autoCropArea: 1, // Автоматически обрезать всю доступную область изображения
            ready: function () {
              cropper.crop(); // Применить первоначальное обрезание
            }
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

        var formData = new FormData($("#formUpload")[0]);

        $.ajax({
            url: '/avatar_edit/',  // Адрес представления для редактирования аватара
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (data) {
                if (data.response == 'ok'){
                    location.reload();
                }
                else{
                    display_modal('notify', data.header, data.response, null, data.grey_btn);
                }
            }
        });

    });

  });
