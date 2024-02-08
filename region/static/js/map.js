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

  const flightInterval = setInterval(() => {
    currentTime += 0.1;
    const newLat = startCoords[0] + latStep * currentTime;
    const newLon = startCoords[1] + lonStep * currentTime;

    planeMarker.setLatLng([newLat, newLon]);

    if (currentTime + 0.1 >= duration) {
      clearInterval(flightInterval);
    }
  }, 100);
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