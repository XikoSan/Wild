  for (let i = 0; i < 10; i++) {
    if (localStorage.getItem(i) == '{{ player.pk }}') {
      break;
    }
    if (localStorage.getItem(i) === null) {
      localStorage.setItem(i,'{{ player.pk }}');
      break;
    }
  }

  let list = '';

  for (let i = 0; i < 10; i++) {
    if (localStorage.getItem(i) === null) {
      break;
    }
    if(list === ''){
      list = localStorage.getItem(i);
    }
    else{
      list = list + ',' +localStorage.getItem(i);
    }
  }
  if(list.includes(',')){
    var sending_data = "&csrfmiddlewaretoken=" + csrftoken;
    sending_data += "&list=" + list;
    $.ajax({
        type: "POST",
        url: "/comma_list/",
        data:  sending_data,
        cache: false,
        success: function(data){
            if (data.response == 'ok'){
                localStorage.clear();
                location.reload();
            }
        }
    });
  }