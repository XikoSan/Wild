// получаем прописку в этом регионе
function to_fly(){

    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&region=" + this.parentElement.getElementsByClassName("region_id")[0].value;

    $.ajax({
        beforeSend: function() {},
        type: "POST",
        url: "/map",
        data: sending_data,
        cache: false,
        success: function(result){
            if (result.response == 'ok'){
                location.reload();
            }
            else{
                display_modal('notify', result.header, result.response, null, result.grey_btn)
            }
        }
    });
};


function animateFlight(planeMarker, startCoords, endCoords, duration) {
  const latStep = (endCoords[0] - startCoords[0]) / duration;
  const lonStep = (endCoords[1] - startCoords[1]) / duration;

  let currentTime = 0;
  const fadeDuration = 3; // последние 2 секунды для плавного исчезновения

  const flightInterval = setInterval(() => {
    currentTime += 0.01;
    const newLat = startCoords[0] + latStep * currentTime;
    const newLon = startCoords[1] + lonStep * currentTime;

    planeMarker.setLatLng([newLat, newLon]);

    // Если осталось менее fadeDuration времени, начинаем уменьшать opacity
    if (currentTime >= duration - fadeDuration) {
      const opacity = (duration - currentTime) / fadeDuration; // от 1 до 0
      planeMarker.setOpacity(opacity);
    }

    // Завершаем анимацию и удаляем маркер
    if (currentTime >= duration) {
      clearInterval(flightInterval);
      planeMarker.remove();
    }
  }, 10);
}


function adjustStartCoords(startCoords, endCoords, duration, estimate) {
  const percentCompleted = estimate / duration;

  const latStep = (endCoords[0] - startCoords[0]) * percentCompleted;
  const lonStep = (endCoords[1] - startCoords[1]) * percentCompleted;

  const adjustedStartLat = startCoords[0] + latStep;
  const adjustedStartLon = startCoords[1] + lonStep;

  return [adjustedStartLat, adjustedStartLon];
}


function calculateAngle(startCoords, endCoords) {
  const deltaY = endCoords[1] - startCoords[1];
  const deltaX = endCoords[0] - startCoords[0];
  const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
  return angle;
}